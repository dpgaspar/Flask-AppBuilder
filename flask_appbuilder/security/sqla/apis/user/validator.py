from flask import current_app
from flask_appbuilder.exceptions import PasswordComplexityValidationError
from flask_appbuilder.validators import default_password_complexity
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Validator


class PasswordComplexityValidator(Validator):
    """Validator for password.
    """

    def __call__(self, value: str) -> str:
        if current_app.config.get("FAB_PASSWORD_COMPLEXITY_ENABLED", False):
            password_complexity_validator = current_app.config.get(
                "FAB_PASSWORD_COMPLEXITY_VALIDATOR", None
            )
            if password_complexity_validator is not None:
                try:
                    password_complexity_validator(value)
                except PasswordComplexityValidationError as exc:
                    raise ValidationError(str(exc))
            else:
                try:
                    default_password_complexity(value)
                except PasswordComplexityValidationError as exc:
                    raise ValidationError(str(exc))

        return value
