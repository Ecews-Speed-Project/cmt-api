from flask import Flask
import logging
from logging.config import dictConfig
from sqlalchemy import text
from .config import Config
from .extensions import db, jwt, ma, cors

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

logger = logging.getLogger(__name__)

def test_db_connection(app):
    try:
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            logger.info('Successfully connected to the database!')
    except Exception as e:
        logger.error(f'Database connection failed! Error: {str(e)}')
        raise

def create_app(config_class=Config):
    app = Flask(__name__)
    try:
        app.config.from_object(Config)
        logger.info('Configuration loaded successfully')
    except Exception as e:
        logger.error(f'Failed to load configuration: {str(e)}')
        raise

    from app.models.appointments import DrugPickup, ViralLoad
    from app.models.cmt import CMT
    from app.models.user import User, Roles, UserRoles
    from app.models.patient import Patient
    from app.models.facility import Facility, State
    from app.models.case_manager import CaseManager
    from app.models.performance import CaseManagerPerformance

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5001", 'http://eboard.ecews.org:5001']  # Replace with your frontend's origin
            }
        }
    )
 
    ma.init_app(app)

    # Test database connection (non-blocking)
    try:
        test_db_connection(app)
    except Exception as e:
        logger.warning(f'Initial database connection test failed, but continuing: {str(e)}')
    
    with app.app_context():
        from app.jobs.scheduler import flask_scheduler
        scheduler = flask_scheduler.init_scheduler(app)
        

    # Import and register blueprints
    from .routes import (
        auth_bp, user_bp, cmt_bp, case_manager_bp, 
        patient_bp, dashboard_bp, report_bp, home_bp, 
        facility_bp, performance_bp
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cmt_bp)
    app.register_blueprint(case_manager_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(facility_bp)
    app.register_blueprint(performance_bp)
    logger.info('Blueprints registered successfully')

    # Register error handlers
    from .utils import register_error_handlers
    register_error_handlers(app)

    # Register CLI commands
    from app.cli.commands import register_commands
    register_commands(app)
    
    # Setup Swagger documentation (non-intrusive)
    try:
        from .swagger_setup import setup_swagger
        setup_swagger(app)
        logger.info('Swagger documentation setup successfully')
    except Exception as e:
        logger.warning(f'Swagger setup failed, but continuing: {str(e)}')
    
    return app
