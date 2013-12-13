
from flask_appbuilder.models.mixins import AuditMixin, BaseMixin, FileColumn, ImageColumn
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey
from flask_appbuilder import Base
from flask_appbuilder.security.models import User
from app import db
"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""
        
class Project(AuditMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(150), unique = True, nullable=False)
    
class ProjectFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship("Project")
    file = db.Column(FileColumn, nullable=False)
    
