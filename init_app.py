from app import db
from app.general.security.models import User, Role
from config import AUTH_ROLE_ADMIN, AUTH_ROLE_PUBLIC

print "--------------------------"
print "     CREATE DB"
print "--------------------------"
db.create_all()
print "--------------------------"
print " CREATE USER and  ROLES"
print "--------------------------"
role_admin = Role()
role_admin.name = AUTH_ROLE_ADMIN
role_public = Role()
role_public.name = AUTH_ROLE_PUBLIC
user = User()
user.first_name = 'Admin'
user.last_name = ''
user.username = 'admin'
user.password = 'general'
user.active = True
user.role = role

db.session.add(role_admin)
db.session.add(role_public)
db.session.add(user)
db.session.commit()
