from app.extensions import db

class BaseRepository:
    model = None

    def __init__(self):
        if self.model is None:
            raise NotImplementedError("Repository subclass must define a 'model' attribute.")

    def get_by_id(self, entity_id):
        return db.session.get(self.model, entity_id)

    def get_all(self):
        return db.session.query(self.model).all()

    def add(self, entity):
        db.session.add(entity)
        return entity

    def delete(self, entity):
        db.session.delete(entity)
