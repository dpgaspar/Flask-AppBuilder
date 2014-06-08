from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, PasswordField
from flask.ext.babelpkg import lazy_gettext
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms import validators
from wtforms.validators import Required, Length, EqualTo
#from flask.ext.wtf import Required, Length, validators, EqualTo
from flask.ext.appbuilder.fieldwidgets import BS3PasswordFieldWidget
from flask.ext.appbuilder.forms import DynamicForm


class LoginForm_oid(DynamicForm):
    openid = TextField(lazy_gettext('openid'), validators=[Required()])
    remember_me = BooleanField(lazy_gettext('remember_me'), default=False)


class LoginForm_db(DynamicForm):
    username = TextField(lazy_gettext('User Name'), validators=[Required()])
    password = PasswordField(lazy_gettext('Password'), validators=[Required()])


class ResetPasswordForm(DynamicForm):
    password = PasswordField(lazy_gettext('Password'),
                             description=lazy_gettext(
                                 'Please use a good password policy, this application does not check this for you'),
                             validators=[Required()],
                             widget=BS3PasswordFieldWidget())
    conf_password = PasswordField(lazy_gettext('Confirm Password'),
                                  description=lazy_gettext('Please rewrite the password to confirm'),
                                  validators=[EqualTo('password', message=lazy_gettext('Passwords must match'))],
                                  widget=BS3PasswordFieldWidget())
