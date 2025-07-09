import importlib
from random import SystemRandom
import string

from packaging.version import Version

LETTERS_AND_DIGITS = string.ascii_letters + string.digits


def generate_random_string(length=30):
    rand = SystemRandom()
    return "".join(rand.choice(LETTERS_AND_DIGITS) for _ in range(length))


def get_default_hash_method(app):
    """
    Returns the default password hash method based on the Werkzeug version.
    """
    parsed_werkzeug_version = Version(importlib.metadata.version("werkzeug"))
    if parsed_werkzeug_version < Version("3.0.0"):
        return app.config.get("FAB_PASSWORD_HASH_METHOD", "pbkdf2:sha256")
    else:
        return app.config.get("FAB_PASSWORD_HASH_METHOD", "scrypt")
