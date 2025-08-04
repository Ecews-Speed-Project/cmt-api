from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.services import UserService, CMTService
from app.utils.rbac import role_required
from app.swagger_config import (
    auth_ns, cmt_ns, login_request, login_response, success_model, error_model,
    cmt_fields, cmt_create_request
)
from flask_restx import Resource
import logging

logger = logging.getLogger(__name__)

# Authentication endpoints
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_request)
    @auth_ns.response(200, 'Login successful', login_response)
    @auth_ns.response(400, 'Bad request', error_model)
    @auth_ns.response(401, 'Invalid credentials', error_model)
    @auth_ns.response(500, 'Internal server error', error_model)
    def post(self):
        """Authenticate user and return JWT tokens"""
        try:
            data = request.get_json()
            if not data or 'email' not in data or 'password' not in data:
                return {"error": "Email and password are required"}, 400

            auth_result = UserService().authenticate(data)
            if auth_result:
                return auth_result, 200
                
            return {"error": "Invalid credentials"}, 401
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {"error": "An error occurred during login", "err_str": str(e)}, 500

@auth_ns.route('/logout')
class Logout(Resource):
    @auth_ns.doc(security='apikey')
    @auth_ns.response(200, 'Logout successful', success_model)
    @jwt_required()
    def post(self):
        """Logout user and invalidate JWT token"""
        return {"message": "Successfully logged out"}, 200

@auth_ns.route('/refresh')
class Refresh(Resource):
    @auth_ns.doc(security='apikey')
    @auth_ns.response(200, 'Token refreshed successfully', {'access_token': 'string'})
    @jwt_required(refresh=True)
    def post(self):
        """Refresh JWT access token using refresh token"""
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return {"access_token": access_token}, 200

# CMT endpoints
@cmt_ns.route('/')
class CMTList(Resource):
    @cmt_ns.doc(security='apikey')
    @cmt_ns.response(200, 'Success', [cmt_fields])
    @cmt_ns.response(401, 'Unauthorized', error_model)
    @jwt_required()
    def get(self):
        """Get all CMTs with case managers and patient counts"""
        current_user = UserService.get_user_by_id(get_jwt_identity())
        cmts = CMTService.get_all_cmt(current_user)
        return cmts

    @cmt_ns.doc(security='apikey')
    @cmt_ns.expect(cmt_create_request)
    @cmt_ns.response(201, 'CMT created successfully', cmt_fields)
    @cmt_ns.response(400, 'Bad request', error_model)
    @cmt_ns.response(401, 'Unauthorized', error_model)
    @jwt_required()
    @role_required(['super_admin'])
    def post(self):
        """Create a new CMT"""
        data = request.get_json()
        try:
            cmt = CMTService.create_cmt(data)
            return cmt, 201
        except ValueError as e:
            return {"error": str(e)}, 400

@cmt_ns.route('/<int:cmt_id>')
@cmt_ns.param('cmt_id', 'The CMT identifier')
class CMTSingle(Resource):
    @cmt_ns.doc(security='apikey')
    @cmt_ns.response(200, 'Success', cmt_fields)
    @cmt_ns.response(401, 'Unauthorized', error_model)
    @cmt_ns.response(404, 'CMT not found', error_model)
    @jwt_required()
    def get(self, cmt_id):
        """Get a single CMT with performance metrics"""
        current_user = UserService.get_user_by_id(get_jwt_identity())
        
        cmt = CMTService.get_single_cmt(cmt_id, current_user)
        if not cmt:
            return {"error": "CMT not found"}, 404
        return cmt, 200 