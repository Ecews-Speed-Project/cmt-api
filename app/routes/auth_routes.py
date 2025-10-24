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
    """
    User login endpoint
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              description: User email address
              example: "user@example.com"
            password:
              type: string
              description: User password
              example: "password123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: JWT access token
            user:
              type: object
              properties:
                id:
                  type: integer
                email:
                  type: string
                fullname:
                  type: string
      400:
        description: Bad request - missing email or password
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Email and password are required"
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid credentials"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
            err_str:
              type: string
    """
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password are required"}), 400

        auth_result = user_service.authenticate(data)
        if auth_result:
            return jsonify(auth_result), 200
            
        return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "An error occurred during login", "err_str": str(e)}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    User logout endpoint
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Successfully logged out"
      401:
        description: Unauthorized - invalid or missing token
    """
    # Token invalidation logic here
    return jsonify({"message": "Successfully logged out"}), 200

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh JWT token endpoint
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Token refreshed successfully
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: New JWT access token
      401:
        description: Unauthorized - invalid or missing refresh token
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
