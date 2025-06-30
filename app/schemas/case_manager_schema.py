from . import ma
from app.models import CaseManager, CaseManagerPerformance

class CaseManagerSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CaseManager
        include_fk = True

    cm_id = ma.auto_field()
    id = ma.auto_field()
    cmt = ma.auto_field()
    fullname = ma.auto_field()
    role = ma.auto_field()
    state = ma.auto_field()
    facilities = ma.auto_field()

class CaseManagerPerformanceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CaseManagerPerformance

    id = ma.auto_field()
    appointments_schedule = ma.auto_field()
    appointments_completed = ma.auto_field()
    viral_load_suppressed = ma.auto_field()

case_manager_schema = CaseManagerSchema()
case_managers_schema = CaseManagerSchema(many=True)
case_manager_performance_schema = CaseManagerPerformanceSchema()
case_manager_performances_schema = CaseManagerPerformanceSchema(many=True)
