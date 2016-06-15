from wtforms import StringField, BooleanField, PasswordField
from flask_wtf.recaptcha import RecaptchaField
from flask_babelpkg import lazy_gettext
from wtforms.validators import DataRequired, EqualTo, Email
from flask_appbuilder.fieldwidgets import BS3PasswordFieldWidget, BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm


class UserInfoEdit(DynamicForm):
    first_name = StringField(lazy_gettext('First Name'), validators=[DataRequired()], widget=BS3TextFieldWidget(),
                             description=lazy_gettext('Write the user first name or names'))
    last_name = StringField(lazy_gettext('Last Name'), validators=[DataRequired()], widget=BS3TextFieldWidget(),
                            description=lazy_gettext('Write the user last name'))
    emp_number = StringField(lazy_gettext('Emp. Number'), validators=[DataRequired()], widget=BS3TextFieldWidget(),
                            description=lazy_gettext('Employee Number'))
