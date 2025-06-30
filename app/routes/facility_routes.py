from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services import FacilityService
from app.utils.rbac import role_required

bp = Blueprint('facility', __name__, url_prefix='/api/facilities')

@bp.route('/', methods=['GET'])
#@jwt_required()
def get_facilities():
    state_id = request.args.get('state_id')
    facilities = FacilityService.get_facilities(state_id)
    return jsonify(facilities)

@bp.route('/states', methods=['GET'])
#@jwt_required()
def get_states():
    states = FacilityService.get_states()
    return jsonify(states)

@bp.route('/datim/<datim_code>', methods=['GET'])
@jwt_required()
def get_facility_by_datim(datim_code):
    facility = FacilityService.get_facility_by_datim(datim_code)
    if not facility:
        return jsonify({"error": "Facility not found"}), 404
    return jsonify(facility)
