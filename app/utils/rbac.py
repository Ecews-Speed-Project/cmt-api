from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models import User

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role not in allowed_roles:
                return jsonify({"error": "Unauthorized access"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def facility_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "Unauthorized access"}), 403
            
        facility_id = kwargs.get('facility_id')
        if user.role != 'super_admin' and user.facility_id != facility_id:
            return jsonify({"error": "Access denied to this facility"}), 403
        return f(*args, **kwargs)
    return decorated_function
