from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'Users'
    __table_args__ = {'schema': 'user'}
    
    id = db.Column("Id", db.Integer, primary_key=True)
    fullname = db.Column("FullName", db.String(200))
    email = db.Column("Email", db.String(120), unique=True, nullable=False)
    password_hash = db.Column("PasswordHash", db.String(128))
    role = db.Column("Cadre", db.String(20), nullable=False)
    state_id = db.Column("State", db.Integer, db.ForeignKey('dbo.State.StateId'), nullable=True)
    facility_id = db.Column("FacilityIds", db.Integer, db.ForeignKey('dbo.Facilities.FacilityId'), nullable=True)
    is_active = db.Column("Active", db.Integer)
    
    user_roles = db.relationship('UserRoles', 
                               primaryjoin="User.id==UserRoles.user_id",
                               lazy='joined')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Roles(db.Model):
     __tablename__ = 'Roles'
     __table_args__ = {'schema': 'user'}
    
     id = db.Column("Id", db.Integer, primary_key=True)
     role_name = db.Column("Name", db.String(200))


class UserRoles(db.Model):
    __tablename__ = 'UserRoles'
    __table_args__ = (
        db.PrimaryKeyConstraint('RoleId', 'UserId', name='pk_user_roles'),
        {'schema': 'user'}
    )
    
    role_id = db.Column("RoleId", db.Integer, db.ForeignKey('user.Roles.Id'), nullable=False)
    user_id = db.Column("UserId", db.Integer, db.ForeignKey('user.Users.Id'), nullable=False)