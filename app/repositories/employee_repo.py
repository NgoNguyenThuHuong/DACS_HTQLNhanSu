from app.repositories.base_repo import BaseRepository
from app.models import Employee
from app.extensions import db
from sqlalchemy.orm import joinedload

class EmployeeRepository(BaseRepository):
    model = Employee

    def get_by_username(self, username):
        return db.session.query(Employee).filter(Employee.username == username).first()

    def get_by_code(self, employee_code):
        return db.session.query(Employee).filter(Employee.employee_code == employee_code).first()

    def get_active_employees(self):
        return db.session.query(Employee).order_by(Employee.created_at.desc()).all()

    def get_with_department(self, employee_id):
        return db.session.query(Employee)\
            .options(joinedload(Employee.department))\
            .filter(Employee.id == employee_id)\
            .first()

    def get_all_with_departments(self):
        return db.session.query(Employee)\
            .options(joinedload(Employee.department))\
            .order_by(Employee.created_at.desc())\
            .all()
