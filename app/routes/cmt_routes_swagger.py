from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import CMTService, UserService
from app.utils.rbac import role_required
from app.schemas.cmt_schema import cmt_schema, cmts_schema
from app.swagger_config import cmt_ns, cmt_fields, cmt_create_request, error_model
from flask_restx import Resource
import logging

logger = logging.getLogger(__name__)

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
            return cmt_schema.dump(cmt), 201
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