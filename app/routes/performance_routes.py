from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import UserService, PerformanceService
from app.schemas.performance_schema import performance_schema  # Update import
from app.utils.rbac import role_required
from app.utils.validators import validate_date_range

bp = Blueprint('performance', __name__, url_prefix='/api/performance')

@bp.route('/case-managers', methods=['GET'])
@jwt_required()
#@role_required(['Super Admin', 'facility_backstop', 'Admin'])
def get_case_managers():
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = PerformanceService.get_case_managers_performance(current_user)
    return jsonify(performance_data), 200

@bp.route('/cmts', methods=['GET'])
@jwt_required()
def get_cmt_performance():
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = PerformanceService.get_cmt_performance(current_user)
    return jsonify(performance_data), 200

@bp.route('/case-managers/<string:case_manager_id>', methods=['GET'])
@jwt_required()
def get_case_manager_performance(case_manager_id):
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = PerformanceService.get_single_case_manager_performance(case_manager_id, current_user)
    if performance_data:
        return jsonify(performance_data), 200
    return jsonify({'message': 'Case manager not found'}), 404

@bp.route('/cmts/<string:cmt_name>', methods=['GET'])
@jwt_required()
def get_cmt_performance_by_name(cmt_name):
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = PerformanceService.get_single_cmt_performance(cmt_name, current_user)
    if performance_data:
        return jsonify(performance_data), 200
    return jsonify({'message': 'CMT not found'}), 404

