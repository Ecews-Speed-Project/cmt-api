from app import db

class BaseService:
    def commit(self):
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
