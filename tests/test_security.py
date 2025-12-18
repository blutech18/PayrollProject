from __future__ import annotations

from utils.security import hash_password, verify_password


def test_hash_and_verify_password_success():
    plain = "Secr3tP@ss!"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True


def test_verify_password_failure():
    plain = "password123"
    other = "different123"
    hashed = hash_password(plain)

    assert verify_password(other, hashed) is False


