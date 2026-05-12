import os
import uuid
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Employee, Department, Attendance, LeaveRequest, Task
from analytics import get_turnover_risk_ai, get_individual_performance, get_radar_data
from datetime import datetime
from werkzeug.utils import secure_filename

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
    from analytics import get_turnover_risk_ai, get_radar_data, get_attendance_trend, get_recent_activity
    
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    today = datetime.now().date()
    present_today = Attendance.query.filter_by(work_date=today).count()
    pending_leave = LeaveRequest.query.filter_by(status='Pending').count()
    
    # Attendance Rate calculation
    attendance_rate = round((present_today / total_employees * 100), 1) if total_employees > 0 else 0
    
    # Department stats for Chart.js
    departments = Department.query.all()
    dept_labels = [d.name for d in departments]
    dept_counts = [len(d.employees) for d in departments]
    
    # Real AI Risks
    ai_risks = get_turnover_risk_ai()
    
    # Radar Chart Data
    radar_data = get_radar_data()
    
    # 7-day Attendance Trend
    attendance_trend = get_attendance_trend(7)
    
    # Recent Activities
    recent_activities = get_recent_activity(8)
    
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
    from analytics import get_turnover_risk_ai, get_recent_activity, get_radar_data
    
    total_employees = Employee.query.count()
    today = datetime.now().date()
    present_today = Attendance.query.filter_by(work_date=today).count()
    pending_leave_reqs = LeaveRequest.query.filter_by(status='Pending').all()
    
    ai_risks = get_turnover_risk_ai()
    recent_activities = get_recent_activity(10)
    radar_data = get_radar_data()
    
    return render_template('index_hr.html', 
                           total_employees=total_employees,
                           present_today=present_today,
                           ai_risks=ai_risks,
                           pending_leave=pending_leave_reqs,
                           recent_activities=recent_activities,
                           radar_data=radar_data)

def employee_dashboard():
    from analytics import get_individual_performance, get_individual_radar_data
    
    today = datetime.now().date()
    today_att = Attendance.query.filter_by(employee_id=current_user.id, work_date=today).first()
    tasks = Task.query.filter_by(employee_id=current_user.id, status='Pending').order_by(Task.due_date.asc()).limit(5).all()
    
    # Real KPI data
    perf = get_individual_performance(current_user.id)
    radar_data = get_individual_radar_data(current_user.id)
    
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
    
    if file:
        # Kiểm tra định dạng
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext not in ['jpg', 'jpeg', 'png']:
            return jsonify({'success': False, 'message': 'Định dạng file không hỗ trợ (chỉ nhận JPG, PNG)'}), 400
        
        # Kiểm tra dung lượng (2MB)
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > 2 * 1024 * 1024:
            return jsonify({'success': False, 'message': 'Dung lượng file quá lớn (> 2MB)'}), 400
            
        # Tạo tên file duy nhất
        new_filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
        upload_path = os.path.join('static', 'uploads', 'avatars')
        
        # Đảm bảo thư mục tồn tại
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        # Lưu file
        file_path = os.path.join(upload_path, new_filename)
        file.save(file_path)
        
        # Cập nhật DB
        old_avatar = current_user.avatar
        current_user.avatar = new_filename
        db.session.commit()
        
        # Xóa ảnh cũ nếu không phải ảnh mặc định
        if old_avatar and old_avatar != 'default_avatar.png':
            try:
                old_path = os.path.join(upload_path, old_avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)
            except:
                pass
        
        return jsonify({
            'success': True, 
            'message': 'Cập nhật ảnh đại diện thành công!',
            'avatar_url': f'/static/uploads/avatars/{new_filename}'
        })
