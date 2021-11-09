from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm
from flask_babel import lazy_gettext
from wtforms import StringField
from wtforms.validators import DataRequired


class TestForm(DynamicForm):
    TestFieldOne = StringField(
        lazy_gettext("Test Field One"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
    TestFieldTwo = StringField(
        lazy_gettext("Test Field One"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
