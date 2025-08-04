from flask_restx import Api, Resource, fields
from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create the main API blueprint
swagger_bp = Blueprint('swagger', __name__, url_prefix='/api')

# Initialize the API with Swagger documentation
api = Api(
    swagger_bp,
    title='CMT API',
    version='1.0',
    description='A comprehensive API for Case Management Team (CMT) operations',
    doc='/docs',
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type 'Bearer <JWT>' where JWT is the token"
        }
    },
    security='apikey'
)

# Define common response models
error_model = api.model('Error', {
    'error': fields.String(required=True, description='Error message'),
    'err_str': fields.String(description='Detailed error string')
})

success_model = api.model('Success', {
    'message': fields.String(required=True, description='Success message')
})

# Define common request/response fields
user_fields = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(required=True, description='User email'),
    'fullname': fields.String(description='User full name'),
    'roles': fields.List(fields.String, description='User roles'),
    'state_id': fields.Integer(description='User state ID'),
    'created_at': fields.DateTime(description='User creation date')
})

login_request = api.model('LoginRequest', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

login_response = api.model('LoginResponse', {
    'access_token': fields.String(description='JWT access token'),
    'refresh_token': fields.String(description='JWT refresh token'),
    'user': fields.Nested(user_fields, description='User information')
})

cmt_fields = api.model('CMT', {
    'id': fields.Integer(description='CMT ID'),
    'name': fields.String(required=True, description='CMT name'),
    'state': fields.String(required=True, description='CMT state'),
    'facility_name': fields.String(required=True, description='Facility name'),
    'case_managers': fields.List(fields.Raw, description='List of case managers'),
    'patient_count': fields.Integer(description='Total patient count'),
    'created_at': fields.DateTime(description='CMT creation date')
})

cmt_create_request = api.model('CMTCreateRequest', {
    'name': fields.String(required=True, description='CMT name'),
    'state': fields.String(required=True, description='CMT state'),
    'facility_name': fields.String(required=True, description='Facility name')
})

case_manager_fields = api.model('CaseManager', {
    'id': fields.Integer(description='Case Manager ID'),
    'fullname': fields.String(required=True, description='Full name'),
    'role': fields.String(description='Role'),
    'state': fields.String(description='State'),
    'facilities': fields.String(description='Facilities'),
    'cmt': fields.String(description='CMT name'),
    'created_at': fields.DateTime(description='Creation date')
})

patient_fields = api.model('Patient', {
    'id': fields.Integer(description='Patient ID'),
    'pepid': fields.String(description='Patient PEP ID'),
    'fullname': fields.String(description='Patient full name'),
    'case_manager_id': fields.Integer(description='Case Manager ID'),
    'created_at': fields.DateTime(description='Creation date')
})

facility_fields = api.model('Facility', {
    'id': fields.Integer(description='Facility ID'),
    'name': fields.String(required=True, description='Facility name'),
    'state': fields.String(description='State'),
    'created_at': fields.DateTime(description='Creation date')
})

performance_fields = api.model('Performance', {
    'id': fields.Integer(description='Performance ID'),
    'CaseManagerID': fields.Integer(description='Case Manager ID'),
    'tx_cur': fields.Integer(description='Current treatment'),
    'iit': fields.Integer(description='Interruption in treatment'),
    'transferred_out': fields.Integer(description='Transferred out'),
    'dead': fields.Integer(description='Deceased'),
    'discontinued': fields.Integer(description='Discontinued'),
    'appointments_completed': fields.Integer(description='Completed appointments'),
    'appointments_schedule': fields.Integer(description='Scheduled appointments'),
    'viral_load_suppressed': fields.Integer(description='Viral load suppressed'),
    'viral_load_samples': fields.Integer(description='Viral load samples'),
    'viral_load_results': fields.Integer(description='Viral load results'),
    'viral_load_eligible': fields.Integer(description='Viral load eligible'),
    'final_score': fields.Float(description='Final performance score'),
    'created_at': fields.DateTime(description='Creation date')
})

# Define namespaces for different API sections
auth_ns = api.namespace('auth', description='Authentication operations')
cmt_ns = api.namespace('cmt', description='CMT operations')
case_manager_ns = api.namespace('case-managers', description='Case Manager operations')
patient_ns = api.namespace('patients', description='Patient operations')
facility_ns = api.namespace('facilities', description='Facility operations')
performance_ns = api.namespace('performance', description='Performance operations')
user_ns = api.namespace('users', description='User operations')
dashboard_ns = api.namespace('dashboard', description='Dashboard operations')
report_ns = api.namespace('reports', description='Report operations') 