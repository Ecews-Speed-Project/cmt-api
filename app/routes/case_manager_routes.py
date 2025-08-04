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
    """
    Get all case managers
    ---
    tags:
      - Case Managers
    security:
      - Bearer: []
    responses:
      200:
        description: List of case managers retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              fullname:
                type: string
              role:
                type: string
              state:
                type: string
              facilities:
                type: string
              cmt:
                type: string
              created_at:
                type: string
                format: date-time
      401:
        description: Unauthorized - invalid or missing token
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    case_managers = CaseManagerService.get_all_case_managers(current_user)
    return jsonify(case_managers)

@bp.route('/<int:cm_id>/patients', methods=['GET'])
@jwt_required()
def get_case_manager_patients(cm_id):
    """
    Get patients managed by a specific case manager
    ---
    tags:
      - Case Managers
    parameters:
      - name: cm_id
        in: path
        type: integer
        required: true
        description: The case manager identifier
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
      404:
        description: Case manager not found
    """
    patients = CaseManagerService.get_patients(cm_id)
    return jsonify(patients_schema.dump(patients))

@bp.route('/<int:cm_id>/performance', methods=['GET'])
@jwt_required()
@validate_date_range
def get_case_manager_performance(cm_id):
    """
    Get performance metrics for a specific case manager
    ---
    tags:
      - Case Managers
    parameters:
      - name: cm_id
        in: path
        type: integer
        required: true
        description: The case manager identifier
      - name: start
        in: query
        type: string
        format: date
        description: Start date for performance period (YYYY-MM-DD)
        example: "2024-01-01"
      - name: end
        in: query
        type: string
        format: date
        description: End date for performance period (YYYY-MM-DD)
        example: "2024-12-31"
    security:
      - Bearer: []
    responses:
      200:
        description: Performance metrics retrieved successfully
        schema:
          type: object
          properties:
            tx_cur:
              type: integer
              description: Current treatment count
            iit:
              type: integer
              description: Interruption in treatment count
            transferred_out:
              type: integer
              description: Transferred out count
            dead:
              type: integer
              description: Deceased count
            discontinued:
              type: integer
              description: Discontinued count
            appointments_completed:
              type: integer
              description: Completed appointments count
            appointments_schedule:
              type: integer
              description: Scheduled appointments count
            viral_load_suppressed:
              type: integer
              description: Viral load suppressed count
            viral_load_samples:
              type: integer
              description: Viral load samples count
            viral_load_results:
              type: integer
              description: Viral load results count
            viral_load_eligible:
              type: integer
              description: Viral load eligible count
            final_score:
              type: number
              format: float
              description: Final performance score
      400:
        description: Bad request - invalid date range
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Case manager not found
    """
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    metrics = CaseManagerService.get_performance(cm_id, start_date, end_date)
    return jsonify(metrics)

@bp.route('/<int:cm_id>', methods=['PUT'])
@jwt_required()
@role_required(['super_admin', 'facility_backstop'])
def update_case_manager(cm_id):
    """
    Update a case manager's information
    ---
    tags:
      - Case Managers
    parameters:
      - name: cm_id
        in: path
        type: integer
        required: true
        description: The case manager identifier
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            fullname:
              type: string
              description: Full name of the case manager
              example: "John Doe"
            role:
              type: string
              description: Role of the case manager
              example: "Case Manager"
            state:
              type: string
              description: State where the case manager works
              example: "Lagos"
            facilities:
              type: string
              description: Facilities assigned to the case manager
              example: "General Hospital Lagos"
            cmt:
              type: string
              description: CMT assignment
              example: "CMT Lagos"
    security:
      - Bearer: []
    responses:
      200:
        description: Case manager updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            fullname:
              type: string
            role:
              type: string
            state:
              type: string
            facilities:
              type: string
            cmt:
              type: string
            created_at:
              type: string
              format: date-time
      400:
        description: Bad request - invalid data
      401:
        description: Unauthorized - invalid or missing token
      403:
        description: Forbidden - insufficient permissions
      404:
        description: Case manager not found
    """
    data = request.get_json()
    updated = CaseManagerService.update_case_manager(cm_id, data)
    return jsonify(case_manager_schema.dump(updated))

@bp.route('/<int:case_manager_id>', methods=['GET'])
@jwt_required()
def get_case_manager(case_manager_id):
    """
    Get a specific case manager by ID
    ---
    tags:
      - Case Managers
    parameters:
      - name: case_manager_id
        in: path
        type: integer
        required: true
        description: The case manager identifier
    security:
      - Bearer: []
    responses:
      200:
        description: Case manager details retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            fullname:
              type: string
            role:
              type: string
            state:
              type: string
            facilities:
              type: string
            cmt:
              type: string
            created_at:
              type: string
              format: date-time
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Case manager not found or access denied
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Case manager not found or access denied"
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    case_manager = CaseManagerService.get_case_manager(case_manager_id, current_user)
    if case_manager:
        return jsonify(case_manager), 200
    return jsonify({'message': 'Case manager not found or access denied'}), 404
