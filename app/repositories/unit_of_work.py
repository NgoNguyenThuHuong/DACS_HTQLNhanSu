from app.extensions import db

class UnitOfWork:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            db.session.rollback()
        else:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise
