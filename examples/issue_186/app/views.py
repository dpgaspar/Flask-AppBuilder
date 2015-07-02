import sqlalchemy as sa
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder import ModelView
from flask.ext.appbuilder.fieldwidgets import BS3TextFieldWidget
from flask.ext.babelpkg import gettext
from flask.ext.appbuilder.models.sqla.filters import BaseFilter
from flask.ext.babelpkg import lazy_gettext
from app import appbuilder, db
from wtforms.fields import TextField
from .models import Device, Site, DeviceType, LowerCaseString


class MySQLAInterface(SQLAInterface):
    def is_string(self, col_name):
        try:
            return (isinstance(self.list_columns[col_name].type, sa.types.String) or
                    isinstance(self.list_columns[col_name].type, LowerCaseString))
        except:
            return False

class SiteModelView(ModelView):
    datamodel = SQLAInterface(Site)


class DeviceTypeModelView(ModelView):
    datamodel = SQLAInterface(DeviceType)


class DeviceModelView(ModelView):
    datamodel = MySQLAInterface(Device)
    
db.create_all()

appbuilder.add_view(SiteModelView, "Site", icon="fa-folder-open-o", category="Management", category_icon='fa-envelope')
appbuilder.add_view(DeviceTypeModelView, "DeviceType", icon="fa-folder-open-o", category="Management", category_icon='fa-envelope')
appbuilder.add_view(DeviceModelView, "Devices", icon="fa-folder-open-o", category="Management", category_icon='fa-envelope')

