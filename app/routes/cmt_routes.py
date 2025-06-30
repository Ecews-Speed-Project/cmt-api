from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import CMTService, UserService
from app.utils.rbac import role_required
from app.schemas.cmt_schema import cmt_schema, cmts_schema

bp = Blueprint('cmt', __name__, url_prefix='/api/cmt')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_cmts():
    current_user = UserService.get_user_by_id(get_jwt_identity())
    cmts = CMTService.get_all_cmt(current_user)
    return jsonify(cmts)

@bp.route('/<int:cmt_id>', methods=['GET'])
@jwt_required()
def get_cmt_performance(cmt_id):
    current_user = UserService.get_user_by_id(get_jwt_identity())
    
    cmt = CMTService.get_single_cmt(cmt_id, current_user)
    return jsonify(cmt), 200


@bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['super_admin'])
def create_cmt():
    data = request.get_json()
    try:
        cmt = CMTService.create_cmt(data)
        return jsonify(cmt_schema.dump(cmt)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
