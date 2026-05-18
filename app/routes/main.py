import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Employee, Department, Attendance, LeaveRequest, Task
from app.extensions import db
from app.services import AnalyticsService, EmployeeService
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    if current_user.role == 'Admin':
        return admin_dashboard()
    elif current_user.role == 'HR':
        return hr_dashboard()
    else:
        return employee_dashboard()

def admin_dashboard():
    analytics_service = AnalyticsService()
    
    total_employees = db.session.query(Employee).count()
    total_departments = db.session.query(Department).count()
    today = datetime.now().date()
    present_today = db.session.query(Attendance).filter(Attendance.work_date == today).count()
    pending_leave = db.session.query(LeaveRequest).filter(LeaveRequest.status == 'Pending').count()
    
    attendance_rate = round((present_today / total_employees * 100), 1) if total_employees > 0 else 0
    
    departments = db.session.query(Department).all()
    dept_labels = [d.name for d in departments]
    dept_counts = [len(d.employees) for d in departments]
    
    ai_risks = analytics_service.get_turnover_risk_ai_dashboard()
    radar_data = analytics_service.get_system_radar_data()
    attendance_trend = analytics_service.get_weekly_attendance_trend()
    recent_activities = analytics_service.get_recent_activities()[:8]
    
    return render_template('index_admin.html', 
                           total_employees=total_employees,
                           total_departments=total_departments,
                           present_today=present_today,
                           pending_leave=pending_leave,
                           attendance_rate=attendance_rate,
                           dept_labels=dept_labels,
                           dept_counts=dept_counts,
                           ai_risks=ai_risks,
                           radar_data=radar_data,
                           attendance_trend=attendance_trend,
                           recent_activities=recent_activities)

def hr_dashboard():
    analytics_service = AnalyticsService()
    
    total_employees = db.session.query(Employee).count()
    today = datetime.now().date()
    present_today = db.session.query(Attendance).filter(Attendance.work_date == today).count()
    pending_leave_reqs = db.session.query(LeaveRequest).filter(LeaveRequest.status == 'Pending').all()
    
    ai_risks = analytics_service.get_turnover_risk_ai_dashboard()
    recent_activities = analytics_service.get_recent_activities()
    radar_data = analytics_service.get_system_radar_data()
    
    return render_template('index_hr.html', 
                           total_employees=total_employees,
                           present_today=present_today,
                           ai_risks=ai_risks,
                           pending_leave=pending_leave_reqs,
                           recent_activities=recent_activities,
                           radar_data=radar_data)

def employee_dashboard():
    analytics_service = AnalyticsService()
    
    today = datetime.now().date()
    today_att = db.session.query(Attendance).filter(Attendance.employee_id == current_user.id, Attendance.work_date == today).first()
    tasks = db.session.query(Task).filter(Task.employee_id == current_user.id, Task.status == 'Pending').order_by(Task.due_date.asc()).limit(5).all()
    
    perf = analytics_service.get_individual_performance_metrics(current_user.id)
    radar_data = analytics_service.get_individual_radar_data(current_user.id)
    
    return render_template('index_employee.html', 
                           today_att=today_att,
                           tasks=tasks,
                           perf=perf,
                           radar_data=radar_data,
                           today_str=today.strftime('%d/%m/%Y'))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'Không tìm thấy file'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400
    
    try:
        employee_service = EmployeeService()
        new_filename = employee_service.update_avatar(current_user.id, file, upload_path='static/uploads/avatars')
        return jsonify({
            'success': True, 
            'message': 'Cập nhật ảnh đại diện thành công!',
            'avatar_url': f'/static/uploads/avatars/{new_filename}'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
