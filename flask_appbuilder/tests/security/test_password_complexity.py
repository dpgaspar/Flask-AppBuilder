from flask_appbuilder.exceptions import PasswordComplexityValidationError
from flask_appbuilder.validators import default_password_complexity

from ..base import FABTestCase


class PasswordComplexityTestCase(FABTestCase):
    def test_default_complexity_validator(self):
        # No upper, numeric digits or special characters
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity("password")
        # No upper nor special characters
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity("password1234")
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity("Password123")
        # Upper, lower, numeric but no special characters
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity("PAssword123")
        # Upper, lower, special and numeric but small
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity("PAssw12!")
        # Just one Upper
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity("Password123!")
        # Just two lower
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity("PASSWOrd123!")
        # Just one numeric digit
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity("PAssword3!!")
        default_password_complexity("PAssword123!")
