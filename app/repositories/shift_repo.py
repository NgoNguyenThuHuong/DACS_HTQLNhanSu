from app.repositories.base_repo import BaseRepository
from app.models.models import Shift
from app.extensions import db

class ShiftRepository(BaseRepository):
    model = Shift

    def get_all_shifts(self):
        return db.session.query(Shift).all()
