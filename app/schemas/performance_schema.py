from app.schemas import ma
from app.models import  CaseManagerPerformance

class TrendDataSchema(ma.Schema):
    class Meta:
        fields = ('week', 'count')

class CaseManagerPerformanceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CaseManagerPerformance
        load_instance = True

    CaseManagerID = ma.auto_field()
    tx_cur = ma.auto_field()
    iit = ma.auto_field()
    dead = ma.auto_field()
    discontinued = ma.auto_field()
    transferred_out = ma.auto_field()
    appointments_schedule = ma.auto_field()
    appointments_completed = ma.auto_field()
    appointment_compliance = ma.auto_field()
    viral_load_eligible = ma.auto_field()
    viral_load_samples = ma.auto_field()
    sample_collection_rate = ma.auto_field()
    viral_load_results = ma.auto_field()
    viral_load_suppressed = ma.auto_field()
    suppression_rate = ma.auto_field()
    final_score = ma.auto_field()   

trend_data_schema = TrendDataSchema(many=True)
performance_schema = CaseManagerPerformanceSchema(many=True)
performance_metrics_schema = CaseManagerPerformanceSchema(many=True)
