from app.routes.auth_routes import bp as auth_bp
from app.routes.user_routes import bp as user_bp
from app.routes.cmt_routes import bp as cmt_bp
from app.routes.case_manager_routes import bp as case_manager_bp
from app.routes.patient_routes import bp as patient_bp
from app.routes.dashboard_routes import bp as dashboard_bp
from app.routes.report_routes import bp as report_bp
from app.routes.home import bp as home_bp
from app.routes.facility_routes import bp as facility_bp
from app.routes.performance_routes import bp as performance_bp

__all__ = [
    'auth_bp',
    'user_bp', 
    'cmt_bp',
    'case_manager_bp',
    'patient_bp',
    'dashboard_bp',
    'report_bp',
    'home_bp',
    'facility_bp',
    'performance_bp'
]
