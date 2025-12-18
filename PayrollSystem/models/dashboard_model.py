"""
Model functions for dashboard statistics and metrics.
"""

from __future__ import annotations

from typing import Dict

from .database import get_connection


def get_hr_dashboard_stats() -> Dict[str, int]:
    """Get HR Officer dashboard statistics."""
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Total Employees
            cur.execute("SELECT COUNT(*) as total FROM employees WHERE is_active = 1")
            total_employees = cur.fetchone()["total"]
            
            # Reports Generated (using payroll periods as proxy)
            cur.execute("SELECT COUNT(*) as total FROM payroll_periods WHERE status IN ('PROCESSED', 'APPROVED')")
            reports_generated = cur.fetchone()["total"]
            
            return {
                "total_employees": total_employees,
                "reports_generated": reports_generated,
            }


def get_accountant_dashboard_stats() -> Dict[str, any]:
    """Get Accountant dashboard statistics."""
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Pending Verification
            cur.execute("SELECT COUNT(*) as total FROM payroll_entries WHERE status = 'PENDING'")
            pending_verification = cur.fetchone()["total"]
            
            # Verified This Month
            cur.execute("""
                SELECT COUNT(*) as total FROM payroll_entries pe
                JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
                WHERE pe.status = 'VERIFIED' 
                AND MONTH(pp.start_date) = MONTH(CURRENT_DATE())
                AND YEAR(pp.start_date) = YEAR(CURRENT_DATE())
            """)
            verified_this_month = cur.fetchone()["total"]
            
            # Total Payroll
            cur.execute("""
                SELECT COALESCE(SUM(net_pay), 0) as total FROM payroll_entries
                WHERE status IN ('VERIFIED', 'APPROVED')
            """)
            total_payroll = float(cur.fetchone()["total"] or 0)
            
            return {
                "pending_verification": pending_verification,
                "verified_this_month": verified_this_month,
                "total_payroll": total_payroll,
            }


def get_admin_dashboard_stats() -> Dict[str, any]:
    """Get Administrator dashboard statistics."""
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Total Users
            cur.execute("SELECT COUNT(*) as total FROM users WHERE is_active = 1")
            total_users = cur.fetchone()["total"]
            
            # System Health (simplified - check if database is accessible)
            system_health = "OK"
            
            # Last Backup (using latest audit log as proxy)
            cur.execute("SELECT MAX(created_at) as last_backup FROM audit_logs")
            last_backup_row = cur.fetchone()
            last_backup = "Never" if not last_backup_row["last_backup"] else "Recently"
            
            return {
                "total_users": total_users,
                "system_health": system_health,
                "last_backup": last_backup,
            }

