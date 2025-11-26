from app import db
from datetime import datetime

class Patient(db.Model):
    __tablename__ = 'CMPatientLineList'
    __table_args__ = {'schema': 'dbo'}
    
    id = db.Column('uniquePatientId', db.String(100), primary_key=True)
    pep_id = db.Column('pepId', db.String(50), nullable=False)
    case_manager_id = db.Column('caseManagerId', db.Integer, db.ForeignKey('cms.case_managers.cm_id'), nullable=True)
    
    # Facility Information
    state = db.Column('state', db.String(100))
    lga = db.Column('lga', db.String(100))
    datim_code = db.Column('datimCode', db.String(50))
    facility_name = db.Column('facilityName', db.String(200), 
                               db.ForeignKey('dbo.Facilities.FacilityName'))
    
    # Patient Demographics
    sex = db.Column('sex', db.String(10))
    dob = db.Column('dob', db.DateTime)
    current_age = db.Column('currentAge', db.Integer)
    current_age_months = db.Column('currentAgeMonths', db.Integer)
    age_band = db.Column('age_band', db.String(50))
    
    # Clinical Information
    art_start_date = db.Column('artStartDate', db.DateTime)
    days_on_art = db.Column('daysOnArt', db.String(50))
    pharmacy_last_pickup_date = db.Column('pharmacyLastPickupdate', db.DateTime)
    days_of_arv_refill = db.Column('daysOfArvRefill', db.Integer)
    current_pregnancy_status = db.Column('currentPregnancyStatus', db.String(50))
    current_viral_load = db.Column('currentViralLoad', db.Float)
    date_of_current_viral_load = db.Column('dateofCurrentViralLoad', db.DateTime)
    last_date_of_sample_collection = db.Column('lastDateOfSampleCollection', db.DateTime)
    
    # Status Information
    outcomes = db.Column('outcomes', db.String(100))
    outcomes_date = db.Column('outcomesDate', db.DateTime)
    current_art_status = db.Column('currentArtStatus', db.String(50))
    
    # Transfer Information
    is_transfer_in = db.Column('ti', db.Boolean)
    date_transfered_in = db.Column('dateTransferedIn', db.DateTime)
    
    # Recapture Information
    recapture = db.Column('recapture', db.Boolean)
    date_of_recapture = db.Column('dateOfRecapture', db.DateTime)
    recapture_count = db.Column('recaptureCount', db.Integer)
    
    # Relationships
    drug_pickup_appointments = db.relationship(
        'DrugPickup',
        backref='patient',
        lazy=True,
        primaryjoin="and_(Patient.pep_id==foreign(DrugPickup.pep_id), "
                   "Patient.datim_code==foreign(DrugPickup.datim_code))"
    )
    viral_load_appointments = db.relationship(
        'ViralLoad',
        backref='patient',
        lazy=True,
        primaryjoin="and_(Patient.pep_id==foreign(ViralLoad.pep_id), "
                   "Patient.datim_code==foreign(ViralLoad.datim_code))"
    )
