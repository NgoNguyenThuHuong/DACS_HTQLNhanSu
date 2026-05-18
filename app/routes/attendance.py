from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from app.services import AttendanceService
from app.repositories import AttendanceRepository
from app.core.exceptions import ValidationError, AIVerificationError, BusinessException

attendance = Blueprint('attendance', __name__)
attendance_service = AttendanceService()
attendance_repo = AttendanceRepository()

@attendance.route('/attendance')
@login_required
def index():
    att = attendance_repo.get_today_attendance(current_user.id)
    return render_template('modules/attendance/index.html', att=att)

@attendance.route('/attendance/verify', methods=['POST'])
@login_required
def verify():
    data = request.get_json() or {}
    image_data = data.get('image')
    action = data.get('action') # 'check_in' or 'check_out'
    
    dept_name = current_user.department.name if current_user.department else ""
    pos_str = current_user.position if current_user.position else ""
    upload_folder = current_app.config['ATTENDANCE_UPLOAD_FOLDER']

    try:
        token, qr_filename = attendance_service.verify_and_record_attendance(
            employee_id=current_user.id,
            employee_fullname=current_user.fullname,
            employee_code=current_user.employee_code,
            department_name=dept_name,
            position_str=pos_str,
            action=action,
            image_base64=image_data,
            upload_folder=upload_folder
        )
        
        return jsonify({
            'success': True, 
            'message': f'Xác thực {action} thành công!',
            'qr_url': url_for('static', filename=f'uploads/attendance/{qr_filename}'),
            'token': token
        })
    except (ValidationError, AIVerificationError, BusinessException) as e:
        return jsonify({'success': False, 'message': e.message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi hệ thống: {str(e)}'})

@attendance.route('/attendance/checkout', methods=['POST'])
@login_required
def checkout():
    upload_folder = current_app.config['ATTENDANCE_UPLOAD_FOLDER']
    try:
        token, qr_filename, time_str = attendance_service.manual_checkout(
            employee_id=current_user.id,
            employee_code=current_user.employee_code,
            upload_folder=upload_folder
        )
        
        return jsonify({
            'success': True,
            'message': f'Check-out thành công lúc {time_str}',
            'qr_url': url_for('static', filename=f'uploads/attendance/{qr_filename}'),
            'token': token,
            'time': time_str
        })
    except (ValidationError, BusinessException) as e:
        return jsonify({'success': False, 'message': e.message})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi hệ thống: {str(e)}'})
