import re
from typing import Optional

from flask import current_app
from flask_appbuilder.exceptions import PasswordComplexityValidationError
from flask_appbuilder.models.base import BaseInterface
from flask_babel import gettext
from wtforms import Field, Form, ValidationError

password_complexity_regex = re.compile(
    r"""(
    ^(?=.*[A-Z].*[A-Z])                # at least two capital letters
    (?=.*[^0-9a-zA-Z])                 # at least one of these special characters
    (?=.*[0-9].*[0-9])                 # at least two numeric digits
    (?=.*[a-z].*[a-z].*[a-z])          # at least three lower case letters
    .{10,}                             # at least 10 total characters
    $
    )""",
    re.VERBOSE,
)


class Unique:
    """
    WTForm field validator. Checks if field value is unique against
    a specified table field.
    """

    field_flags = ("unique",)

    def __init__(
        self, datamodel: BaseInterface, col_name: str, message: Optional[str] = None
    ) -> None:
        """
        :param datamodel: The datamodel class, abstract layer for backend
        :param col_name: The unique column name.
        :param message: The error message.
        """
        self.datamodel = datamodel
        self.col_name = col_name
        self.message = message

    def __call__(self, form: Form, field: Field) -> None:
        filters = self.datamodel.get_filters().add_filter(
            self.col_name, self.datamodel.FilterEqual, field.data
        )
        count, obj = self.datamodel.query(filters)
        if count > 0:
            # only test if Unique, if pk value is different on update.
            if not hasattr(form, "_id") or form._id != self.datamodel.get_keys(obj)[0]:
                if self.message is None:
                    self.message = field.gettext("Already exists.")
                raise ValidationError(self.message)


class PasswordComplexityValidator:
    """
    WTForm field validator. Calls a custom password validator, useful for imposing
    password complexity for database Auth users.
    """

    def __call__(self, form: Form, field: Field) -> None:
        if current_app.config.get("FAB_PASSWORD_COMPLEXITY_ENABLED", False):
            password_complexity_validator = current_app.config.get(
                "FAB_PASSWORD_COMPLEXITY_VALIDATOR", None
            )
            if password_complexity_validator is not None:
                try:
                    password_complexity_validator(field.data)
                except PasswordComplexityValidationError as exc:
                    raise ValidationError(str(exc))
            else:
                try:
                    default_password_complexity(field.data)
                except PasswordComplexityValidationError as exc:
                    raise ValidationError(str(exc))


def default_password_complexity(password: str) -> None:
    """
    FAB's default password complexity validator, set FAB_PASSWORD_COMPLEXITY_ENABLED
    to True to enable it
    """
    match = re.search(password_complexity_regex, password)
    if not match:
        raise PasswordComplexityValidationError(
            gettext(
                "Must have at least two capital letters,"
                " one special character, two digits, three lower case letters and"
                " a minimal length of 10."
            )
        )
