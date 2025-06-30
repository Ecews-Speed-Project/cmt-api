from datetime import datetime
from functools import wraps
from flask import request, jsonify

def validate_date_range(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        # Skip validation if dates aren't provided
        if not start_date or not end_date:
            return f(*args, **kwargs)
            
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if end < start:
                return jsonify({"error": "End date must be after start date"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            
        return f(*args, **kwargs)
    return decorated_function
