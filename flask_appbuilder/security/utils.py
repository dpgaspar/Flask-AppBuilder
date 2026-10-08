from random import SystemRandom
import string
from typing import Optional

LETTERS_AND_DIGITS = string.ascii_letters + string.digits


def generate_random_string(length=30):
    rand = SystemRandom()
    return "".join(rand.choice(LETTERS_AND_DIGITS) for _ in range(length))


def is_null_password(password: Optional[str]) -> bool:
    """
    Whether a password is empty or made up solely of NUL bytes.

    Such values must not be accepted for database authentication: the hashes
    of an empty string and of any NUL-only string are indistinguishable, so an
    account stored without a real password could otherwise be authenticated by
    sending one or more NUL bytes.
    """
    return not password or sum(password.encode()) == 0
