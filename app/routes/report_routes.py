from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services import ReportService
from app.utils.validators import validate_date_range
from app.utils.rbac import role_required

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@bp.route('/cmt', methods=['GET'])
@jwt_required()
@validate_date_range
@role_required(['super_admin', 'Admin', 'facility_backstop'])
def get_cmt_report():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    state_id = request.args.get('state_id')
    
    report_data = ReportService.generate_cmt_report(start_date, end_date, state_id)
    return jsonify(report_data)

@bp.route('/case-managers', methods=['GET'])
@jwt_required()
@validate_date_range
@role_required(['super_admin', 'Admin', 'facility_backstop'])
def get_case_manager_report():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    facility_id = request.args.get('facility_id')
    
    report_data = ReportService.generate_case_manager_report(start_date, end_date, facility_id)
    return jsonify({
        'headers': [
            'Name', 'CMT', 'Assigned Patients', 'Active Patients',
            'Appointment Adherence', 'Viral Load Collection',
            'Viral Suppression', 'Biometric Recapture Pending',
            'Drug Pickup Adherence'
        ],
        'data': [vars(item) for item in report_data]
    })
