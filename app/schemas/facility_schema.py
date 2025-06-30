from app.schemas import ma
from app.models import Facility, State

class StateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = State
        include_fk = True

    id = ma.auto_field()
    name = ma.auto_field()
    code = ma.auto_field()

class FacilitySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Facility
        include_fk = True
    
    id = ma.auto_field()
    name = ma.auto_field()
    datim_code = ma.auto_field()
    state_id = ma.auto_field()
    lga = ma.auto_field()

facility_schema = FacilitySchema()
facilities_schema = FacilitySchema(many=True)
state_schema = StateSchema()
states_schema = StateSchema(many=True)
