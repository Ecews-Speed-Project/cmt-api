from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services import FacilityService
from app.utils.rbac import role_required

bp = Blueprint('facility', __name__, url_prefix='/api/facilities')

@bp.route('/', methods=['GET'])
#@jwt_required()
def get_facilities():
    """
    Get all facilities, optionally filtered by state
    ---
    tags:
      - Facilities
    parameters:
      - name: state_id
        in: query
        type: integer
        description: State ID to filter facilities by
        example: 1
    responses:
      200:
        description: List of facilities retrieved successfully
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
              datim_code:
                type: string
              created_at:
                type: string
                format: date-time
    """
    state_id = request.args.get('state_id')
    facilities = FacilityService.get_facilities(state_id)
    return jsonify(facilities)

@bp.route('/states', methods=['GET'])
#@jwt_required()
def get_states():
    """
    Get all states
    ---
    tags:
      - Facilities
    responses:
      200:
        description: List of states retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              created_at:
                type: string
                format: date-time
    """
    states = FacilityService.get_states()
    return jsonify(states)

@bp.route('/datim/<datim_code>', methods=['GET'])
@jwt_required()
def get_facility_by_datim(datim_code):
    """
    Get facility information by DATIM code
    ---
    tags:
      - Facilities
    parameters:
      - name: datim_code
        in: path
        type: string
        required: true
        description: The DATIM code of the facility
        example: "12345"
    security:
      - Bearer: []
    responses:
      200:
        description: Facility information retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            state:
              type: string
            datim_code:
              type: string
            created_at:
              type: string
              format: date-time
      401:
        description: Unauthorized - invalid or missing token
      404:
        description: Facility not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Facility not found"
    """
    facility = FacilityService.get_facility_by_datim(datim_code)
    if not facility:
        return jsonify({"error": "Facility not found"}), 404
    return jsonify(facility)
