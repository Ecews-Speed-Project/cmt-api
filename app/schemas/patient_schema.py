from app.schemas import ma
from app.models import Patient
from .appointment_schema import DrugPickupSchema, ViralLoadSchema

class PatientSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Patient
        include_fk = True

    id = ma.auto_field()
    pep_id = ma.auto_field()
    case_manager_id = ma.auto_field()
    state = ma.auto_field()
    lga = ma.auto_field()
    datim_code = ma.auto_field()
    facility_name = ma.auto_field()
    sex = ma.auto_field()
    dob = ma.auto_field()
    current_age = ma.auto_field()
    art_start_date = ma.auto_field()
    pharmacy_last_pickup_date = ma.auto_field()
    current_art_status = ma.auto_field()
    outcomes = ma.auto_field()
    outcomes_date = ma.auto_field()
    
    drug_pickup_appointments = ma.Nested(DrugPickupSchema, many=True)
    viral_load_appointments = ma.Nested(ViralLoadSchema, many=True)

patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)
