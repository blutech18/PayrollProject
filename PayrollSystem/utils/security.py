from __future__ import annotations

"""
Password hashing utilities for the PROLY Payroll Management System.

Uses bcrypt for secure password hashing and verification.
"""

import bcrypt


def hash_password(plain: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Returns the hashed password as a UTF-8 string suitable for storing in the database.
    """
    if plain is None:
        raise ValueError("Password cannot be None")
    password_bytes = plain.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Returns True if the password matches, False otherwise.
    """
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        # In case the stored hash is not a valid bcrypt hash
        return False


