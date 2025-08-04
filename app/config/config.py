import os
from datetime import timedelta

class Config:
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    DEBUG = os.environ.get('DEBUG', False)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_timeout": 60,
        "max_overflow": 10,
        "connect_args": {
            "timeout": 60
        }
    }
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES')
    JWT_REFRESH_TOKEN_EXPIRES = os.environ.get('JWT_REFRESH_TOKEN_EXPIRES')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS')

    def __init__(self):
        self.SECRET_KEY = self.SECRET_KEY or 'dev-secret-key'
        self.SQLALCHEMY_DATABASE_URI = self.SQLALCHEMY_DATABASE_URI or os.environ.get('DATABASE_URL')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = self.SQLALCHEMY_TRACK_MODIFICATIONS or False
        self.JWT_SECRET_KEY = self.JWT_SECRET_KEY or 'jwt-secret-key'
        self.JWT_ACCESS_TOKEN_EXPIRES = self.JWT_ACCESS_TOKEN_EXPIRES or timedelta(hours=1)
        self.JWT_REFRESH_TOKEN_EXPIRES = self.JWT_REFRESH_TOKEN_EXPIRES or timedelta(days=30)
