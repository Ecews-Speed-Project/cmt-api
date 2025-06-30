from app.schemas import ma
from app.models import CMT, CaseManager
from marshmallow import fields

class CaseManagerSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CaseManager

    id = ma.auto_field()
    fullname = ma.auto_field()
    role = ma.auto_field()
    state = ma.auto_field()
    facilities = ma.auto_field()
    created_at = ma.auto_field()

class CMTSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CMT

    id = ma.auto_field()
    name = ma.auto_field()
    facility_name = ma.auto_field()
    state = ma.auto_field()
    created_at = ma.auto_field()
    case_managers = fields.List(fields.Nested(CaseManagerSchema))
    patient_count = fields.Integer()

# class CMTPerformanceSchema(ma.SQLAlchemySchema):
#     class Meta:
#         model = CMTPerformance

#     id = ma.auto_field()
#     appointments_scheduled = ma.auto_field()
#     appointments_completed = ma.auto_field()
#     appointments_missed = ma.auto_field()
#     viral_load_suppressed = ma.auto_field()

cmt_schema = CMTSchema()
cmts_schema = CMTSchema(many=True)
# cmt_performance_schema = CMTPerformanceSchema()
# cmt_performances_schema = CMTPerformanceSchema(many=True)
