from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Employee, Department, Candidate, Attendance, LeaveRequest, ExamResult, CandidateAnswer, JobPost, Exam, ExamQuestion, RolePermission, UserPermission, Task
from email_service import send_passed_email, send_failed_email
from datetime import datetime

hr = Blueprint('hr', __name__)

# ─── NHÂN SỰ ──────────────────────────────────────────────────────────────────

@hr.route('/accounts')
@login_required
def manage_accounts():
    if current_user.role != 'Admin':
        flash("Bạn không có quyền truy cập trang này.", "error")
        return redirect(url_for('main.index'))
    
    employees = Employee.query.all()
    return render_template('modules/admin/accounts.html', employees=employees)

@hr.route('/employees', methods=['GET', 'POST'])
@login_required
def employees_list():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        employee_code = request.form.get('employee_code')
        fullname      = request.form.get('fullname')
        username      = request.form.get('username')
        password      = request.form.get('password')
        email         = request.form.get('email')
        department_id = request.form.get('department_id')
        role          = request.form.get('role')

        new_emp = Employee(
            employee_code=employee_code,
            fullname=fullname,
            username=username,
            password=password,
            email=email,
            department_id=department_id,
            role=role
        )
        db.session.add(new_emp)
        db.session.commit()
        flash(f'Đã thêm nhân viên {fullname} thành công!', 'success')
        return redirect(url_for('hr.employees_list'))

    employees   = Employee.query.all()
    departments = Department.query.all()
    return render_template('modules/employees/list.html', employees=employees, departments=departments)

@hr.route('/employees/reset_password/<int:emp_id>', methods=['POST'])
@login_required
def reset_password(emp_id):
    if current_user.role != 'Admin':
        return "Unauthorized", 403
    
    emp = Employee.query.get_or_404(emp_id)
    emp.password = '123456'  # Mật khẩu mặc định
    db.session.commit()
    flash(f'Đã reset mật khẩu cho {emp.fullname} về "123456".', 'success')
    return redirect(url_for('hr.employees_list'))

@hr.route('/employees/permissions/<int:emp_id>')
@login_required
def user_permissions(emp_id):
    if current_user.role != 'Admin':
        return "Unauthorized", 403
    
    emp = Employee.query.get_or_404(emp_id)
    
    # Lấy danh sách tất cả các quyền (từ RolePermission hoặc cứng trong mã)
    all_perms = db.session.query(RolePermission.permission_key).distinct().all()
    all_perms = [p[0] for p in all_perms]
    
    # Nếu chưa có cấu hình perm nào, lấy mặc định cho demo
    if not all_perms:
        all_perms = ['VIEW_REPORTS', 'MANAGE_EMPLOYEES', 'APPROVE_LEAVE', 'MANAGE_RECRUITMENT']
    
    user_perms = {}
    for perm in all_perms:
        # Kiểm tra ghi đè
        override = UserPermission.query.filter_by(user_id=emp_id, permission_key=perm).first()
        if override:
            user_perms[perm] = override.is_allowed
        else:
            # Mặc định theo Role
            role_p = RolePermission.query.filter_by(role_name=emp.role, permission_key=perm).first()
            user_perms[perm] = role_p.is_allowed if role_p else False
            
    return render_template('modules/admin/user_permissions.html', user=emp, all_perms=all_perms, user_perms=user_perms)

@hr.route('/employees/permissions/update', methods=['POST'])
@login_required
def update_user_permission():
    if current_user.role != 'Admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.form
    user_id = data.get('user_id', type=int)
    perm_key = data.get('permission')
    value = data.get('value') == 'true'
    
    override = UserPermission.query.filter_by(user_id=user_id, permission_key=perm_key).first()
    if override:
        override.is_allowed = value
    else:
        new_override = UserPermission(user_id=user_id, permission_key=perm_key, is_allowed=value)
        db.session.add(new_override)
    
    db.session.commit()
    return jsonify({'success': True})

@hr.route('/departments', methods=['GET', 'POST'])
@login_required
def departments_list():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        name        = request.form.get('name')
        description = request.form.get('description')
        new_dept    = Department(name=name, description=description)
        db.session.add(new_dept)
        db.session.commit()
        flash(f'Đã thêm phòng ban {name}!', 'success')
        return redirect(url_for('hr.departments_list'))

    departments = Department.query.all()
    return render_template('modules/employees/departments.html', departments=departments)

# ─── CHẤM CÔNG / NGHỈ PHÉP ───────────────────────────────────────────────────

@hr.route('/attendance/logs')
@login_required
def attendance_logs():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    # Lấy các tham số lọc
    start_date = request.args.get('start_date')
    end_date   = request.args.get('end_date')
    search     = request.args.get('search', '').strip()

    query = Attendance.query.join(Employee)

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
        req_id   = request.args.get('req_id')
        action   = request.form.get('action')
        leave_req = LeaveRequest.query.get_or_404(req_id)

        if action == 'approve':
            leave_req.status = 'Approved'
            diff = (leave_req.end_date - leave_req.start_date).days + 1
            leave_req.employee.leave_days_used += diff
        elif action == 'reject':
            leave_req.status = 'Rejected'

        db.session.commit()
        flash(f'Yêu cầu của {leave_req.employee.fullname} đã được xử lý.', 'success')
        return redirect(url_for('hr.manage_leave'))

    requests = LeaveRequest.query.filter_by(status='Pending').all()
    return render_template('modules/hr/manage_leave.html', requests=requests)

# ─── TUYỂN DỤNG ───────────────────────────────────────────────────────────────

@hr.route('/recruitment/manage')
@login_required
def recruitment_index():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    # Bộ lọc
    status_filter = request.args.get('status', '')
    search        = request.args.get('search', '').strip()
    min_score     = request.args.get('min_score', type=float)
    max_score     = request.args.get('max_score', type=float)

    query = Candidate.query

    if status_filter:
        query = query.filter(Candidate.status == status_filter)
    if search:
        query = query.filter(
            (Candidate.fullname.ilike(f'%{search}%')) |
            (Candidate.email.ilike(f'%{search}%'))
        )

    candidates = query.order_by(Candidate.created_at.desc()).all()

    # Lọc theo điểm (lấy điểm từ kết quả thi)
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

    # Thống kê
    all_candidates = Candidate.query.all()
    stats = {
        'total':   len(all_candidates),
        'applied': sum(1 for c in all_candidates if c.status == 'Applied'),
        'testing': sum(1 for c in all_candidates if c.status == 'Testing'),
        'passed':  sum(1 for c in all_candidates if c.status == 'Passed'),
        'failed':  sum(1 for c in all_candidates if c.status == 'Failed'),
        'job_labels': [j.title for j in JobPost.query.all()],
        'job_counts': [len(j.candidates) for j in JobPost.query.all()]
    }

    return render_template('modules/recruitment/manage.html',
                           candidates=candidates, stats=stats,
                           status_filter=status_filter, search=search,
                           min_score=min_score, max_score=max_score)

@hr.route('/candidate/<int:can_id>', methods=['GET', 'POST'])
@login_required
def candidate_detail(can_id):
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    candidate = Candidate.query.get_or_404(can_id)

    # Lưu nhận xét HR cho câu tự luận
    if request.method == 'POST':
        result_id = request.form.get('result_id', type=int)
        feedback  = request.form.get('hr_feedback', '').strip()
        if result_id:
            result = ExamResult.query.get(result_id)
            if result:
                result.hr_feedback = feedback
                result.status      = 'Completed'
                db.session.commit()
                flash('Đã lưu nhận xét thành công.', 'success')
        return redirect(url_for('hr.candidate_detail', can_id=can_id))

    results = ExamResult.query.filter_by(candidate_id=can_id).all()
    return render_template('modules/recruitment/candidate_detail.html',
                           candidate=candidate, results=results)

@hr.route('/candidate/<int:can_id>/decide', methods=['POST'])
@login_required
def decide_candidate(can_id):
    """Duyệt (Đậu) hoặc Từ chối (Rớt) ứng viên — gửi email tự động."""
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    candidate = Candidate.query.get_or_404(can_id)
    decision  = request.form.get('decision')  # 'Passed' hoặc 'Failed'
    notes     = request.form.get('notes', '').strip()

    if decision not in ('Passed', 'Failed'):
        flash('Quyết định không hợp lệ.', 'danger')
        return redirect(url_for('hr.candidate_detail', can_id=can_id))

    candidate.status      = decision
    candidate.notes       = notes
    candidate.reviewed_at = datetime.utcnow()
    candidate.reviewed_by = current_user.id

    # Lấy điểm thi mới nhất
    latest_result = candidate.results[-1] if candidate.results else None
    score = latest_result.score if latest_result else 0
    job_title = candidate.job.title if candidate.job else 'Chưa xác định'

    # Gửi email
    if not candidate.email_sent:
        if decision == 'Passed':
            ok = send_passed_email(candidate.fullname, candidate.email, job_title, score)
        else:
            ok = send_failed_email(candidate.fullname, candidate.email, job_title, score)

        if ok:
            candidate.email_sent = True
            flash(f'Đã {"DUYỆT" if decision == "Passed" else "TỪ CHỐI"} và gửi email thông báo cho {candidate.fullname}.', 'success')
        else:
            flash(f'Đã cập nhật trạng thái nhưng GỬI EMAIL THẤT BẠI. Kiểm tra lại cấu hình SMTP.', 'warning')
    else:
        flash(f'Đã cập nhật trạng thái. (Email đã gửi trước đó)', 'info')

    db.session.commit()
    return redirect(url_for('hr.candidate_detail', can_id=can_id))

@hr.route('/recruitment/export')
@login_required
def export_candidates():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    import csv
    from io import StringIO
    from flask import make_response

    candidates = Candidate.query.all()
    
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

    result   = ExamResult.query.get_or_404(result_id)
    feedback = request.form.get('hr_feedback', '')

    result.hr_feedback = feedback
    result.status      = 'Completed'
    db.session.commit()
    flash('Đã lưu nhận xét cho bài thi.', 'success')
    return redirect(url_for('hr.candidate_detail', can_id=result.candidate_id))

# ─── QUẢN LÝ TIN TUYỂN DỤNG ──────────────────────────────────────────────────

@hr.route('/recruitment/jobs', methods=['GET', 'POST'])
@login_required
def manage_jobs():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        action = request.form.get('action')
        job_id = request.form.get('job_id', type=int)

        if action == 'add':
            title        = request.form.get('title')
            description  = request.form.get('description')
            requirements = request.form.get('requirements')
            new_job = JobPost(title=title, description=description, requirements=requirements)
            db.session.add(new_job)
            db.session.commit()
            flash(f'Đã thêm tin tuyển dụng: {title}', 'success')
        
        elif action == 'edit' and job_id:
            job = JobPost.query.get(job_id)
            if job:
                job.title        = request.form.get('title')
                job.description  = request.form.get('description')
                job.requirements = request.form.get('requirements')
                db.session.commit()
                flash('Đã cập nhật tin tuyển dụng.', 'success')
        
        elif action == 'toggle_status' and job_id:
            job = JobPost.query.get(job_id)
            if job:
                job.status = 'Closed' if job.status == 'Open' else 'Open'
                db.session.commit()
                flash(f'Đã chuyển trạng thái sang: {job.status}', 'info')
        
        return redirect(url_for('hr.manage_jobs'))

    jobs = JobPost.query.order_by(JobPost.created_at.desc()).all()
    return render_template('modules/recruitment/manage_jobs.html', jobs=jobs)

# ─── QUẢN LÝ BÀI THI & CÂU HỎI ────────────────────────────────────────────────

@hr.route('/recruitment/exams', methods=['GET', 'POST'])
@login_required
def manage_exams():
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    if request.method == 'POST':
        action  = request.form.get('action')
        exam_id = request.form.get('exam_id', type=int)

        if action == 'add':
            title            = request.form.get('title')
            duration         = request.form.get('duration_minutes', type=int, default=30)
            pass_threshold   = request.form.get('pass_threshold', type=float, default=7.0)
            new_exam = Exam(title=title, duration_minutes=duration, pass_threshold=pass_threshold)
            db.session.add(new_exam)
            db.session.commit()
            flash(f'Đã tạo bài thi: {title}', 'success')
            return redirect(url_for('hr.edit_exam', exam_id=new_exam.id))
        
        elif action == 'delete' and exam_id:
            exam = Exam.query.get(exam_id)
            if exam:
                db.session.delete(exam)
                db.session.commit()
                flash('Đã xóa bài thi.', 'warning')
        
        return redirect(url_for('hr.manage_exams'))

    exams = Exam.query.all()
    return render_template('modules/recruitment/manage_exams.html', exams=exams)

@hr.route('/recruitment/exams/edit/<int:exam_id>', methods=['GET', 'POST'])
@login_required
def edit_exam(exam_id):
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403

    exam = Exam.query.get_or_404(exam_id)

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_exam':
            exam.title            = request.form.get('title')
            exam.duration_minutes = request.form.get('duration_minutes', type=int)
            exam.pass_threshold   = request.form.get('pass_threshold', type=float)
            db.session.commit()
            flash('Cập nhật thông tin bài thi thành công.', 'success')
        
        elif action == 'add_question':
            q_text = request.form.get('question_text')
            q_type = request.form.get('question_type', 'MCQ')
            new_q = ExamQuestion(
                exam_id=exam_id,
                question_text=q_text,
                question_type=q_type,
                order_num=len(exam.questions) + 1
            )
            if q_type == 'MCQ':
                new_q.option_a = request.form.get('option_a')
                new_q.option_b = request.form.get('option_b')
                new_q.option_c = request.form.get('option_c')
                new_q.option_d = request.form.get('option_d')
                new_q.correct_option = request.form.get('correct_option', '').upper()
            
            db.session.add(new_q)
            db.session.commit()
            flash('Đã thêm câu hỏi mới.', 'success')

        elif action == 'delete_question':
            q_id = request.form.get('question_id', type=int)
            q = ExamQuestion.query.get(q_id)
            if q:
                db.session.delete(q)
                db.session.commit()
                flash('Đã xóa câu hỏi.', 'info')

        return redirect(url_for('hr.edit_exam', exam_id=exam_id))

    return render_template('modules/recruitment/edit_exam.html', exam=exam)

# ─── BÁO CÁO ─────────────────────────────────────────────────────────────────

@hr.route('/reports')
@login_required
def reports_index():
    from analytics import get_attendance_trend, get_radar_data
    if current_user.role not in ['Admin', 'HR']:
        return "Unauthorized", 403
        
    # 1. Tỷ lệ chuyên cần thực tế
    total_emp = Employee.query.count()
    attendance_count = Attendance.query.filter_by(work_date=datetime.now().date()).count()
    attendance_rate = round((attendance_count / total_emp * 100), 1) if total_emp > 0 else 0
    
    # 2. Nghỉ phép trung bình
    avg_leave = db.session.query(db.func.avg(Employee.leave_days_used)).scalar() or 0
    avg_leave = round(avg_leave, 1)

    # 3. Nhân viên mới (trong 30 ngày qua)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_emps = Employee.query.filter(Employee.created_at >= thirty_days_ago).count()

    # 4. Điểm thi trung bình (Recruitment)
    avg_score = db.session.query(db.func.avg(ExamResult.mcq_score)).scalar() or 0
    avg_score = round(avg_score, 1)

    # 5. Phân bổ theo phòng ban
    depts = Department.query.all()
    dept_labels = [d.name for d in depts]
    dept_counts = [len(d.employees) for d in depts]
    
    # 6. Xu hướng 7 ngày
    attendance_trend = get_attendance_trend(7)
    
    # 7. Tuyển dụng thực tế cho funnel
    total_candidates = Candidate.query.count()
    passed_candidates = Candidate.query.filter_by(status='Passed').count()
    failed_candidates = Candidate.query.filter_by(status='Failed').count()
    recruitment_data = [total_candidates, passed_candidates, failed_candidates]
    
    # 8. Radar
    radar_data = get_radar_data()
    
    # 9. Recent Activities
    from analytics import get_recent_activity
    recent_activities = get_recent_activity(10)

    return render_template('modules/reports/index.html',
                           attendance_rate=attendance_rate,
                           avg_leave=avg_leave,
                           new_emps=new_emps,
                           avg_score=avg_score,
                           dept_labels=dept_labels,
                           dept_counts=dept_counts,
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
        
        if action == 'add':
            employee_id = request.form.get('employee_id', type=int)
            title       = request.form.get('title')
            description = request.form.get('description')
            category    = request.form.get('category', 'Chung')
            due_date_str = request.form.get('due_date')
            priority    = request.form.get('priority', 'Medium')
            
            due_date = None
            if due_date_str:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            
            new_task = Task(
                employee_id=employee_id,
                title=title,
                description=description,
                category=category,
                due_date=due_date,
                priority=priority
            )
            db.session.add(new_task)
            db.session.commit()
            flash(f'Đã giao nhiệm vụ thành công!', 'success')

        elif action == 'edit':
            task_id = request.form.get('task_id', type=int)
            task = Task.query.get(task_id)
            if task:
                task.title = request.form.get('title')
                task.description = request.form.get('description')
                task.category = request.form.get('category')
                task.priority = request.form.get('priority')
                task.status = request.form.get('status')
                
                due_date_str = request.form.get('due_date')
                if due_date_str:
                    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                
                db.session.commit()
                flash('Đã cập nhật thông tin nhiệm vụ.', 'success')
            
        elif action == 'delete':
            task_id = request.form.get('task_id', type=int)
            task = Task.query.get(task_id)
            if task:
                db.session.delete(task)
                db.session.commit()
                flash('Đã xóa nhiệm vụ.', 'info')
                
        return redirect(url_for('hr.manage_tasks'))

    # Lọc và Tìm kiếm
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    category_filter = request.args.get('category', '')
    
    query = Task.query.join(Employee)
    if search:
        query = query.filter((Employee.fullname.ilike(f'%{search}%')) | (Task.title.ilike(f'%{search}%')))
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
    if category_filter:
        query = query.filter(Task.category == category_filter)
        
    tasks = query.order_by(Task.created_at.desc()).all()
    employees = Employee.query.all()
    categories = db.session.query(Task.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('modules/hr/manage_tasks.html', 
                           tasks=tasks, 
                           employees=employees,
                           categories=categories,
                           now=datetime.now(),
                           search=search,
                           status_filter=status_filter,
                           priority_filter=priority_filter,
                           category_filter=category_filter)
