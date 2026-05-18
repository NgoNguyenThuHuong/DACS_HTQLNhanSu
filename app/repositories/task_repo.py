from app.repositories.base_repo import BaseRepository
from app.models import Task, Employee
from app.extensions import db
from sqlalchemy.orm import joinedload

class TaskRepository(BaseRepository):
    model = Task

    def get_tasks_filtered(self, search="", status="", priority="", category=""):
        query = db.session.query(Task).options(joinedload(Task.employee)).join(Employee)
        if search:
            query = query.filter((Employee.fullname.ilike(f'%{search}%')) | (Task.title.ilike(f'%{search}%')))
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if category:
            query = query.filter(Task.category == category)
        return query.order_by(Task.created_at.desc()).all()

    def get_distinct_categories(self):
        categories = db.session.query(Task.category).distinct().all()
        return [c[0] for c in categories if c[0]]
