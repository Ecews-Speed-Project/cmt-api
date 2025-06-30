from app.extensions import db
from datetime import datetime

class CMT(db.Model):
    __tablename__ = 'cmt'
    __table_args__ = {'schema': 'cms'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    facility_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Use string references to avoid circular imports
    # case_managers = db.relationship('CaseManager', backref='cmt', lazy=True)
    # performance_metrics = db.relationship('CMTPerformance', backref='cmt', lazy=True)