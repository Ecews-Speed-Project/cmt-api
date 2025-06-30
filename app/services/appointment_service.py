from models.appointments import Appointment, DrugPickup, ViralLoad
from schemas.appointment_schema import (
    appointments_schema, drug_pickups_schema, viral_loads_schema
)
from app import db

class AppointmentService:
    @staticmethod
    # def get_appointments(patient_id, start_date=None, end_date=None):
    #     query = Appointment.query.filter_by(patient_id=patient_id)
    #     if start_date and end_date:
    #         query = query.filter(Appointment.scheduled_date.between(start_date, end_date))
    #     appointments = query.all()
    #     return appointments_schema.dump(appointments)

    @staticmethod
    def get_drug_pickups(patient_id, start_date=None, end_date=None):
        query = DrugPickup.query.filter_by(patient_id=patient_id)
        if start_date and end_date:
            query = query.filter(DrugPickup.scheduled_date.between(start_date, end_date))
        pickups = query.all()
        return drug_pickups_schema.dump(pickups)

    @staticmethod
    def get_viral_loads(patient_id, start_date=None, end_date=None):
        query = ViralLoad.query.filter_by(patient_id=patient_id)
        if start_date and end_date:
            query = query.filter(ViralLoad.collection_date.between(start_date, end_date))
        loads = query.all()
        return viral_loads_schema.dump(loads)
