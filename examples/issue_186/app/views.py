from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask.ext.appbuilder import ModelView
from flask.ext.appbuilder.fieldwidgets import BS3TextFieldWidget
from flask.ext.babelpkg import gettext
from app import appbuilder, db
from wtforms.fields import TextField
from .models import Device


class DeviceModelView(ModelView):
    datamodel = SQLAInterface(Device)
    search_columns = ['description','site']
    add_form_extra_fields = {'name': TextField(gettext('Extra Field'),
                    description=gettext('Extra Field description'),
                    widget=BS3TextFieldWidget())}

    edit_form_extra_fields = {'name': TextField(gettext('Extra Field'),
                    description=gettext('Extra Field description'),
					widget=BS3TextFieldWidget())}
	
    search_form_extra_fields = {'name': TextField(gettext('Extra Field'),
                    description=gettext('Extra Field description'),
                    widget=BS3TextFieldWidget())}			

db.create_all()

appbuilder.add_view(DeviceModelView, "Devices", icon="fa-folder-open-o", category="Management", category_icon='fa-envelope')

