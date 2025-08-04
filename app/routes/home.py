from flask import Blueprint, jsonify
from app.swagger_config import api

bp = Blueprint('home', __name__)

@bp.route('/')
def home():
    return jsonify({
        "message": "CMT API is running",
        "version": "1.0",
        "documentation": "/api/docs"
    })

@bp.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "message": "API is operational"
    })