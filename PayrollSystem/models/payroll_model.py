"""
Model functions for payroll-related queries.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .database import get_connection


def get_payroll_periods() -> List[Dict]:
    """Get all payroll periods."""
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, name, start_date, end_date, status FROM payroll_periods ORDER BY start_date DESC")
            return cur.fetchall()


def get_payroll_entries_by_period(period_id: int) -> List[Dict]:
    """Get payroll entries for a specific period."""
    query = """
        SELECT pe.id, e.employee_code, CONCAT(e.first_name, ' ', e.last_name) as name,
               pe.basic_pay, pe.overtime_pay, pe.allowances, pe.gross_pay,
               pe.sss_contrib, pe.philhealth_contrib, pe.pagibig_contrib,
               pe.withholding_tax, pe.total_deductions, pe.net_pay, pe.status
        FROM payroll_entries pe
        JOIN employees e ON pe.employee_id = e.id
        WHERE pe.payroll_period_id = %s
        ORDER BY e.last_name, e.first_name
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (period_id,))
            return cur.fetchall()


def get_pending_verification_entries() -> List[Dict]:
    """Get payroll entries pending verification."""
    query = """
        SELECT pe.id, e.employee_code, CONCAT(e.first_name, ' ', e.last_name) as name,
               pe.gross_pay as salary, pe.total_deductions as deduction, pe.net_pay,
               pp.name as period_name, pp.start_date, pp.end_date
        FROM payroll_entries pe
        JOIN employees e ON pe.employee_id = e.id
        JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
        WHERE pe.status = 'PENDING'
        ORDER BY pp.start_date DESC, e.last_name
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query)
            return cur.fetchall()


def get_total_payroll_for_period(period_id: Optional[int] = None) -> float:
    """Get total payroll amount for a period or all periods."""
    if period_id:
        query = "SELECT COALESCE(SUM(net_pay), 0) as total FROM payroll_entries WHERE payroll_period_id = %s"
        params = (period_id,)
    else:
        query = "SELECT COALESCE(SUM(net_pay), 0) as total FROM payroll_entries WHERE status = 'PENDING'"
        params = ()
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, params)
            result = cur.fetchone()
            return float(result["total"] or 0)

