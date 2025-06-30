from flask import Blueprint, jsonify

bp = Blueprint('/api/', __name__)

@bp.route('/')
def home():
    
    return jsonify(message="Welcome to the SPEED CMS API!"), 200