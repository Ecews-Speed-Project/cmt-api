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
    """
    Get all patients (filtered by user permissions)
    ---
    tags:
      - Patients
    security:
      - Bearer: []
    responses:
      200:
        description: List of patients retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              pepid:
                type: string
              fullname:
                type: string
              case_manager_id:
                type: integer
              created_at:
                type: string
                format: date-time
      401:
        description: Unauthorized - invalid or missing token
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    patients = PatientService.get_filtered_patients(current_user)
    return jsonify(patients_schema.dump(patients))

@bp.route('/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_details(patient_id):
    """
    Get detailed information for a specific patient
    ---
    tags:
      - Patients
    parameters:
      - name: patient_id
        in: path
        type: integer
        required: true
        description: The patient identifier
    security:
      - Bearer: []
    responses:
      200:
        description: Patient details retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            pepid:
              type: string
            fullname:
              type: string
            case_manager_id:
              type: integer
            created_at:
              type: string
              format: date-time
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Patient not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Patient not found"
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    patient = PatientService.get_patient_details(patient_id, current_user)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient_schema.dump(patient))

@bp.route('/<int:patient_id>/metrics', methods=['GET'])
@jwt_required()
@validate_date_range
def get_patient_metrics(patient_id):
    """
    Get performance metrics for a specific patient
    ---
    tags:
      - Patients
    parameters:
      - name: patient_id
        in: path
        type: integer
        required: true
        description: The patient identifier
      - name: start
        in: query
        type: string
        format: date
        description: Start date for metrics period (YYYY-MM-DD)
        example: "2024-01-01"
      - name: end
        in: query
        type: string
        format: date
        description: End date for metrics period (YYYY-MM-DD)
        example: "2024-12-31"
    security:
      - Bearer: []
    responses:
      200:
        description: Patient metrics retrieved successfully
        schema:
          type: object
          properties:
            appointment_attendance:
              type: number
              format: float
            drug_pickup_rate:
              type: number
              format: float
            viral_load_suppression:
              type: number
              format: float
      400:
        description: Bad request - invalid date range
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Patient not found
    """
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    metrics = PatientService.get_patient_metrics(patient_id, start_date, end_date)
    return jsonify(metrics)

@bp.route('/<int:patient_id>/drug-pickups', methods=['GET'])
@jwt_required()
@validate_date_range
def get_drug_pickups(patient_id):
    """
    Get drug pickup history for a specific patient
    ---
    tags:
      - Patients
    parameters:
      - name: patient_id
        in: path
        type: integer
        required: true
        description: The patient identifier
      - name: start
        in: query
        type: string
        format: date
        description: Start date for pickup history (YYYY-MM-DD)
        example: "2024-01-01"
      - name: end
        in: query
        type: string
        format: date
        description: End date for pickup history (YYYY-MM-DD)
        example: "2024-12-31"
    security:
      - Bearer: []
    responses:
      200:
        description: Drug pickup history retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              patient_id:
                type: integer
              pickup_date:
                type: string
                format: date
              drug_name:
                type: string
              quantity:
                type: string
      400:
        description: Bad request - invalid date range
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Patient not found
    """
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    pickups = PatientService.get_drug_pickups(patient_id, start_date, end_date)
    return jsonify(pickups)

@bp.route('/<int:patient_id>/viral-load', methods=['GET'])
@jwt_required()
@validate_date_range
def get_viral_load(patient_id):
    """
    Get viral load history for a specific patient
    ---
    tags:
      - Patients
    parameters:
      - name: patient_id
        in: path
        type: integer
        required: true
        description: The patient identifier
      - name: start
        in: query
        type: string
        format: date
        description: Start date for viral load history (YYYY-MM-DD)
        example: "2024-01-01"
      - name: end
        in: query
        type: string
        format: date
        description: End date for viral load history (YYYY-MM-DD)
        example: "2024-12-31"
    security:
      - Bearer: []
    responses:
      200:
        description: Viral load history retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              patient_id:
                type: integer
              test_date:
                type: string
                format: date
              viral_load_value:
                type: string
              is_suppressed:
                type: boolean
      400:
        description: Bad request - invalid date range
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Patient not found
    """
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    viral_loads = PatientService.get_viral_load_history(patient_id, start_date, end_date)
    return jsonify(viral_loads)

@bp.route('/<int:patient_id>/biometric-status', methods=['GET'])
@jwt_required()
def get_biometric_status(patient_id):
    """
    Get biometric status for a specific patient
    ---
    tags:
      - Patients
    parameters:
      - name: patient_id
        in: path
        type: integer
        required: true
        description: The patient identifier
    security:
      - Bearer: []
    responses:
      200:
        description: Biometric status retrieved successfully
        schema:
          type: object
          properties:
            patient_id:
              type: integer
            has_biometrics:
              type: boolean
            biometric_date:
              type: string
              format: date
              nullable: true
            biometric_type:
              type: string
              nullable: true
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Patient not found
    """
    status = PatientService.get_biometric_status(patient_id)
    return jsonify(status)

@bp.route('/filter', methods=['GET'])
@jwt_required()
def filter_patients():
    """
    Filter patients by location (state and/or facility)
    ---
    tags:
      - Patients
    parameters:
      - name: state
        in: query
        type: integer
        description: State ID to filter by
        example: 1
      - name: facility
        in: query
        type: integer
        description: Facility ID to filter by
        example: 5
    security:
      - Bearer: []
    responses:
      200:
        description: Filtered patients retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              pepid:
                type: string
              fullname:
                type: string
              case_manager_id:
                type: integer
              created_at:
                type: string
                format: date-time
      401:
        description: Unauthorized - invalid or missing token
      403:
        description: Forbidden - insufficient permissions
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unauthorized access"
    """
    state_id = request.args.get('state')
    facility_id = request.args.get('facility')
    current_user = UserService.get_user_by_id(get_jwt_identity())
    
    if current_user.role != 'super_admin' and current_user.role != 'Admin':
        if facility_id and facility_id != str(current_user.facility_id):
            return jsonify({"error": "Unauthorized access"}), 403
            
    patients = PatientService.get_filtered_by_location(state_id, facility_id)
    return jsonify(patients_schema.dump(patients))
