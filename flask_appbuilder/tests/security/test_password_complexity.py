from flask_appbuilder.exceptions import PasswordComplexityValidationError
from flask_appbuilder.validators import default_password_complexity
from parameterized import parameterized

from ..base import FABTestCase


class PasswordComplexityTestCase(FABTestCase):
    @parameterized.expand(
        [
            ("password"),  # No upper, numeric digits or special characters
            ("password1234"),  # No upper nor special characters
            ("password123"),  # No upper nor special characters
            ("PAssword123"),  # Upper, lower, numeric but no special characters
            ("PAssw12!"),  # Upper, lower, special and numeric but small
            ("Password123!"),  # Just one Upper
            ("PASSWOrd123!"),  # Just two lower
            ("PAssword3!!"),  # Just one numeric digit
            ("PAssw3!!"),  # length not enough
        ]
    )
    def test_default_complexity_validator_fail(self, password):
        with self.assertRaises(PasswordComplexityValidationError):
            default_password_complexity(password)

    @parameterized.expand(
        [
            ("PAssword12!"),  # Simple valid example
            ("PAssword12!#"),  # Multiple special characters
            ("PAssword12!#>"),  # More multiple special characters
            ("PAssw!ord12"),  # Special character in the middle
            ("!PAssword12"),  # Special characters at the beginning
            ("!PAssw>ord12"),  # Special characters at the beginning and middle
            ("ssw>ord12!PA"),  # Upper case in the end
            ("ssw>PAord12!"),  # Upper case in the end
        ]
    )
    def test_default_complexity_validator(self, password):
        default_password_complexity(password)
