from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services import UserService
from app.extensions import db
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('auth', __name__, url_prefix='/api/auth')
user_service = UserService()

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password are required"}), 400

        auth_result = user_service.authenticate(data)
        if auth_result:
            return jsonify(auth_result), 200
            
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "An error occurred during login", "err_str": str(e)}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Token invalidation logic here
    return jsonify({"message": "Successfully logged out"}), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
