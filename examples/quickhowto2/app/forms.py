from wtforms import StringField
from flask_babelpkg import lazy_gettext
from wtforms.validators import DataRequired
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm


class TestForm(DynamicForm):
    TestFieldOne = StringField(lazy_gettext('Test Field One'), validators=[DataRequired()], widget=BS3TextFieldWidget())
    TestFieldTwo = StringField(lazy_gettext('Test Field One'), validators=[DataRequired()], widget=BS3TextFieldWidget())
