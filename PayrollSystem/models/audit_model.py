"""
Model functions for audit log queries.
"""

from __future__ import annotations

from typing import List, Optional, Dict

from .database import get_connection


def get_audit_logs(user_filter: Optional[str] = None, action_filter: Optional[str] = None, date_filter: Optional[str] = None) -> List[Dict]:
    """
    Get audit logs with optional filters.
    
    Args:
        user_filter: Username or role name to filter by (or "ALL" for all users)
                    Role names: "Admin", "HR Officer", "Accountant", "Employee"
        action_filter: Action type to filter by (or "ALL" for all actions)
        date_filter: Date string in YYYY-MM-DD format (or None for all dates)
    """
    query = """
        SELECT al.created_at, u.username as user, r.name as role_name, al.action, al.details
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.id
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE 1=1
    """
    params = []
    
    if user_filter and user_filter != "ALL":
        # Check if it's a role name or username
        role_names = ["Admin", "HR Officer", "Accountant", "Employee", "Administrator"]
        if user_filter in role_names:
            # Map "Admin" to "Administrator" for database consistency
            role_filter = "Administrator" if user_filter == "Admin" else user_filter
            query += " AND r.name = %s"
            params.append(role_filter)
        else:
            query += " AND u.username = %s"
            params.append(user_filter)
    
    if action_filter and action_filter != "ALL":
        query += " AND al.action = %s"
        params.append(action_filter)
    
    if date_filter:
        query += " AND DATE(al.created_at) = %s"
        params.append(date_filter)
    
    query += " ORDER BY al.created_at DESC LIMIT 100"
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def log_audit(user_id: Optional[int], action: str, details: str = ""):
    """Create an audit log entry."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO audit_logs (user_id, action, details) VALUES (%s, %s, %s)",
                (user_id, action, details)
            )
            conn.commit()

