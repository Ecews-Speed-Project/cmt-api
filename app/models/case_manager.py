from os import name
from app import db
from datetime import datetime
class CaseManager(db.Model):
    __tablename__ = 'case_managers'
    __table_args__ = {'schema': 'cms'}
    cm_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    cmt = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    facilities = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assigned_patients = db.relationship(
        'Patient',
        primaryjoin="CaseManager.cm_id==foreign(Patient.case_manager_id)",
        lazy='selectin'
    )
    
    performance_metrics = db.relationship(
        'CaseManagerPerformance', 
        primaryjoin="CaseManager.id==foreign(CaseManagerPerformance.CaseManagerID)",
        backref='case_manager', 
        lazy=True)
    

    drug_pickup_appointments = db.relationship(
        'DrugPickup',
        primaryjoin="CaseManager.id==foreign(DrugPickup.case_manager)",
        backref='assigned_case_manager',
        lazy=True
    )
    
    viral_load_appointments = db.relationship(
        'ViralLoad',
        primaryjoin="CaseManager.id==foreign(ViralLoad.case_manager)",
        backref='assigned_case_manager',
        lazy=True
    )
    

class CaseManagerClaims(db.Model):
    __tablename__ = 'UserClaims'
    __table_args__ = {'schema': 'user'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column("UserId", db.Integer, db.ForeignKey('user.Users.Id'))
    claim_type = db.Column("ClaimType", db.String(100), nullable=False)
    claim_value = db.Column("ClaimValue", db.String(100), nullable=False)