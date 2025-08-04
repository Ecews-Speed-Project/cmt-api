from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services import UserService
from app.utils.rbac import role_required

bp = Blueprint('user', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['super_admin'])
def get_users():
    """
    Get all users (super admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
    responses:
      200:
        description: List of users retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              email:
                type: string
              fullname:
                type: string
              role:
                type: string
              state:
                type: string
              facilities:
                type: string
              active:
                type: integer
              created_at:
                type: string
                format: date-time
      401:
        description: Unauthorized - invalid or missing token
      403:
        description: Forbidden - insufficient permissions
    """
    users = UserService.get_users()
    return jsonify(users)

@bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['super_admin'])
def create_user():
    """
    Create a new user (super admin only)
    ---
    tags:
      - Users
    security:
      - Bearer: []
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
            fullname:
              type: string
              description: User full name
              example: "John Doe"
            role:
              type: string
              description: User role
              example: "case_manager"
            state:
              type: string
              description: User state
              example: "Lagos"
            facilities:
              type: string
              description: User facilities
              example: "General Hospital Lagos"
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            email:
              type: string
            fullname:
              type: string
            role:
              type: string
            state:
              type: string
            facilities:
              type: string
            active:
              type: integer
            created_at:
              type: string
              format: date-time
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
        user = UserService.create_user(data)
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required(['super_admin'])
def update_user(user_id):
    """
    Update a user (super admin only)
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The user identifier
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              description: User email address
              example: "user@example.com"
            fullname:
              type: string
              description: User full name
              example: "John Doe"
            role:
              type: string
              description: User role
              example: "case_manager"
            state:
              type: string
              description: User state
              example: "Lagos"
            facilities:
              type: string
              description: User facilities
              example: "General Hospital Lagos"
    responses:
      200:
        description: User updated successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            email:
              type: string
            fullname:
              type: string
            role:
              type: string
            state:
              type: string
            facilities:
              type: string
            active:
              type: integer
            created_at:
              type: string
              format: date-time
      401:
        description: Unauthorized - invalid or missing token
      403:
        description: Forbidden - insufficient permissions
      404:
        description: User not found
    """
    data = request.get_json()
    user = UserService.update_user(user_id, data)
    return jsonify(user)

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(['super_admin'])
def deactivate_user(user_id):
    """
    Deactivate a user (super admin only)
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The user identifier
    security:
      - Bearer: []
    responses:
      200:
        description: User deactivated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User deactivated successfully"
      401:
        description: Unauthorized - invalid or missing token
      403:
        description: Forbidden - insufficient permissions
      404:
        description: User not found
    """
    UserService.deactivate_user(user_id)
    return jsonify({"message": "User deactivated successfully"})
