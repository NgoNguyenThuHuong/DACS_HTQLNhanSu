from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services import EmployeeService
from app.core.exceptions import ValidationError, EntityNotFoundException
from datetime import datetime

employee = Blueprint('employee', __name__)
employee_service = EmployeeService()

@employee.route('/leave', methods=['GET', 'POST'])
@login_required
def leave_index():
    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        reason = request.form.get('reason')
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
            
            employee_service.create_leave_request(
                employee_id=current_user.id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )
            flash('Yêu cầu nghỉ phép của bạn đã được gửi và đang chờ duyệt.', 'success')
        except ValidationError as e:
            flash(e.message, 'error')
        except Exception as e:
            flash(f'Lỗi hệ thống: {str(e)}', 'error')
            
        return redirect(url_for('employee.leave_index'))

    requests = employee_service.get_leave_requests(current_user.id)
    return render_template('modules/leave/index.html', requests=requests)

@employee.route('/tasks')
@login_required
def tasks_index():
    tasks = employee_service.get_tasks(current_user.id)
    return render_template('modules/employee/tasks.html', tasks=tasks, now=datetime.now())

@employee.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    new_status = request.form.get('status')
    
    try:
        employee_service.update_task_status(
            task_id=task_id,
            employee_id=current_user.id,
            new_status=new_status
        )
        flash(f'Cập nhật trạng thái nhiệm vụ thành công!', 'success')
    except (ValidationError, EntityNotFoundException) as e:
        flash(e.message, 'error')
    except Exception as e:
        flash(f'Lỗi hệ thống: {str(e)}', 'error')
        
    return redirect(url_for('employee.tasks_index'))
