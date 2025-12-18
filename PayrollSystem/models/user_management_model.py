"""
Model functions for user management queries.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .database import get_connection


def get_all_users() -> List[Dict]:
    """Get all users with their roles."""
    query = """
        SELECT u.id, u.username, r.name as role, 
               CASE WHEN u.is_active = 1 THEN 'Active' ELSE 'Inactive' END as status
        FROM users u
        JOIN roles r ON u.role_id = r.id
        ORDER BY u.username
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query)
            return cur.fetchall()


def get_departments() -> List[Dict]:
    """Get all departments."""
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, name FROM departments ORDER BY name")
            return cur.fetchall()

