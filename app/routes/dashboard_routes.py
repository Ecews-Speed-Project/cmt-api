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
    """
    Get dashboard statistics
    ---
    tags:
      - Dashboard
    parameters:
      - name: start
        in: query
        type: string
        format: date
        description: Start date for statistics period (YYYY-MM-DD)
        example: "2024-01-01"
      - name: end
        in: query
        type: string
        format: date
        description: End date for statistics period (YYYY-MM-DD)
        example: "2024-12-31"
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard statistics retrieved successfully
        schema:
          type: object
          properties:
            total_patients:
              type: integer
            total_case_managers:
              type: integer
            total_cmts:
              type: integer
            total_facilities:
              type: integer
            appointment_completion_rate:
              type: number
              format: float
            viral_load_suppression_rate:
              type: number
              format: float
            average_performance_score:
              type: number
              format: float
      400:
        description: Bad request - invalid date range
      401:
        description: Unauthorized - invalid or missing token
    """
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    current_user = UserService.get_user_by_id(get_jwt_identity())
    print(current_user)
    stats = DashboardService.get_stats(start_date, end_date, current_user)
    return jsonify(stats)


@bp.route('/top3-cmts', methods=['GET'])
@jwt_required()
def get_top_cmt():
    """
    Get top 3 performing CMTs
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Top 3 CMTs retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              cmt_name:
                type: string
              total_case_managers:
                type: integer
              total_tx_cur:
                type: integer
              total_iit:
                type: integer
              total_transferred_out:
                type: integer
              total_dead:
                type: integer
              total_discontinued:
                type: integer
              total_appointments_completed:
                type: integer
              total_appointments_scheduled:
                type: integer
              total_vl_suppressed:
                type: integer
              total_vl_samples:
                type: integer
              total_vl_results:
                type: integer
              total_vl_eligible:
                type: integer
              average_score:
                type: number
                format: float
      401:
        description: Unauthorized - invalid or missing token
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = DashboardService.get_top_cmts(current_user)
    return jsonify(performance_data), 200


@bp.route('/top3-case-managers', methods=['GET'])
@jwt_required()
def get_top3_case_managers():
    """
    Get top 3 performing case managers
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Top 3 case managers retrieved successfully
        schema:
          type: array
          items:
            type: object
            properties:
              case_manager_id:
                type: string
              fullname:
                type: string
              tx_cur:
                type: integer
              iit:
                type: integer
              transferred_out:
                type: integer
              dead:
                type: integer
              discontinued:
                type: integer
              appointments_completed:
                type: integer
              appointments_schedule:
                type: integer
              viral_load_suppressed:
                type: integer
              viral_load_samples:
                type: integer
              viral_load_results:
                type: integer
              viral_load_eligible:
                type: integer
              final_score:
                type: number
                format: float
      401:
        description: Unauthorized - invalid or missing token
    """
    current_user = UserService.get_user_by_id(get_jwt_identity())
    performance_data = DashboardService.get_top_case_managers(current_user)
    # schema_data = performance_schema.dump(performance_data)
    # top_cmt = sorted(schema_data, key=lambda x: x['final_score'], reverse=True)[:3]
    return jsonify(performance_data), 200


@bp.route('/appointment-trends', methods=['GET'])
@jwt_required()
def get_trends():
    """
    Get appointment trends data
    ---
    tags:
      - Dashboard
    parameters:
      - name: start
        in: query
        type: string
        format: date
        description: Start date for trends period (YYYY-MM-DD)
        example: "2024-01-01"
      - name: end
        in: query
        type: string
        format: date
        description: End date for trends period (YYYY-MM-DD)
        example: "2024-12-31"
    security:
      - Bearer: []
    responses:
      200:
        description: Appointment trends retrieved successfully
        schema:
          type: object
          properties:
            monthly_trends:
              type: array
              items:
                type: object
                properties:
                  month:
                    type: string
                  completed:
                    type: integer
                  scheduled:
                    type: integer
                  completion_rate:
                    type: number
                    format: float
            weekly_trends:
              type: array
              items:
                type: object
                properties:
                  week:
                    type: string
                  completed:
                    type: integer
                  scheduled:
                    type: integer
                  completion_rate:
                    type: number
                    format: float
      401:
        description: Unauthorized - invalid or missing token
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
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
