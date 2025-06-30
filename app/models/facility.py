from app.extensions import db
from datetime import datetime

class State(db.Model):
    __tablename__ = 'State'
    __table_args__ = {'schema': 'dbo'}
    
    id = db.Column('StateId', db.Integer, primary_key=True)
    name = db.Column('StateName', db.String(100), nullable=False)
    code = db.Column('StateCode', db.String(10), nullable=False)
    facilities = db.relationship('Facility', backref='state', lazy=True)
    # cmts = db.relationship('CMT',
    #     primaryjoin="State.id==foreign(CMT.state)", 
    #     backref='states', lazy=True)

class Facility(db.Model):
    __tablename__ = 'Facilities'
    __table_args__ = (
        db.UniqueConstraint('DatimCode', name='UQ_Facilities_DatimCode'),
        {'schema': 'dbo'}
    )
    
    id = db.Column('FacilityId', db.Integer, primary_key=True)
    datim_code = db.Column('DatimCode', db.String(50), unique=True, nullable=False)
    name = db.Column('FacilityName', db.String(100), nullable=False)
    state_id = db.Column('StateId', db.Integer, db.ForeignKey('dbo.State.StateId'), nullable=False)
    lga = db.Column('Lga', db.String(100), nullable=False)
    
    # cmts = db.relationship('CMT',
    #     primaryjoin="Facility.id==CMT.facility_id", 
    #     backref='facility', lazy=True)
    
   