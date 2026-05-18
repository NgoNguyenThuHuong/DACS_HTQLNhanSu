from app.repositories import EmployeeRepository, UnitOfWork
from app.models import Employee, LeaveRequest, Task
from app.core.exceptions import EntityNotFoundException, ValidationError
from app.extensions import db
import os
import uuid
from werkzeug.utils import secure_filename

class EmployeeService:
    def __init__(self):
        self.employee_repo = EmployeeRepository()

    def get_employee_profile(self, employee_id):
        employee = self.employee_repo.get_by_id(employee_id)
        if not employee:
            raise EntityNotFoundException("Không tìm thấy thông tin nhân viên.")
        return employee

    def reset_password(self, employee_id):
        with UnitOfWork():
            employee = self.employee_repo.get_by_id(employee_id)
            if not employee:
                raise EntityNotFoundException("Không tìm thấy thông tin nhân viên.")
            employee.password = "123456" # Mật khẩu mặc định theo yêu cầu tương thích ngược
            return True

    def update_avatar(self, employee_id, file, upload_path='static/uploads/avatars'):
        if not file or file.filename == '':
            raise ValidationError("File ảnh đại diện không hợp lệ.")
            
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext not in ['jpg', 'jpeg', 'png']:
            raise ValidationError("Định dạng file không hỗ trợ (chỉ nhận JPG, PNG).")
            
        # Kiểm tra dung lượng (2MB)
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > 2 * 1024 * 1024:
            raise ValidationError("Dung lượng file quá lớn (> 2MB).")

        new_filename = f"avatar_{employee_id}_{uuid.uuid4().hex[:8]}.{ext}"
        
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)

        file_path = os.path.join(upload_path, new_filename)
        file.save(file_path)

        with UnitOfWork():
            employee = self.employee_repo.get_by_id(employee_id)
            if not employee:
                raise EntityNotFoundException("Không tìm thấy thông tin nhân viên.")
            
            old_avatar = employee.avatar
            employee.avatar = new_filename
            
            # Xóa ảnh cũ nếu có
            if old_avatar and old_avatar != 'default_avatar.png':
                try:
                    old_path = os.path.join(upload_path, old_avatar)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass

        return new_filename

    # Các phương thức nghiệp vụ nghỉ phép & tác vụ phục vụ cho routes/employee.py
    def create_leave_request(self, employee_id, leave_type, start_date, end_date, reason):
        if not start_date or not end_date:
            raise ValidationError("Ngày bắt đầu và ngày kết thúc không được để trống.")
        if start_date > end_date:
            raise ValidationError("Ngày bắt đầu không được lớn hơn ngày kết thúc.")

        with UnitOfWork():
            new_req = LeaveRequest(
                employee_id=employee_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status='Pending'
            )
            db.session.add(new_req)
            return True

    def get_leave_requests(self, employee_id):
        return db.session.query(LeaveRequest).filter(LeaveRequest.employee_id == employee_id).all()

    def get_tasks(self, employee_id):
        return db.session.query(Task).filter(Task.employee_id == employee_id).order_by(Task.due_date.asc()).all()

    def update_task_status(self, task_id, employee_id, new_status):
        if new_status not in ['In_Progress', 'Completed']:
            raise ValidationError("Trạng thái nhiệm vụ không hợp lệ.")
            
        with UnitOfWork():
            task = db.session.query(Task).filter(Task.id == task_id, Task.employee_id == employee_id).first()
            if not task:
                raise EntityNotFoundException("Không tìm thấy nhiệm vụ yêu cầu.")
            task.status = new_status
            return True
