from . import ma
from app.models import User, Roles

class RoleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Roles
    
    id = ma.auto_field()
    role_name = ma.auto_field()

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    fullname = ma.auto_field()
    email = ma.auto_field()
    state_id = ma.auto_field()
    facility_id = ma.auto_field()
    is_active = ma.auto_field()
    roles = ma.Method('get_roles')

    def get_roles(self, obj):
        user_roles = [ur.role_id for ur in obj.user_roles]
        roles = Roles.query.filter(Roles.id.in_(user_roles)).all()
        return [role.role_name for role in roles]

user_schema = UserSchema()
users_schema = UserSchema(many=True)
