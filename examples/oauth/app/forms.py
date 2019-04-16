from wtforms import StringField
from flask_babel import lazy_gettext
from wtforms.validators import DataRequired
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm


class TweetForm(DynamicForm):
    message = StringField(
        lazy_gettext("Tweet message"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
