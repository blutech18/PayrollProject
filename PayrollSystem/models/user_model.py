from __future__ import annotations

from typing import Optional

from .database import get_connection


class User:
    """
    Simple User model for authentication and RBAC.
    """

    def __init__(self, user_id: int, username: str, role_name: str, is_active: bool = True):
        self.id = user_id
        self.username = username
        self.role_name = role_name
        self.is_active = is_active


def get_user_by_username(username: str) -> Optional[User]:
    """
    Fetch a user plus role name by username. Password verification is handled in controllers.
    """
    query = """
        SELECT u.id, u.username, u.is_active, r.name AS role_name, u.password_hash
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.username = %s
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (username,))
            row = cur.fetchone()

    if not row:
        return None

    user = User(row["id"], row["username"], row["role_name"], bool(row["is_active"]))
    # Attach hashed password for controller-side verification
    user.password_hash = row["password_hash"]
    return user


def get_employee_id_for_user(user_id: int) -> Optional[int]:
    """
    Get employee ID associated with a user account.
    This assumes username matches employee_code or there's a mapping table.
    For now, we'll try to match by username = employee_code.
    """
    query = """
        SELECT e.id
        FROM employees e
        JOIN users u ON u.username = e.employee_code
        WHERE u.id = %s
        LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            return row[0] if row else None
