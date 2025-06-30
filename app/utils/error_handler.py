from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        logger.error(f'Database error occurred: {str(error)}')
        return jsonify({"error": "Database error occurred"}), 500

    @app.errorhandler(Exception)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
