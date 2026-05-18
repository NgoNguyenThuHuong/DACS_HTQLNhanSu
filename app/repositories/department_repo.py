from app.repositories.base_repo import BaseRepository
from app.models import Department
from app.extensions import db

class DepartmentRepository(BaseRepository):
    model = Department

    def get_all_ordered(self):
        return db.session.query(Department).order_by(Department.name.asc()).all()
