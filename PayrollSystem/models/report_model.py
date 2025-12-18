"""
Report Model for PROLY Payroll System.
Provides functions to generate different types of reports (Attendance, Payroll, Performance).
Supports daily, weekly, and monthly report filtering.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .database import get_connection


def get_attendance_report(start_date: date, end_date: date, department_id: Optional[int] = None) -> List[Dict]:
    """
    Generate attendance report for a date range and optional department.
    
    Args:
        start_date: Start date of the report period
        end_date: End date of the report period
        department_id: Optional department filter (None for all departments)
    
    Returns:
        List of attendance records with employee info
    """
    query = """
        SELECT 
            e.id as employee_id,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.position,
            d.name as department_name,
            a.attendance_date,
            a.time_in,
            a.time_out,
            a.hours_worked,
            a.status,
            a.late_minutes,
            a.undertime_minutes
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.is_active = 1
        AND a.attendance_date >= %s
        AND a.attendance_date <= %s
    """
    params = [start_date, end_date]
    
    if department_id:
        query += " AND e.department_id = %s"
        params.append(department_id)
    
    query += " ORDER BY e.last_name, e.first_name, a.attendance_date"
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def get_payroll_report(start_date: date, end_date: date, department_id: Optional[int] = None) -> List[Dict]:
    """
    Generate payroll report for a date range and optional department.
    
    Args:
        start_date: Start date of the report period
        end_date: End date of the report period
        department_id: Optional department filter (None for all departments)
    
    Returns:
        List of payroll entries with employee and period info
    """
    query = """
        SELECT 
            e.id as employee_id,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.position,
            d.name as department_name,
            pp.name as period_name,
            pp.start_date as period_start,
            pp.end_date as period_end,
            pe.basic_pay,
            pe.overtime_pay,
            pe.allowances,
            pe.holiday_pay,
            pe.vacation_sickleave,
            pe.salary_adjustment,
            pe.incentive_pay,
            pe.gross_pay,
            pe.sss_contrib,
            pe.philhealth_contrib,
            pe.pagibig_contrib,
            pe.withholding_tax,
            pe.late_deduction,
            pe.cash_advance,
            pe.undertime_deduction,
            pe.other_deductions,
            pe.total_deductions,
            pe.net_pay,
            pe.status as payroll_status
        FROM payroll_entries pe
        JOIN employees e ON pe.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
        WHERE e.is_active = 1
        -- Include any payroll period that overlaps the requested range
        AND pp.start_date <= %s
        AND pp.end_date >= %s
    """
    params = [end_date, start_date]
    
    if department_id:
        query += " AND e.department_id = %s"
        params.append(department_id)
    
    query += " ORDER BY e.last_name, e.first_name, pp.start_date DESC"
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def get_performance_report(start_date: date, end_date: date, department_id: Optional[int] = None) -> List[Dict]:
    """
    Generate performance report for a date range and optional department.
    Uses payroll data and attendance to calculate performance metrics.
    
    Args:
        start_date: Start date of the report period
        end_date: End date of the report period
        department_id: Optional department filter (None for all departments)
    
    Returns:
        List of performance metrics per employee
    """
    query = """
        SELECT 
            e.id as employee_id,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.position,
            d.name as department_name,
            COUNT(DISTINCT pe.id) as payroll_periods_count,
            SUM(pe.gross_pay) as total_gross_pay,
            AVG(pe.gross_pay) as avg_gross_pay,
            SUM(pe.overtime_pay) as total_overtime,
            SUM(pe.incentive_pay) as total_incentives,
            SUM(CASE WHEN pe.late_deduction > 0 THEN 1 ELSE 0 END) as late_occurrences,
            SUM(pe.late_deduction) as total_late_deductions,
            SUM(CASE WHEN pe.undertime_deduction > 0 THEN 1 ELSE 0 END) as undertime_occurrences,
            SUM(pe.undertime_deduction) as total_undertime_deductions,
            COUNT(DISTINCT a.id) as attendance_days,
            AVG(a.hours_worked) as avg_hours_per_day
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN payroll_entries pe ON e.id = pe.employee_id
        LEFT JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
            AND pp.start_date <= %s
            AND pp.end_date >= %s
        LEFT JOIN attendance a ON e.id = a.employee_id AND a.attendance_date >= %s AND a.attendance_date <= %s
        WHERE e.is_active = 1
    """
    params = [end_date, start_date, start_date, end_date]
    
    if department_id:
        query += " AND e.department_id = %s"
        params.append(department_id)
    
    query += " GROUP BY e.id, e.employee_code, e.first_name, e.last_name, e.position, d.name"
    query += " ORDER BY e.last_name, e.first_name"
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, params)
            return cur.fetchall()


# ============================================================================
# Date Range Helper Functions for Daily/Weekly/Monthly Reports
# ============================================================================

def get_today_date_range() -> Tuple[date, date]:
    """Get date range for today."""
    today = date.today()
    return today, today


def get_yesterday_date_range() -> Tuple[date, date]:
    """Get date range for yesterday."""
    yesterday = date.today() - timedelta(days=1)
    return yesterday, yesterday


def get_current_week_date_range() -> Tuple[date, date]:
    """Get date range for current week (Monday to Sunday)."""
    today = date.today()
    # Get Monday of current week (weekday 0 = Monday)
    start_of_week = today - timedelta(days=today.weekday())
    # Get Sunday of current week
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def get_last_week_date_range() -> Tuple[date, date]:
    """Get date range for last week (Monday to Sunday)."""
    today = date.today()
    # Get Monday of last week
    start_of_last_week = today - timedelta(days=today.weekday() + 7)
    # Get Sunday of last week
    end_of_last_week = start_of_last_week + timedelta(days=6)
    return start_of_last_week, end_of_last_week


def get_current_month_date_range() -> Tuple[date, date]:
    """Get date range for current month."""
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    # Get last day of current month
    if today.month == 12:
        end_of_month = date(today.year, 12, 31)
    else:
        end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
    return start_of_month, end_of_month


def get_last_month_date_range() -> Tuple[date, date]:
    """Get date range for last month."""
    today = date.today()
    # Get first day of last month
    if today.month == 1:
        start_of_last_month = date(today.year - 1, 12, 1)
        end_of_last_month = date(today.year - 1, 12, 31)
    else:
        start_of_last_month = date(today.year, today.month - 1, 1)
        # Get last day of last month
        end_of_last_month = date(today.year, today.month, 1) - timedelta(days=1)
    return start_of_last_month, end_of_last_month


def get_date_range_by_type(range_type: str) -> Tuple[date, date]:
    """
    Get date range based on type.
    
    Args:
        range_type: 'today', 'yesterday', 'current_week', 'last_week', 
                   'current_month', 'last_month', or 'custom'
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if range_type == 'today':
        return get_today_date_range()
    elif range_type == 'yesterday':
        return get_yesterday_date_range()
    elif range_type == 'current_week':
        return get_current_week_date_range()
    elif range_type == 'last_week':
        return get_last_week_date_range()
    elif range_type == 'current_month':
        return get_current_month_date_range()
    elif range_type == 'last_month':
        return get_last_month_date_range()
    else:
        # Default to current month
        return get_current_month_date_range()


# ============================================================================
# Enhanced Payroll Report Functions with Transaction Data
# ============================================================================

def get_payroll_report_with_transactions(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    status_filter: Optional[str] = None
) -> List[Dict]:
    """
    Generate enhanced payroll report with transaction history.
    
    This function returns payroll entries for periods that overlap with the date range,
    along with the count of transactions and latest transaction date.
    
    Args:
        start_date: Start date of the report period
        end_date: End date of the report period
        department_id: Optional department filter (None for all departments)
        status_filter: Optional status filter (e.g., 'PENDING', 'VERIFIED')
    
    Returns:
        List of payroll entries with employee info and transaction counts
    """
    query = """
        SELECT 
            e.id as employee_id,
            e.employee_code,
            e.first_name,
            e.last_name,
            e.position,
            d.name as department_name,
            pp.id as period_id,
            pp.name as period_name,
            pp.start_date as period_start,
            pp.end_date as period_end,
            pe.id as entry_id,
            pe.basic_pay,
            pe.overtime_pay,
            pe.allowances,
            pe.holiday_pay,
            pe.vacation_sickleave,
            pe.salary_adjustment,
            pe.incentive_pay,
            pe.gross_pay,
            pe.sss_contrib,
            pe.philhealth_contrib,
            pe.pagibig_contrib,
            pe.withholding_tax,
            pe.late_deduction,
            pe.cash_advance,
            pe.undertime_deduction,
            pe.other_deductions,
            pe.total_deductions,
            pe.net_pay,
            pe.status as payroll_status,
            (SELECT COUNT(*) FROM payroll_transaction_history 
             WHERE payroll_entry_id = pe.id) as transaction_count,
            (SELECT MAX(transaction_date) FROM payroll_transaction_history 
             WHERE payroll_entry_id = pe.id) as last_transaction_date
        FROM payroll_entries pe
        JOIN employees e ON pe.employee_id = e.id
        LEFT JOIN departments d ON e.department_id = d.id
        JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
        WHERE e.is_active = 1
        -- Include any payroll period that overlaps the requested range
        AND pp.start_date <= %s
        AND pp.end_date >= %s
    """
    params = [end_date, start_date]
    
    if department_id:
        query += " AND e.department_id = %s"
        params.append(department_id)
    
    if status_filter:
        query += " AND pe.status = %s"
        params.append(status_filter)
    
    query += " ORDER BY e.last_name, e.first_name, pp.start_date DESC"
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def get_daily_payroll_summary(target_date: Optional[date] = None) -> Dict:
    """
    Get payroll summary for a specific day.
    
    Args:
        target_date: Date to get summary for (defaults to today)
    
    Returns:
        Dictionary with daily summary statistics
    """
    if target_date is None:
        target_date = date.today()
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Get payroll entries for periods that include this date
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT pe.employee_id) as total_employees,
                    COUNT(DISTINCT pe.id) as total_entries,
                    SUM(pe.gross_pay) as total_gross_pay,
                    SUM(pe.total_deductions) as total_deductions,
                    SUM(pe.net_pay) as total_net_pay,
                    COUNT(DISTINCT CASE WHEN pe.status = 'PENDING' THEN pe.id END) as pending_count,
                    COUNT(DISTINCT CASE WHEN pe.status = 'VERIFIED' THEN pe.id END) as verified_count,
                    COUNT(DISTINCT pp.id) as affected_periods
                FROM payroll_entries pe
                JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
                WHERE pp.start_date <= %s
                AND pp.end_date >= %s
            """, (target_date, target_date))
            summary = cur.fetchone()
            
            # Get transaction count for this date
            cur.execute("""
                SELECT COUNT(*) as daily_transactions
                FROM payroll_transaction_history
                WHERE DATE(transaction_date) = %s
            """, (target_date,))
            transaction_data = cur.fetchone()
            
            return {
                **summary,
                'target_date': target_date,
                'daily_transactions': transaction_data['daily_transactions'] if transaction_data else 0
            }


def get_weekly_payroll_summary(start_date: date, end_date: date) -> Dict:
    """
    Get payroll summary for a week.
    
    Args:
        start_date: Start of week
        end_date: End of week
    
    Returns:
        Dictionary with weekly summary statistics
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Get payroll entries for periods that overlap with this week
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT pe.employee_id) as total_employees,
                    COUNT(DISTINCT pe.id) as total_entries,
                    SUM(pe.gross_pay) as total_gross_pay,
                    SUM(pe.total_deductions) as total_deductions,
                    SUM(pe.net_pay) as total_net_pay,
                    COUNT(DISTINCT CASE WHEN pe.status = 'PENDING' THEN pe.id END) as pending_count,
                    COUNT(DISTINCT CASE WHEN pe.status = 'VERIFIED' THEN pe.id END) as verified_count,
                    COUNT(DISTINCT pp.id) as affected_periods
                FROM payroll_entries pe
                JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
                WHERE pp.start_date <= %s
                AND pp.end_date >= %s
            """, (end_date, start_date))
            summary = cur.fetchone()
            
            # Get transaction count for this week
            cur.execute("""
                SELECT COUNT(*) as weekly_transactions
                FROM payroll_transaction_history
                WHERE DATE(transaction_date) >= %s
                AND DATE(transaction_date) <= %s
            """, (start_date, end_date))
            transaction_data = cur.fetchone()
            
            return {
                **summary,
                'start_date': start_date,
                'end_date': end_date,
                'weekly_transactions': transaction_data['weekly_transactions'] if transaction_data else 0
            }


def get_monthly_payroll_summary(year: int, month: int) -> Dict:
    """
    Get payroll summary for a specific month.
    
    Args:
        year: Year
        month: Month (1-12)
    
    Returns:
        Dictionary with monthly summary statistics
    """
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Get payroll entries for periods that overlap with this month
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT pe.employee_id) as total_employees,
                    COUNT(DISTINCT pe.id) as total_entries,
                    SUM(pe.gross_pay) as total_gross_pay,
                    SUM(pe.total_deductions) as total_deductions,
                    SUM(pe.net_pay) as total_net_pay,
                    COUNT(DISTINCT CASE WHEN pe.status = 'PENDING' THEN pe.id END) as pending_count,
                    COUNT(DISTINCT CASE WHEN pe.status = 'VERIFIED' THEN pe.id END) as verified_count,
                    COUNT(DISTINCT pp.id) as affected_periods
                FROM payroll_entries pe
                JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
                WHERE pp.start_date <= %s
                AND pp.end_date >= %s
            """, (end_date, start_date))
            summary = cur.fetchone()
            
            # Get transaction count for this month
            cur.execute("""
                SELECT COUNT(*) as monthly_transactions
                FROM payroll_transaction_history
                WHERE DATE(transaction_date) >= %s
                AND DATE(transaction_date) <= %s
            """, (start_date, end_date))
            transaction_data = cur.fetchone()
            
            return {
                **summary,
                'year': year,
                'month': month,
                'start_date': start_date,
                'end_date': end_date,
                'monthly_transactions': transaction_data['monthly_transactions'] if transaction_data else 0
            }

