from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import func
from app.services import DashboardService, UserService,PerformanceService
from app.schemas.performance_schema import performance_schema
from app.models import User
from app.utils.validators import validate_date_range


bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
@jwt_required()
@validate_date_range
def get_dashboard_stats():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    current_user = UserService.get_user_by_id(get_jwt_identity())
    print(current_user)
    stats = DashboardService.get_stats(start_date, end_date, current_user)
    return jsonify(stats)


@bp.route('/top3-cmts', methods=['GET'])
@jwt_required()
def get_top_cmt():
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = DashboardService.get_top_cmts(current_user)
    return jsonify(performance_data), 200


@bp.route('/top3-case-managers', methods=['GET'])
@jwt_required()
def get_top3_case_managers():
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = DashboardService.get_top_case_managers(current_user)
    # schema_data = performance_schema.dump(performance_data)
    # top_cmt = sorted(schema_data, key=lambda x: x['final_score'], reverse=True)[:3]
    return jsonify(performance_data), 200


@bp.route('/appointment-trends', methods=['GET'])
@jwt_required()
def get_trends():
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        # Convert dates only if both parameters are provided
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            start_date = None
            end_date = None
        
        current_user = UserService.get_user_by_id(get_jwt_identity())
        trends = DashboardService.get_trends(start_date, end_date, current_user)
        return jsonify(trends)
    except Exception as e:
        print(f"Error in get_trends: {str(e)}")
        return jsonify({"error": str(e)}), 500
