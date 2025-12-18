from __future__ import annotations

"""
User service layer for PROLY Payroll System.

Contains business logic for creating and updating users that was previously
embedded in views.
"""

from typing import Optional, Dict, Any

from PyQt6.QtWidgets import QMessageBox

from models.database import get_connection
from models.audit_model import log_audit
from utils.security import hash_password


def create_user(
    username: str,
    password: str,
    role_name: str,
    is_active: bool = True,
    parent_widget=None,
) -> bool:
    """
    Create a new user with the given role name.

    Returns True on success, False on validation or DB error.
    """
    if not username:
        if parent_widget:
            QMessageBox.warning(parent_widget, "Validation Error", "Username is required.")
        return False

    if not password:
        if parent_widget:
            QMessageBox.warning(parent_widget, "Validation Error", "Password is required.")
        return False

    if len(password) < 4:
        if parent_widget:
            QMessageBox.warning(
                parent_widget, "Validation Error", "Password must be at least 4 characters."
            )
        return False

    password_hash = hash_password(password)

    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                # Check if username already exists
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    if parent_widget:
                        QMessageBox.warning(
                            parent_widget,
                            "Validation Error",
                            f"Username '{username}' already exists.",
                        )
                    return False

                # Resolve role_id from role name
                cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
                role_row = cur.fetchone()
                if not role_row:
                    if parent_widget:
                        QMessageBox.warning(
                            parent_widget,
                            "Error",
                            f"Role '{role_name}' not found in system.",
                        )
                    return False

                role_id = role_row["id"]

                cur.execute(
                    """
                    INSERT INTO users (username, password_hash, role_id, is_active, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (username, password_hash, role_id, 1 if is_active else 0),
                )
                conn.commit()

                log_audit(None, "Create User", f"Created new user: {username}")

        if parent_widget:
            QMessageBox.information(
                parent_widget,
                "Success",
                f"User '{username}' has been created.",
            )
        return True
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(
                parent_widget,
                "Error",
                f"Failed to create user: {str(e)}",
            )
        return False


def update_user(
    username: str,
    role_name: str,
    is_active: bool,
    new_password: Optional[str] = None,
    parent_widget=None,
) -> bool:
    """
    Update an existing user's role, active status, and optional password.
    """
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                # Resolve role_id from role name
                cur.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
                role_row = cur.fetchone()
                if not role_row:
                    if parent_widget:
                        QMessageBox.warning(
                            parent_widget,
                            "Error",
                            f"Role '{role_name}' not found in system.",
                        )
                    return False

                role_id = role_row["id"]

                if new_password:
                    if len(new_password) < 4:
                        if parent_widget:
                            QMessageBox.warning(
                                parent_widget,
                                "Validation Error",
                                "Password must be at least 4 characters.",
                            )
                        return False
                    password_hash = hash_password(new_password)
                    cur.execute(
                        """
                        UPDATE users
                        SET password_hash = %s, role_id = %s, is_active = %s
                        WHERE username = %s
                        """,
                        (password_hash, role_id, 1 if is_active else 0, username),
                    )
                else:
                    cur.execute(
                        """
                        UPDATE users
                        SET role_id = %s, is_active = %s
                        WHERE username = %s
                        """,
                        (role_id, 1 if is_active else 0, username),
                    )

                conn.commit()

                log_audit(None, "Update User", f"Updated user: {username}")

        if parent_widget:
            QMessageBox.information(
                parent_widget,
                "Success",
                f"User '{username}' has been updated.",
            )
        return True
    except Exception as e:
        if parent_widget:
            QMessageBox.critical(
                parent_widget,
                "Error",
                f"Failed to update user: {str(e)}",
            )
        return False


