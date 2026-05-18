from app.repositories.base_repo import BaseRepository
from app.models import LeaveRequest
from app.extensions import db
from sqlalchemy.orm import joinedload

class LeaveRepository(BaseRepository):
    model = LeaveRequest

    def get_pending_requests(self):
        return db.session.query(LeaveRequest)\
            .options(joinedload(LeaveRequest.employee))\
            .filter(LeaveRequest.status == 'Pending')\
            .order_by(LeaveRequest.created_at.desc())\
            .all()

    def get_by_id_with_employee(self, req_id):
        return db.session.query(LeaveRequest)\
            .options(joinedload(LeaveRequest.employee))\
            .filter(LeaveRequest.id == req_id)\
            .first()
