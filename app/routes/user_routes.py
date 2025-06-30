from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services import UserService
from app.utils.rbac import role_required

bp = Blueprint('user', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['super_admin'])
def get_users():
    users = UserService.get_users()
    return jsonify(users)

@bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['super_admin'])
def create_user():
    data = request.get_json()
    try:
        user = UserService.create_user(data)
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required(['super_admin'])
def update_user(user_id):
    data = request.get_json()
    user = UserService.update_user(user_id, data)
    return jsonify(user)

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin'])
def deactivate_user(user_id):
    UserService.deactivate_user(user_id)
    return jsonify({"message": "User deactivated successfully"})
