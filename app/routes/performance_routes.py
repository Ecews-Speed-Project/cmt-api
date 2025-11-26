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
    """
    Get performance data for all case managers
    ---
    tags:
      - Performance
    security:
      - Bearer: []
    responses:
      200:
        description: Case manager performance data retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              case_manager_id:
                type: string
              fullname:
                type: string
              tx_cur:
                type: integer
              iit:
                type: integer
              transferred_out:
                type: integer
              dead:
                type: integer
              discontinued:
                type: integer
              appointments_completed:
                type: integer
              appointments_schedule:
                type: integer
              viral_load_suppressed:
                type: integer
              viral_load_samples:
                type: integer
              viral_load_results:
                type: integer
              viral_load_eligible:
                type: integer
              final_score:
                type: number
                format: float
      401:
        description: Unauthorized - invalid or missing token
    """
    pediatrics = request.args.get('pediatrics', 'false').lower() == 'true'
    pmtct = request.args.get('pmtct', 'false').lower() == 'true'
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = PerformanceService.get_case_managers_performance(
        current_user,
        pediatrics_filter=pediatrics,
        pmtct_filter=pmtct
    )
    return jsonify(performance_data), 200

@bp.route('/cmts', methods=['GET'])
@jwt_required()
def get_cmt_performance():
    """
    Get performance data for all CMTs
    ---
    tags:
      - Performance
    security:
      - Bearer: []
    responses:
      200:
        description: CMT performance data retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              cmt_name:
                type: string
              total_case_managers:
                type: integer
              total_tx_cur:
                type: integer
              total_iit:
                type: integer
              total_transferred_out:
                type: integer
              total_dead:
                type: integer
              total_discontinued:
                type: integer
              total_appointments_completed:
                type: integer
              total_appointments_scheduled:
                type: integer
              total_vl_suppressed:
                type: integer
              total_vl_samples:
                type: integer
              total_vl_results:
                type: integer
              total_vl_eligible:
                type: integer
              average_score:
                type: number
                format: float
      401:
        description: Unauthorized - invalid or missing token
    """
    pediatrics = request.args.get('pediatrics', 'false').lower() == 'true'
    pmtct = request.args.get('pmtct', 'false').lower() == 'true'
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = PerformanceService.get_cmt_performance(
        current_user,
        pediatrics_filter=pediatrics,
        pmtct_filter=pmtct
    )
    return jsonify(performance_data), 200

@bp.route('/case-managers/<string:case_manager_id>', methods=['GET'])
@jwt_required()
def get_case_manager_performance(case_manager_id):
    """
    Get performance data for a specific case manager
    ---
    tags:
      - Performance
    parameters:
      - name: case_manager_id
        in: path
        type: string
        required: true
        description: The case manager identifier
        example: "123"
    security:
      - Bearer: []
    responses:
      200:
        description: Case manager performance data retrieved successfully
        schema:
          type: object
          properties:
            case_manager_id:
              type: string
            fullname:
              type: string
            tx_cur:
              type: integer
            iit:
              type: integer
            transferred_out:
              type: integer
            dead:
              type: integer
            discontinued:
              type: integer
            appointments_completed:
              type: integer
            appointments_schedule:
              type: integer
            viral_load_suppressed:
              type: integer
            viral_load_samples:
              type: integer
            viral_load_results:
              type: integer
            viral_load_eligible:
              type: integer
            final_score:
              type: number
              format: float
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Case manager not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Case manager not found"
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = PerformanceService.get_single_case_manager_performance(case_manager_id, current_user)
    if performance_data:
        return jsonify(performance_data), 200
    return jsonify({'message': 'Case manager not found'}), 404

@bp.route('/cmts/<string:cmt_name>', methods=['GET'])
@jwt_required()
def get_cmt_performance_by_name(cmt_name):
    """
    Get performance data for a specific CMT by name
    ---
    tags:
      - Performance
    parameters:
      - name: cmt_name
        in: path
        type: string
        required: true
        description: The CMT name
        example: "CMT Lagos"
    security:
      - Bearer: []
    responses:
      200:
        description: CMT performance data retrieved successfully
        schema:
          type: object
          properties:
            cmt_name:
              type: string
            total_case_managers:
              type: integer
            total_tx_cur:
              type: integer
            total_iit:
              type: integer
            total_transferred_out:
              type: integer
            total_dead:
              type: integer
            total_discontinued:
              type: integer
            total_appointments_completed:
              type: integer
            total_appointments_scheduled:
              type: integer
            total_vl_suppressed:
              type: integer
            total_vl_samples:
              type: integer
            total_vl_results:
              type: integer
            total_vl_eligible:
              type: integer
            average_score:
              type: number
              format: float
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: CMT not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "CMT not found"
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = PerformanceService.get_single_cmt_performance(cmt_name, current_user)
    if performance_data:
        return jsonify(performance_data), 200
    return jsonify({'message': 'CMT not found'}), 404

