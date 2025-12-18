"""
Employee Salary Management Model for PROLY Payroll System.
Handles employee salary updates and history tracking.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional
import logging

from .database import get_connection
from .audit_model import log_audit


logger = logging.getLogger(__name__)


def update_employee_salary(employee_id: int, new_salary: float, effective_date: Optional[date] = None, reason: Optional[str] = None) -> bool:
    """
    Update an employee's base salary.
    
    Args:
        employee_id: Employee ID
        new_salary: New base salary amount
        effective_date: Date when salary change takes effect (defaults to today)
        reason: Reason for salary change (e.g., "Promotion", "Annual Increase")
    
    Returns:
        True if successful, False otherwise
    """
    if effective_date is None:
        effective_date = date.today()
    
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                # Get current salary for history
                cur.execute("SELECT base_salary FROM employees WHERE id = %s", (employee_id,))
                result = cur.fetchone()
                if not result:
                    return False
                
                old_salary = float(result['base_salary'])
                
                # Update employee salary
                cur.execute(
                    "UPDATE employees SET base_salary = %s WHERE id = %s",
                    (new_salary, employee_id)
                )
                
                # Log salary history
                cur.execute(
                    """
                    INSERT INTO salary_history (employee_id, old_salary, new_salary, effective_date, reason, changed_by)
                    VALUES (%s, %s, %s, %s, %s, NULL)
                    """,
                    (employee_id, old_salary, new_salary, effective_date, reason)
                )
                
                conn.commit()
                
                # Log audit
                log_audit(None, "Update Salary", f"Updated salary for employee {employee_id}: {old_salary:,.2f} -> {new_salary:,.2f} ({reason or 'No reason provided'})")
                
                return True
    except Exception as e:
        logger.exception("Error updating employee salary: %s", e)
        return False


def get_employee_salary_history(employee_id: int) -> List[Dict]:
    """
    Get salary history for an employee.
    
    Args:
        employee_id: Employee ID
    
    Returns:
        List of salary change records
    """
    query = """
        SELECT 
            sh.id,
            sh.old_salary,
            sh.new_salary,
            sh.effective_date,
            sh.reason,
            sh.created_at,
            u.username as changed_by_username
        FROM salary_history sh
        LEFT JOIN users u ON sh.changed_by = u.id
        WHERE sh.employee_id = %s
        ORDER BY sh.effective_date DESC, sh.created_at DESC
    """
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (employee_id,))
            return cur.fetchall()


def get_employee_current_salary(employee_id: int) -> Optional[float]:
    """
    Get current base salary for an employee.
    
    Args:
        employee_id: Employee ID
    
    Returns:
        Current base salary or None if employee not found
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT base_salary FROM employees WHERE id = %s", (employee_id,))
            result = cur.fetchone()
            if result:
                return float(result[0])
            return None

