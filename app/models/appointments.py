from app import db
from datetime import datetime

class DrugPickup(db.Model):
    __tablename__ = 'DrugPickupAppointment'
    __table_args__ = {'schema': 'dbo'}

    id = db.Column('pk', db.Integer, primary_key=True)  # Add primary key
    state = db.Column('State', db.String(100))
    lga = db.Column('LGA', db.String(100))
    datim_code = db.Column('DatimCode', db.String(50))
    facility_name = db.Column('FacilityName', db.String(200))
    pep_id = db.Column('PepID', db.String(50))
    sex = db.Column('Sex', db.String(10))
    pharmacy_last_pickup_date = db.Column('PharmacyLastPickupdate', db.DateTime)
    days_of_arv_refill = db.Column('DaysOfARVRefill', db.Integer)
    next_visit_date = db.Column('NextVisitDate', db.DateTime)  # Removed trailing comma
    outcomes = db.Column('Outcomes', db.String(100))
    outcomes_date = db.Column('OutcomesDate', db.DateTime)
    current_age = db.Column('CurrentAge', db.Integer)
    current_age_months = db.Column('CurrentAgeMonths', db.Integer)
    recapture = db.Column('Recapture', db.Boolean)
    date_of_recapture = db.Column('DateOfRecapture', db.DateTime)
    recapture_count = db.Column('RecaptureCount', db.Integer)
    case_manager = db.Column('CaseManagerId', db.String(100))
    age_band = db.Column('AgeBand', db.String(50))
    next_appointment_date = db.Column('estimatedNextAppointmentPharmacy', db.DateTime)

class ViralLoad(db.Model):
    __tablename__ = 'VLAppointment'
    __table_args__ = {'schema': 'dbo'}

    id = db.Column('pk', db.Integer, primary_key=True)  # Add primary key
    state = db.Column('State', db.String(100))
    lga = db.Column('LGA', db.String(100))
    datim_code = db.Column('DatimCode', db.String(50))
    facility_name = db.Column('FacilityName', db.String(200))
    pep_id = db.Column('PepID', db.String(50))
    sex = db.Column('Sex', db.String(10))
    current_pregnancy_status = db.Column('CurrentPregnancyStatus', db.String(50))
    current_viral_load = db.Column('CurrentViralLoad', db.Float)
    date_of_current_viral_load = db.Column('DateofCurrentViralLoad', db.DateTime)
    last_date_of_sample_collection = db.Column('lastDateOfSampleCollection', db.DateTime)
    outcomes = db.Column('Outcomes', db.String(100))
    outcomes_date = db.Column('OutcomesDate', db.DateTime)
    dob = db.Column('DOB', db.DateTime)
    current_age = db.Column('CurrentAge', db.Integer)
    case_manager = db.Column('CaseManagerId', db.String(100))
    
