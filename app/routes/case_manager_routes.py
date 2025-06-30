from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import CaseManagerService, UserService
from app.schemas.case_manager_schema import case_manager_schema, case_managers_schema
from app.schemas.patient_schema import patients_schema
from app.utils.rbac import role_required
from app.utils.validators import validate_date_range

bp = Blueprint('case_manager', __name__, url_prefix='/api/case-managers')

@bp.route('/', methods=['GET'])
@jwt_required()
#@role_required(['Super Admin', 'State', 'Admin'])
def get_case_managers():
    current_user = UserService.get_user_by_id(get_jwt_identity())
    case_managers = CaseManagerService.get_all_case_managers(current_user)
    return jsonify(case_managers)

@bp.route('/<int:cm_id>/patients', methods=['GET'])
@jwt_required()
def get_case_manager_patients(cm_id):
    patients = CaseManagerService.get_patients(cm_id)
    return jsonify(patients_schema.dump(patients))

@bp.route('/<int:cm_id>/performance', methods=['GET'])
@jwt_required()
@validate_date_range
def get_case_manager_performance(cm_id):
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    metrics = CaseManagerService.get_performance(cm_id, start_date, end_date)
    return jsonify(metrics)

@bp.route('/<int:cm_id>', methods=['PUT'])
@jwt_required()
@role_required(['super_admin', 'facility_backstop'])
def update_case_manager(cm_id):
    data = request.get_json()
    updated = CaseManagerService.update_case_manager(cm_id, data)
    return jsonify(case_manager_schema.dump(updated))

@bp.route('/<int:case_manager_id>', methods=['GET'])
@jwt_required()
def get_case_manager(case_manager_id):
    current_user = UserService.get_user_by_id(get_jwt_identity())
    case_manager = CaseManagerService.get_case_manager(case_manager_id, current_user)
    if case_manager:
        return jsonify(case_manager), 200
    return jsonify({'message': 'Case manager not found or access denied'}), 404
