from app import db
from datetime import datetime

class CaseManagerPerformance(db.Model):
    __tablename__ = 'performance'
    __table_args__ = {'schema': 'cms'}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CaseManagerID = db.Column(db.String(50), nullable=False)
    tx_cur = db.Column(db.Integer, default=0)
    iit = db.Column(db.Integer, default=0)
    dead = db.Column(db.Integer, default=0)
    discontinued = db.Column(db.Integer, default=0)
    transferred_out = db.Column(db.Integer, default=0)
    appointments_schedule = db.Column(db.Integer, default=0)
    appointments_completed = db.Column(db.Integer, default=0)
    appointment_compliance = db.Column(db.Numeric(5, 2), default=0)
    viral_load_eligible = db.Column(db.Integer, default=0)
    viral_load_samples = db.Column(db.Integer, default=0)
    sample_collection_rate = db.Column(db.Numeric(5, 2), default=0)
    viral_load_results = db.Column(db.Integer, default=0)
    viral_load_suppressed = db.Column(db.Integer, default=0)
    suppression_rate = db.Column(db.Numeric(5, 2), default=0)
    final_score = db.Column(db.Numeric(5, 2), default=0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
