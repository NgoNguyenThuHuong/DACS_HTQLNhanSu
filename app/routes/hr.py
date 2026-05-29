from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from app.models import Employee, Department, Candidate, Attendance, LeaveRequest, ExamResult, JobPost, Exam, Task
from app.extensions import db
from app.core.exceptions import ValidationError, BusinessException, EntityNotFoundException

from app.services import HRService, AnalyticsService
from app.repositories import (
    EmployeeRepository,
    DepartmentRepository,
    LeaveRepository,
    TaskRepository,
    RecruitmentRepository,
    AnalyticsRepository
)

from datetime import datetime, timedelta
import csv
from io import StringIO

hr = Blueprint('hr', __name__)
hr_service = HRService()
analytics_service = AnalyticsService()

@hr.route('/dashboard')
@login_required
def dashboard():
    """Simple HR dashboard placeholder for testing."""
    return "HR Dashboard", 200

# Repositories for read operations (Queries)
employee_repo = EmployeeRepository()
department_repo = DepartmentRepository()
leave_repo = LeaveRepository()
task_repo = TaskRepository()
recruitment_repo = RecruitmentRepository()
analytics_repo = AnalyticsRepository()

# ─── NHÂN SỰ ──────────────────────────────────────────────────────────────────

@hr.route('/accounts')
@login_required
def manage_accounts():
    if current_user.role != 'Admin':
        flash("Bạn không có quyền truy cập trang này.", "error")
        return redirect(url_for('main.index'))
    
    employees = employee_repo.get_all()
    return render_template('modules/admin/accounts.html', employees=employees)

@hr.route('/employees', methods=['GET', 'POST'])
@login_required
def employees_list():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        try:
            fullname = request.form.get('fullname')
            hr_service.create_employee(request.form)
            flash(f'Đã thêm nhân viên {fullname} thành công!', 'success')
        except (ValidationError, BusinessException) as e:
            flash(e.message, 'danger')
        return redirect(url_for('hr.employees_list'))

    employees = employee_repo.get_all_with_departments()
    departments = department_repo.get_all()
    return render_template('modules/employees/list.html', employees=employees, departments=departments)

@hr.route('/employees/reset_password/<int:emp_id>', methods=['POST'])
@login_required
def reset_password(emp_id):
    if current_user.role != 'Admin':
        return "Unauthorized", 403
    
    try:
        emp = hr_service.reset_password(emp_id)
        flash(f'Đã reset mật khẩu cho {emp.fullname} về "123456".', 'success')
    except EntityNotFoundException as e:
        flash(e.message, 'danger')
        
    return redirect(url_for('hr.employees_list'))

@hr.route('/employees/permissions/<int:emp_id>')
@login_required
def user_permissions(emp_id):
    if current_user.role != 'Admin':
        return "Unauthorized", 403
    
    try:
        perms_data = hr_service.get_user_permissions(emp_id)
        return render_template('modules/admin/user_permissions.html', 
                               user=perms_data['employee'], 
                               all_perms=perms_data['all_perms'], 
                               user_perms=perms_data['user_perms'])
    except EntityNotFoundException as e:
        flash(e.message, 'danger')
        return redirect(url_for('hr.employees_list'))

@hr.route('/employees/permissions/update', methods=['POST'])
@login_required
def update_user_permission():
    if current_user.role != 'Admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.form
    user_id = data.get('user_id', type=int)
    perm_key = data.get('permission')
    value = data.get('value') == 'true'
    
    try:
        hr_service.update_user_permission(user_id, perm_key, value)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@hr.route('/departments', methods=['GET', 'POST'])
@login_required
def departments_list():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        try:
            name = request.form.get('name', '')
            desc = request.form.get('description', '')
            hr_service.create_department(name, desc)
            flash(f'Đã thêm phòng ban {name}!', 'success')
        except ValidationError as e:
            flash(e.message, 'danger')
        return redirect(url_for('hr.departments_list'))

    departments = department_repo.get_all()
    return render_template('modules/employees/departments.html', departments=departments)

# ─── CHẤM CÔNG / NGHỈ PHÉP ───────────────────────────────────────────────────

@hr.route('/attendance/logs')
@login_required
def attendance_logs():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search = request.args.get('search', '').strip()

    query = db.session.query(Attendance).join(Employee)
    if start_date:
        query = query.filter(Attendance.work_date >= start_date)
    if end_date:
        query = query.filter(Attendance.work_date <= end_date)
    if search:
        query = query.filter(
            (Employee.fullname.ilike(f'%{search}%')) |
            (Employee.employee_code.ilike(f'%{search}%'))
        )
    logs = query.order_by(Attendance.work_date.desc(), Attendance.check_in.desc()).all()
    
    return render_template('modules/attendance/logs.html', 
                           logs=logs, 
                           now=datetime.now(),
                           start_date=start_date,
                           end_date=end_date,
                           search=search)

@hr.route('/leave/manage', methods=['GET', 'POST'])
@login_required
def manage_leave():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        req_id = request.args.get('req_id')
        action = request.form.get('action')
        try:
            hr_service.approve_or_reject_leave(req_id, action)
            flash('Yêu cầu đã được xử lý thành công.', 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('hr.manage_leave'))

    requests = leave_repo.get_pending_requests()
    return render_template('modules/hr/manage_leave.html', requests=requests)

# ─── TUYỂN DỤNG ───────────────────────────────────────────────────────────────

@hr.route('/recruitment/manage')
@login_required
def recruitment_index():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    status_filter = request.args.get('status', '')
    search = request.args.get('search', '').strip()
    min_score = request.args.get('min_score', type=float)
    max_score = request.args.get('max_score', type=float)

    candidates = recruitment_repo.get_candidates_filtered(status_filter, search)

    if min_score is not None or max_score is not None:
        filtered = []
        for c in candidates:
            latest = c.results[-1] if c.results else None
            s = latest.score if latest else 0
            if min_score is not None and s < min_score:
                continue
            if max_score is not None and s > max_score:
                continue
            filtered.append(c)
        candidates = filtered

    stats = recruitment_repo.get_candidates_stats()

    return render_template('modules/recruitment/manage.html',
                           candidates=candidates, stats=stats,
                           status_filter=status_filter, search=search,
                           min_score=min_score, max_score=max_score)

@hr.route('/candidate/<int:can_id>', methods=['GET', 'POST'])
@login_required
def candidate_detail(can_id):
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        result_id = request.form.get('result_id', type=int)
        feedback = request.form.get('hr_feedback', '').strip()
        try:
            hr_service.save_exam_feedback(result_id, feedback)
            flash('Đã lưu nhận xét thành công.', 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('hr.candidate_detail', can_id=can_id))

    candidate = recruitment_repo.get_candidate_by_id(can_id)
    if not candidate:
        flash("Không tìm thấy ứng viên.", "danger")
        return redirect(url_for('hr.recruitment_index'))
        
    results = recruitment_repo.get_results_by_candidate(can_id)
    return render_template('modules/recruitment/candidate_detail.html',
                           candidate=candidate, results=results)

@hr.route('/candidate/<int:can_id>/decide', methods=['POST'])
@login_required
def decide_candidate(can_id):
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    decision = request.form.get('decision')
    notes = request.form.get('notes', '').strip()

    try:
        hr_service.decide_candidate(can_id, decision, notes, current_user.id)
        flash(f'Đã {"DUYỆT" if decision == "Passed" else "TỪ CHỐI"} và gửi email thông báo thành công.', 'success')
    except Exception as e:
        flash(f'Lỗi xử lý: {str(e)}', 'warning')

    return redirect(url_for('hr.candidate_detail', can_id=can_id))

@hr.route('/recruitment/export')
@login_required
def export_candidates():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    candidates = recruitment_repo.get_all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Ho Ten', 'Email', 'SDT', 'Vi tri', 'Trang thai', 'Diem thi', 'Ngay nop'])
    
    for c in candidates:
        latest_res = c.results[-1] if c.results else None
        score = latest_res.score if latest_res else 'N/A'
        job_title = c.job.title if c.job else 'N/A'
        cw.writerow([c.id, c.fullname, c.email, c.phone, job_title, c.status, score, c.created_at.strftime('%Y-%m-%d')])
    
    output = si.getvalue()
    response = make_response(output)
    response.headers["Content-Disposition"] = "attachment; filename=candidates_export.csv"
    response.headers["Content-type"] = "text/csv"
    return response

@hr.route('/score_exam/<int:result_id>', methods=['POST'])
@login_required
def score_exam(result_id):
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    feedback = request.form.get('hr_feedback', '')
    try:
        hr_service.save_exam_feedback(result_id, feedback)
        flash('Đã lưu nhận xét cho bài thi.', 'success')
        result = recruitment_repo.get_result_by_id(result_id)
        return redirect(url_for('hr.candidate_detail', can_id=result.candidate_id))
    except Exception as e:
        flash(str(e), 'danger')
        return redirect(url_for('hr.recruitment_index'))

# ─── QUẢN LÝ TIN TUYỂN DỤNG ──────────────────────────────────────────────────

@hr.route('/recruitment/jobs', methods=['GET', 'POST'])
@login_required
def manage_jobs():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        action = request.form.get('action')
        job_id = request.form.get('job_id', type=int)
        try:
            hr_service.manage_jobs(action, job_id, request.form)
            flash('Đã xử lý thông tin tin tuyển dụng.', 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('hr.manage_jobs'))

    jobs = recruitment_repo.get_all_jobs()
    return render_template('modules/recruitment/manage_jobs.html', jobs=jobs)

# ─── QUẢN LÝ BÀI THI & CÂU HỎI ────────────────────────────────────────────────

@hr.route('/recruitment/exams', methods=['GET', 'POST'])
@login_required
def manage_exams():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        action = request.form.get('action')
        exam_id = request.form.get('exam_id', type=int)
        try:
            exam = hr_service.manage_exams(action, exam_id, request.form)
            if action == 'add' and exam:
                flash(f'Đã tạo bài thi: {exam.title}', 'success')
                return redirect(url_for('hr.edit_exam', exam_id=exam.id))
            flash('Đã cập nhật bài thi thành công.', 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('hr.manage_exams'))

    exams = recruitment_repo.get_all_exams()
    return render_template('modules/recruitment/manage_exams.html', exams=exams)

@hr.route('/recruitment/exams/edit/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def edit_exam(exam_id):
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        action = request.form.get('action')
        try:
            hr_service.edit_exam(exam_id, action, request.form)
            flash('Cập nhật thông tin bài thi/câu hỏi thành công.', 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('hr.edit_exam', exam_id=exam_id))

    exam = recruitment_repo.get_exam_by_id(exam_id)
    if not exam:
        flash("Không tìm thấy bài thi.", "danger")
        return redirect(url_for('hr.manage_exams'))
    return render_template('modules/recruitment/edit_exam.html', exam=exam)

# ─── BÁO CÁO ─────────────────────────────────────────────────────────────────

@hr.route('/reports')
@login_required
def reports_index():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403
        
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    metrics = analytics_repo.get_system_dashboard_metrics(thirty_days_ago)
    depts = analytics_repo.get_department_distribution()
    attendance_trend = analytics_service.get_weekly_attendance_trend()
    
    stats = recruitment_repo.get_candidates_stats()
    recruitment_data = [stats['total'], stats['passed'], stats['failed']]
    
    radar_data = analytics_service.get_system_radar_data()
    recent_activities = analytics_service.get_recent_activities()

    return render_template('modules/reports/index.html',
                           attendance_rate=metrics['attendance_rate'],
                           avg_leave=metrics['avg_leave'],
                           new_emps=metrics['new_emps'],
                           avg_score=metrics['avg_score'],
                           dept_labels=depts['labels'],
                           dept_counts=depts['counts'],
                           attendance_trend=attendance_trend,
                           recruitment_data=recruitment_data,
                           radar_data=radar_data,
                           recent_activities=recent_activities)

# ─── QUẢN LÝ NHIỆM VỤ ──────────────────────────────────────────────────────────

@hr.route('/tasks/manage', methods=['GET', 'POST'])
@login_required
def manage_tasks():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        action = request.form.get('action')
        task_id = request.form.get('task_id', type=int)
        try:
            hr_service.manage_tasks(action, task_id, request.form)
            flash('Đã xử lý thông tin nhiệm vụ thành công.', 'success')
        except Exception as e:
            flash(str(e), 'danger')
        return redirect(url_for('hr.manage_tasks'))

    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    category_filter = request.args.get('category', '')
    
    tasks = task_repo.get_tasks_filtered(search, status_filter, priority_filter, category_filter)
    employees = employee_repo.get_all()
    categories = task_repo.get_distinct_categories()
    
    return render_template('modules/hr/manage_tasks.html', 
                           tasks=tasks, 
                           employees=employees,
                           categories=categories,
                           now=datetime.now(),
                           search=search,
                           status_filter=status_filter,
                           priority_filter=priority_filter,
                           category_filter=category_filter)
