from app.models import State, Facility
from app.schemas.facility_schema import (
    facility_schema, facilities_schema,
    states_schema
)
from app import db

class FacilityService:
    @staticmethod
    def get_facilities(state_id=None):
        query = Facility.query
        if state_id:
            query = query.filter_by(state_id=state_id)
        facilities = query.all()
        return facilities_schema.dump(facilities)

    @staticmethod
    def get_states():
        states = State.query.all()
        return states_schema.dump(states)

    @staticmethod
    def get_facility_by_datim(datim_code):
        facility = Facility.query.filter_by(datim_code=datim_code).first()
        return facility_schema.dump(facility) if facility else None
