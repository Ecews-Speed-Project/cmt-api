from app.models import Patient, DrugPickup, ViralLoad
from app.schemas.patient_schema import patient_schema, patients_schema
from app.schemas.appointment_schema import drug_pickups_schema, viral_loads_schema
from app import db

class PatientService:
    @staticmethod
    def get_filtered_patients(user):
        query = Patient.query.filter_by(is_active=True)
        
        if user.role != 'super_admin':
            if user.role == 'case_manager':
                query = query.filter_by(case_manager_id=user.id)
            elif user.role == 'facility_backstop':
                query = query.filter_by(facility_datim_code=user.facility_datim_code)
            elif user.role == 'Admin':
                query = query.filter_by(state_id=user.state_id)
                
        return patients_schema.dump(query.all())

    @staticmethod
    def get_patient_details(patient_id: int, user):
        patient = Patient.query.get(patient_id)
        if not patient or not PatientService._can_access_patient(patient, user):
            return None
        return patient_schema.dump(patient)

    @staticmethod
    def _can_access_patient(patient, user):
        if user.role == 'super_admin':
            return True
        if user.role == 'case_manager':
            return patient.case_manager_id == user.id
        if user.role == 'facility_backstop':
            return patient.facility_datim_code == user.facility_datim_code
        if user.role == 'Admin':
            return patient.state_id == user.state_id
        return False

    @staticmethod
    def get_drug_pickups(patient_id, start_date, end_date):
        pickups = DrugPickup.query.filter(
            DrugPickup.patient_id == patient_id,
            DrugPickup.scheduled_date.between(start_date, end_date)
        ).all()
        return drug_pickups_schema.dump(pickups)

    @staticmethod
    def get_viral_load_history(patient_id, start_date, end_date):
        loads = ViralLoad.query.filter(
            ViralLoad.patient_id == patient_id,
            ViralLoad.collection_date.between(start_date, end_date)
        ).all()
        return viral_loads_schema.dump(loads)

    @staticmethod
    def get_biometric_status(patient_id):
        patient = Patient.query.get(patient_id)
        return {
            'patient_id': patient_id,
            'last_capture_date': patient.last_biometric_capture,
            'needs_recapture': patient.needs_biometric_recapture,
            'recapture_due_date': patient.biometric_recapture_due_date
        }
