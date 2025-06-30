from flask_jwt_extended import create_access_token
from app.models import User, Roles
from app.schemas.user_schema import user_schema, users_schema
from app.extensions import db
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_users():
        users = User.query.filter(User.active > 0).all()
        return users_schema.dump(users)

    @staticmethod
    def create_user(data):
        try:
            user = User(
                email=data['email'],
                fullname=data.get('fullname'),
                role=data.get('role'),  # This maps to Cadre in the DB
                state=data.get('state'),
                facilities=data.get('facilities'),
                active=1
            )
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            return user_schema.dump(user)
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def authenticate(data):
        try:
            user = User.query.filter_by(email=data['email']).first()
            
            # if user and user.check_password(data['password']):
                # Convert user.id to string for JWT
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(days=1)  # Optional: Set token expiration
                )
            user_data = user_schema.dump(user)
            return {
                    'access_token': access_token,
                    'user': user_data
                }
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def get_user_by_id(user_id):
        try:
            user = User.query.get(int(user_id))
            if user:
                # Get role names through user_roles relationship
                roles = [role.role_name for role in Roles.query.filter(
                    Roles.id.in_([ur.role_id for ur in user.user_roles])
                ).all()]
                
                return {
                    'user_id': user.id,
                    'roles': roles,  # Now returning array of role names
                    'facility_id': user.facility_id,
                    'state_id': user.state_id
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching user by ID: {str(e)}", exc_info=True)
            return None
