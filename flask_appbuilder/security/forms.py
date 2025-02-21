from flask_babel import lazy_gettext
from flask_wtf.recaptcha import RecaptchaField
from wtforms import BooleanField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from ..fieldwidgets import BS3PasswordFieldWidget, BS3TextFieldWidget
from ..forms import DynamicForm
from ..validators import PasswordComplexityValidator


class SelectDataRequired(DataRequired):
    """
    Select required flag on the input field will not work well on Chrome
    Console error:
        An invalid form control with name='roles' is not focusable.

    This makes a simple override to the DataRequired to be used specifically with
    select fields
    """

    field_flags = {}


def roles_or_groups_required(form, field):
    if not form["roles"].data and not form["groups"].data:
        raise ValidationError(lazy_gettext("Either select a role or a group"))


class LoginForm_oid(DynamicForm):
    openid = StringField(lazy_gettext("OpenID"), validators=[DataRequired()])
    username = StringField(lazy_gettext("User Name"))
    remember_me = BooleanField(lazy_gettext("Remember me"), default=False)


class LoginForm_db(DynamicForm):
    username = StringField(lazy_gettext("User Name"), validators=[DataRequired()])
    password = PasswordField(lazy_gettext("Password"), validators=[DataRequired()])


class UserInfoEdit(DynamicForm):
    first_name = StringField(
        lazy_gettext("First Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        description=lazy_gettext("Write the user first name or names"),
    )
    last_name = StringField(
        lazy_gettext("Last Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        description=lazy_gettext("Write the user last name"),
    )


class ResetPasswordForm(DynamicForm):
    password = PasswordField(
        lazy_gettext("Password"),
        description=lazy_gettext(
            "Please use a good password policy,"
            " this application does not check this for you"
        ),
        validators=[DataRequired(), PasswordComplexityValidator()],
        widget=BS3PasswordFieldWidget(),
    )
    conf_password = PasswordField(
        lazy_gettext("Confirm Password"),
        description=lazy_gettext("Please rewrite the password to confirm"),
        validators=[EqualTo("password", message=lazy_gettext("Passwords must match"))],
        widget=BS3PasswordFieldWidget(),
    )


class RegisterUserDBForm(DynamicForm):
    username = StringField(
        lazy_gettext("User Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
    first_name = StringField(
        lazy_gettext("First Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
    last_name = StringField(
        lazy_gettext("Last Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
    email = StringField(
        lazy_gettext("Email"),
        validators=[DataRequired(), Email()],
        widget=BS3TextFieldWidget(),
    )
    password = PasswordField(
        lazy_gettext("Password"),
        description=lazy_gettext(
            "Please use a good password policy,"
            " this application does not check this for you"
        ),
        validators=[DataRequired()],
        widget=BS3PasswordFieldWidget(),
    )
    conf_password = PasswordField(
        lazy_gettext("Confirm Password"),
        description=lazy_gettext("Please rewrite the password to confirm"),
        validators=[EqualTo("password", message=lazy_gettext("Passwords must match"))],
        widget=BS3PasswordFieldWidget(),
    )
    recaptcha = RecaptchaField()


class RegisterUserOIDForm(DynamicForm):
    username = StringField(
        lazy_gettext("User Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
    first_name = StringField(
        lazy_gettext("First Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
    last_name = StringField(
        lazy_gettext("Last Name"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
    email = StringField(
        lazy_gettext("Email"),
        validators=[DataRequired(), Email()],
        widget=BS3TextFieldWidget(),
    )
    recaptcha = RecaptchaField()
