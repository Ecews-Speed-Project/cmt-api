from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import PatientService, UserService
from app.schemas.patient_schema import patient_schema, patients_schema
from app.utils.rbac import role_required
from app.utils.validators import validate_date_range

bp = Blueprint('patient', __name__, url_prefix='/api/patients')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_patients():
    current_user = UserService.get_user_by_id(get_jwt_identity())
    patients = PatientService.get_filtered_patients(current_user)
    return jsonify(patients_schema.dump(patients))

@bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_details(patient_id):
    current_user = UserService.get_user_by_id(get_jwt_identity())
    patient = PatientService.get_patient_details(patient_id, current_user)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient_schema.dump(patient))

@bp.route('/<int:patient_id>/metrics', methods=['GET'])
@jwt_required()
@validate_date_range
def get_patient_metrics(patient_id):
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    metrics = PatientService.get_patient_metrics(patient_id, start_date, end_date)
    return jsonify(metrics)

@bp.route('/<int:patient_id>/drug-pickups', methods=['GET'])
@jwt_required()
@validate_date_range
def get_drug_pickups(patient_id):
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    pickups = PatientService.get_drug_pickups(patient_id, start_date, end_date)
    return jsonify(pickups)

@bp.route('/<int:patient_id>/viral-load', methods=['GET'])
@jwt_required()
@validate_date_range
def get_viral_load(patient_id):
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    viral_loads = PatientService.get_viral_load_history(patient_id, start_date, end_date)
    return jsonify(viral_loads)

@bp.route('/<int:patient_id>/biometric-status', methods=['GET'])
@jwt_required()
def get_biometric_status(patient_id):
    status = PatientService.get_biometric_status(patient_id)
    return jsonify(status)

@bp.route('/filter', methods=['GET'])
@jwt_required()
def filter_patients():
    state_id = request.args.get('state')
    facility_id = request.args.get('facility')
    current_user = UserService.get_user_by_id(get_jwt_identity())
    
    if current_user.role != 'super_admin' and current_user.role != 'Admin':
        if facility_id and facility_id != str(current_user.facility_id):
            return jsonify({"error": "Unauthorized access"}), 403
            
    patients = PatientService.get_filtered_by_location(state_id, facility_id)
    return jsonify(patients_schema.dump(patients))
