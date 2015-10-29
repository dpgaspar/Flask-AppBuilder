from wtforms import Form, StringField
from wtforms.validators import DataRequired
from flask.ext.appbuilder.fieldwidgets import BS3TextFieldWidget
from flask.ext.appbuilder.forms import DynamicForm


class MyForm(DynamicForm):
    field1 = StringField(('Field1'),
        description=('Your field number one!'),
        validators = [DataRequired()], widget=BS3TextFieldWidget())
    field2 = StringField(('Field2'),
        description=('Your field number two!'), widget=BS3TextFieldWidget())
