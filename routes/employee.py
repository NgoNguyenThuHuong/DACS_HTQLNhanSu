from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, LeaveRequest, Task
from datetime import datetime

employee = Blueprint('employee', __name__)

@employee.route('/leave', methods=['GET', 'POST'])
@login_required
def leave_index():
    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        reason = request.form.get('reason')
        
        new_req = LeaveRequest(
            employee_id=current_user.id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='Pending'
        )
        db.session.add(new_req)
        db.session.commit()
        
        flash('Yêu cầu nghỉ phép của bạn đã được gửi và đang chờ duyệt.', 'success')
        return redirect(url_for('employee.leave_index'))

    # Show user's leave requests
    requests = LeaveRequest.query.filter_by(employee_id=current_user.id).all()
    return render_template('modules/leave/index.html', requests=requests)

@employee.route('/tasks')
@login_required
def tasks_index():
    tasks = Task.query.filter_by(employee_id=current_user.id).order_by(Task.due_date.asc()).all()
    return render_template('modules/employee/tasks.html', tasks=tasks, now=datetime.now())

@employee.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, employee_id=current_user.id).first_or_404()
    new_status = request.form.get('status')
    
    if new_status in ['In_Progress', 'Completed']:
        task.status = new_status
        db.session.commit()
        flash(f'Cập nhật trạng thái nhiệm vụ thành công!', 'success')
        
    return redirect(url_for('employee.tasks_index'))


