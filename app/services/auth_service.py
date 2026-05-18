from app.repositories import EmployeeRepository, UnitOfWork
from app.models import Employee
from app.core.exceptions import ValidationError

class AuthService:
    def __init__(self):
        self.employee_repo = EmployeeRepository()

    def register_user(self, username, password, fullname, employee_code, email):
        if not username or not password or not fullname or not employee_code:
            raise ValidationError("Các trường thông tin bắt buộc không được để trống.")
            
        with UnitOfWork():
            user_exists = self.employee_repo.get_by_username(username)
            code_exists = self.employee_repo.get_by_code(employee_code)
            
            if user_exists:
                raise ValidationError("Tên đăng nhập đã tồn tại.")
            if code_exists:
                raise ValidationError("Mã nhân viên đã được đăng ký.")

            new_user = Employee(
                username=username,
                password=password, # Plain text theo yêu cầu hệ thống cũ
                fullname=fullname,
                employee_code=employee_code,
                email=email,
                role='Employee'
            )
            self.employee_repo.add(new_user)
            return new_user

    def authenticate_user(self, username, password):
        if not username or not password:
            raise ValidationError("Tên đăng nhập và mật khẩu không được để trống.")
        
        user = self.employee_repo.get_by_username(username)
        if not user or user.password != password:
            return None
        return user

    def get_user_permissions(self, user):
        perms = {
            'VIEW_REPORTS': user.role in ['Admin', 'HR'],
            'MANAGE_EMPLOYEES': user.role == 'Admin',
            'APPROVE_LEAVE': user.role in ['Admin', 'HR'],
            'MANAGE_RECRUITMENT': user.role in ['Admin', 'HR']
        }
        return perms
