from . import ma

class CMTReportSchema(ma.Schema):
    class Meta:
        fields = (
            'team_name', 'state', 'facility', 'total_patients',
            'active_patients', 'inactive_patients', 'active_rate',
            'appointment_adherence', 'viral_load_collection_rate',
            'viral_suppression_rate', 'drug_pickup_adherence'
        )

class CaseManagerReportSchema(ma.Schema):
    class Meta:
        fields = (
            'name', 'cmt', 'assigned_patients', 'active_patients',
            'appointment_adherence', 'viral_load_collection',
            'viral_suppression', 'biometric_recapture_pending',
            'drug_pickup_adherence'
        )

cmt_report_schema = CMTReportSchema(many=True)
case_manager_report_schema = CaseManagerReportSchema(many=True)
