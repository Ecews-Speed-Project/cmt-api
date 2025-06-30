from app.schemas import ma
from app.models import DrugPickup, ViralLoad

class DrugPickupSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DrugPickup
        include_fk = True
    
    id = ma.auto_field()
    pep_id = ma.auto_field()
    pharmacy_last_pickup_date = ma.auto_field()
    days_of_arv_refill = ma.auto_field()
    next_visit_date = ma.auto_field()
    outcomes = ma.auto_field()
    outcomes_date = ma.auto_field()

class ViralLoadSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ViralLoad
        include_fk = True
    
    id = ma.auto_field()
    pep_id = ma.auto_field()
    current_viral_load = ma.auto_field()
    date_of_current_viral_load = ma.auto_field()

drug_pickups_schema = DrugPickupSchema(many=True)
viral_loads_schema = ViralLoadSchema(many=True)
