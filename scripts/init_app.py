import os
import shutil
from flask.ext import appbuilder

#projectname = raw_input('Enter you project name: ')
#os.mkdir(projectname)
#path = os.path.dirname(appbuilder.__file__)
#shutil.copytree(str(path).join('/skeleton') , './'.join(projectname))


from app import app, db
from flask.ext.appbuilder.security.models import User, Role


print "--------------------------"
print "     CREATE DB"
print "--------------------------"
db.create_all()
print "--------------------------"
print " CREATE USER and  ROLES"
print "--------------------------"
role_admin = Role()
role_admin.name = app.config['AUTH_ROLE_ADMIN']
role_public = Role()
role_public.name = app.config['AUTH_ROLE_PUBLIC']
user = User()
user.first_name = 'Admin'
user.last_name = ''
user.username = 'admin'
user.password = 'general'
user.active = True
user.role = role_admin

db.session.add(role_admin)
db.session.add(role_public)
db.session.add(user)
db.session.commit()
