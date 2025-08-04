from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import CMTService, UserService
from app.utils.rbac import role_required
from app.schemas.cmt_schema import cmt_schema, cmts_schema

bp = Blueprint('cmt', __name__, url_prefix='/api/cmt')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_cmts():
    """
    Get all CMTs with case managers and patient counts
    ---
    tags:
      - CMT
    security:
      - Bearer: []
    responses:
      200:
        description: List of CMTs retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              state:
                type: string
              facility_name:
                type: string
              case_managers:
                type: array
                items:
                  type: object
              patient_count:
                type: integer
      401:
        description: Unauthorized - invalid or missing token
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    cmts = CMTService.get_all_cmt(current_user)
    return jsonify(cmts)

@bp.route('/<int:cmt_id>', methods=['GET'])
@jwt_required()
def get_cmt_performance(cmt_id):
    """
    Get a single CMT with performance metrics
    ---
    tags:
      - CMT
    parameters:
      - name: cmt_id
        in: path
        type: integer
        required: true
        description: The CMT identifier
    security:
      - Bearer: []
    responses:
      200:
        description: CMT details retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            state:
              type: string
            facility_name:
              type: string
            case_managers:
              type: array
            patient_count:
              type: integer
            performance:
              type: object
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: CMT not found
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    
    cmt = CMTService.get_single_cmt(cmt_id, current_user)
    return jsonify(cmt), 200


@bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['super_admin'])
def create_cmt():
    """
    Create a new CMT
    ---
    tags:
      - CMT
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - state
            - facility_name
          properties:
            name:
              type: string
              description: CMT name
              example: "CMT Lagos"
            state:
              type: string
              description: CMT state
              example: "Lagos"
            facility_name:
              type: string
              description: Facility name
              example: "General Hospital Lagos"
    responses:
      201:
        description: CMT created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            state:
              type: string
            facility_name:
              type: string
      400:
        description: Bad request - invalid data
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Unauthorized - invalid or missing token
      403:
        description: Forbidden - insufficient permissions
    """
    data = request.get_json()
    try:
        cmt = CMTService.create_cmt(data)
        return jsonify(cmt_schema.dump(cmt)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
