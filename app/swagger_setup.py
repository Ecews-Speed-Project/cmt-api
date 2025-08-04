from flasgger import Swagger
from flask import jsonify

def setup_swagger(app):
    """Setup Swagger documentation for the Flask app"""
    
    # Swagger configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/api/apispec_1.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/api/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    # Swagger template
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "CMT API",
            "description": "A comprehensive API for Case Management Team (CMT) operations",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@example.com"
            }
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ],
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ]
    }
    
    # Initialize Swagger
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Add a simple health check endpoint for testing
    @app.route('/api/health')
    def health_check():
        """
        Health check endpoint
        ---
        tags:
          - Health
        responses:
          200:
            description: API is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "healthy"
                message:
                  type: string
                  example: "API is operational"
        """
        return jsonify({
            "status": "healthy",
            "message": "API is operational"
        })
    
    return swagger 