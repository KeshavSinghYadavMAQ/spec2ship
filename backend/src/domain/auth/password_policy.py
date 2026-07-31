"""Password policy primitives and hashing helpers (T009)."""

from __future__ import annotations

import hashlib
import hmac
import os
import re

_MIN_LENGTH = 12
_ITERATIONS = 200_000
_PASSWORD_FORMAT = "pbkdf2_sha256"
_COMPROMISED_PASSWORDS = {
    "password",
    "password123",
    "123456789",
    "qwerty123",
    "letmein123",
    "welcome123",
    "admin123!",
}


class PasswordPolicyError(Exception):
    pass


class CompromisedPasswordError(PasswordPolicyError):
    pass


def validate_password_policy(password: str) -> None:
    if len(password) < _MIN_LENGTH:
        raise PasswordPolicyError("Password must be at least 12 characters long")
    if re.search(r"[A-Z]", password) is None:
        raise PasswordPolicyError("Password must include an uppercase letter")
    if re.search(r"[a-z]", password) is None:
        raise PasswordPolicyError("Password must include a lowercase letter")
    if re.search(r"[0-9]", password) is None:
        raise PasswordPolicyError("Password must include a number")
    if re.search(r"[^A-Za-z0-9]", password) is None:
        raise PasswordPolicyError("Password must include a symbol")
    if password.lower() in _COMPROMISED_PASSWORDS:
        raise CompromisedPasswordError("Password is present in compromised-password denylist")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_PASSWORD_FORMAT}${_ITERATIONS}${salt.hex()}${derived.hex()}"


def verify_password(password: str, encoded_password: str) -> bool:
    try:
        fmt, iterations_raw, salt_hex, hash_hex = encoded_password.split("$", maxsplit=3)
        if fmt != _PASSWORD_FORMAT:
            return False
        iterations = int(iterations_raw)
        expected = bytes.fromhex(hash_hex)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(actual, expected)
