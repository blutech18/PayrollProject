"""
Payroll Computation Model - Dynamic Payroll Calculation using Attendance Data
Implements hourly-based payroll computation with overtime, night differential, and holiday pay.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from .database import get_connection
from .timekeeping_model import get_company_work_settings
from .compliance_model import calculate_compliance_deductions
from .employee_model import get_employee_by_id
from .payroll_transaction_history import log_payroll_transaction
import logging

logger = logging.getLogger(__name__)


def calculate_hourly_rate_from_salary(base_salary: float, salary_type: str) -> float:
    """
    Convert base salary to hourly rate based on salary type.
    
    Args:
        base_salary: Base salary amount
        salary_type: 'MONTHLY', 'HOURLY', or 'DAILY'
    
    Returns:
        Hourly rate
    """
    if salary_type == 'HOURLY':
        return base_salary
    elif salary_type == 'DAILY':
        # Assume 8 hours per day
        return base_salary / 8.0
    elif salary_type == 'MONTHLY':
        # Assume 22 working days per month, 8 hours per day = 176 hours
        return base_salary / 176.0
    else:
        # Default to monthly calculation
        return base_salary / 176.0


def get_attendance_for_period(employee_id: int, start_date: date, end_date: date) -> List[Dict]:
    """Get attendance records for an employee within a payroll period."""
    query = """
        SELECT * FROM attendance
        WHERE employee_id = %s 
        AND attendance_date >= %s 
        AND attendance_date <= %s
        AND status IN ('PRESENT', 'LATE')
        ORDER BY attendance_date
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (employee_id, start_date, end_date))
            return cur.fetchall()


def calculate_payroll_for_employee(employee_id: int, period_id: int, 
                                   start_date: date, end_date: date) -> Dict:
    """
    Calculate payroll for an employee based on attendance data.
    
    Args:
        employee_id: Employee ID
        period_id: Payroll period ID
        start_date: Period start date
        end_date: Period end date
    
    Returns:
        Dictionary with all payroll calculations
    """
    employee = get_employee_by_id(employee_id)
    if not employee:
        raise ValueError(f"Employee {employee_id} not found")
    
    settings = get_company_work_settings()
    
    # Get hourly rate
    if employee.hourly_rate > 0:
        hourly_rate = employee.hourly_rate
    else:
        hourly_rate = calculate_hourly_rate_from_salary(employee.base_salary, employee.salary_type)
    
    # Get attendance records for the period
    attendance_records = get_attendance_for_period(employee_id, start_date, end_date)
    
    # Initialize totals
    total_regular_hours = 0.0
    total_overtime_hours = 0.0
    total_night_diff_hours = 0.0
    total_late_minutes = 0
    total_undertime_minutes = 0
    holiday_hours = 0.0
    rest_day_hours = 0.0
    
    # Process each attendance record
    for record in attendance_records:
        regular_hours = float(record.get('regular_hours', 0))
        overtime_hours = float(record.get('overtime_hours', 0))
        night_diff_hours = float(record.get('night_differential_hours', 0))
        late_minutes = int(record.get('late_minutes', 0))
        undertime_minutes = int(record.get('undertime_minutes', 0))
        is_holiday = bool(record.get('is_holiday', 0))
        is_rest_day = bool(record.get('is_rest_day', 0))
        
        total_regular_hours += regular_hours
        total_overtime_hours += overtime_hours
        total_night_diff_hours += night_diff_hours
        total_late_minutes += late_minutes
        total_undertime_minutes += undertime_minutes
        
        if is_holiday:
            holiday_hours += regular_hours
        if is_rest_day:
            rest_day_hours += regular_hours
    
    # Calculate basic pay (regular hours * hourly rate)
    basic_pay = total_regular_hours * hourly_rate
    
    # Calculate overtime pay
    overtime_rate_multiplier = settings.get('overtime_rate_multiplier', 1.25)
    overtime_pay = total_overtime_hours * hourly_rate * overtime_rate_multiplier
    
    # Calculate night differential pay
    night_diff_rate = settings.get('night_differential_rate', 0.10)
    night_differential_pay = total_night_diff_hours * hourly_rate * night_diff_rate
    
    # Calculate holiday pay
    holiday_rate_multiplier = settings.get('holiday_rate_multiplier', 2.0)
    holiday_pay = holiday_hours * hourly_rate * holiday_rate_multiplier
    
    # Calculate rest day pay
    rest_day_rate_multiplier = settings.get('rest_day_rate_multiplier', 1.3)
    rest_day_pay = rest_day_hours * hourly_rate * rest_day_rate_multiplier
    
    # Calculate late and undertime deductions
    late_deduction_rate = hourly_rate / 60.0  # Per minute
    late_deduction = total_late_minutes * late_deduction_rate
    
    undertime_deduction_rate = hourly_rate / 60.0  # Per minute
    undertime_deduction = total_undertime_minutes * undertime_deduction_rate
    
    # Other earnings (allowances, incentives, etc.) - can be set manually
    allowances = 0.0
    vacation_sickleave = 0.0
    salary_adjustment = 0.0
    incentive_pay = 0.0
    
    # Calculate gross pay
    gross_pay = (basic_pay + overtime_pay + night_differential_pay + holiday_pay + 
                 rest_day_pay + allowances + vacation_sickleave + 
                 salary_adjustment + incentive_pay)
    
    # Calculate compliance deductions
    period_date = start_date  # Use start date for compliance rate lookup
    compliance_deductions = calculate_compliance_deductions(gross_pay, period_date)
    
    sss_contrib = compliance_deductions['sss']
    philhealth_contrib = compliance_deductions['philhealth']
    pagibig_contrib = compliance_deductions['pagibig']
    withholding_tax = compliance_deductions['tax']
    
    # Other deductions (can be set manually)
    cash_advance = 0.0
    other_deductions = 0.0
    
    # Total deductions
    total_deductions = (sss_contrib + philhealth_contrib + pagibig_contrib + 
                       withholding_tax + late_deduction + cash_advance + 
                       undertime_deduction + other_deductions)
    
    # Net pay
    net_pay = gross_pay - total_deductions
    
    return {
        'employee_id': employee_id,
        'payroll_period_id': period_id,
        'basic_pay': round(basic_pay, 2),
        'overtime_pay': round(overtime_pay, 2),
        'allowances': round(allowances, 2),
        'holiday_pay': round(holiday_pay, 2),
        'vacation_sickleave': round(vacation_sickleave, 2),
        'salary_adjustment': round(salary_adjustment, 2),
        'incentive_pay': round(incentive_pay, 2),
        'night_differential_pay': round(night_differential_pay, 2),
        'rest_day_pay': round(rest_day_pay, 2),
        'gross_pay': round(gross_pay, 2),
        'sss_contrib': round(sss_contrib, 2),
        'philhealth_contrib': round(philhealth_contrib, 2),
        'pagibig_contrib': round(pagibig_contrib, 2),
        'withholding_tax': round(withholding_tax, 2),
        'late_deduction': round(late_deduction, 2),
        'cash_advance': round(cash_advance, 2),
        'undertime_deduction': round(undertime_deduction, 2),
        'other_deductions': round(other_deductions, 2),
        'total_deductions': round(total_deductions, 2),
        'net_pay': round(net_pay, 2),
        'status': 'PENDING',
        # Additional info
        'total_regular_hours': total_regular_hours,
        'total_overtime_hours': total_overtime_hours,
        'total_night_diff_hours': total_night_diff_hours,
        'total_late_minutes': total_late_minutes,
        'total_undertime_minutes': total_undertime_minutes,
    }


def compute_payroll_period(period_id: int) -> Dict[str, any]:
    """
    Compute payroll for all active employees in a period.
    
    Args:
        period_id: Payroll period ID
    
    Returns:
        Dictionary with computation results
    """
    # Get period details
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT * FROM payroll_periods WHERE id = %s
            """, (period_id,))
            period = cur.fetchone()
            
            if not period:
                raise ValueError(f"Payroll period {period_id} not found")
            
            start_date = period['start_date']
            end_date = period['end_date']
            
            # Get all active employees
            cur.execute("""
                SELECT id FROM employees WHERE is_active = 1
            """)
            employees = cur.fetchall()
    
    results = {
        'period_id': period_id,
        'start_date': start_date,
        'end_date': end_date,
        'total_employees': len(employees),
        'computed': 0,
        'errors': []
    }
    
    # Compute payroll for each employee
    for emp in employees:
        try:
            payroll_data = calculate_payroll_for_employee(
                emp['id'], period_id, start_date, end_date
            )
            
            # Save or update payroll entry
            _save_payroll_entry(payroll_data)
            results['computed'] += 1
        except Exception as e:
            results['errors'].append({
                'employee_id': emp['id'],
                'error': str(e)
            })
    
    return results


def _save_payroll_entry(payroll_data: Dict, changed_by: int = None) -> int:
    """Save or update a payroll entry with transaction logging."""
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Check if entry already exists
            cur.execute("""
                SELECT id, gross_pay, net_pay, status FROM payroll_entries 
                WHERE payroll_period_id = %s AND employee_id = %s
            """, (payroll_data['payroll_period_id'], payroll_data['employee_id']))
            existing = cur.fetchone()
            
            if existing:
                # Store previous values for transaction history
                previous_gross_pay = float(existing['gross_pay']) if existing.get('gross_pay') else 0.0
                previous_net_pay = float(existing['net_pay']) if existing.get('net_pay') else 0.0
                previous_status = existing.get('status', 'PENDING')
                
                # Update existing entry
                cur.execute("""
                    UPDATE payroll_entries SET
                        basic_pay = %s,
                        overtime_pay = %s,
                        allowances = %s,
                        holiday_pay = %s,
                        vacation_sickleave = %s,
                        salary_adjustment = %s,
                        incentive_pay = %s,
                        gross_pay = %s,
                        sss_contrib = %s,
                        philhealth_contrib = %s,
                        pagibig_contrib = %s,
                        withholding_tax = %s,
                        late_deduction = %s,
                        cash_advance = %s,
                        undertime_deduction = %s,
                        other_deductions = %s,
                        total_deductions = %s,
                        net_pay = %s,
                        status = %s
                    WHERE id = %s
                """, (
                    payroll_data['basic_pay'],
                    payroll_data['overtime_pay'],
                    payroll_data['allowances'],
                    payroll_data['holiday_pay'],
                    payroll_data['vacation_sickleave'],
                    payroll_data['salary_adjustment'],
                    payroll_data['incentive_pay'],
                    payroll_data['gross_pay'],
                    payroll_data['sss_contrib'],
                    payroll_data['philhealth_contrib'],
                    payroll_data['pagibig_contrib'],
                    payroll_data['withholding_tax'],
                    payroll_data['late_deduction'],
                    payroll_data['cash_advance'],
                    payroll_data['undertime_deduction'],
                    payroll_data['other_deductions'],
                    payroll_data['total_deductions'],
                    payroll_data['net_pay'],
                    payroll_data['status'],
                    existing['id']
                ))
                conn.commit()
                entry_id = existing['id']
                
                # Log transaction
                try:
                    log_payroll_transaction(
                        payroll_entry_id=entry_id,
                        payroll_period_id=payroll_data['payroll_period_id'],
                        employee_id=payroll_data['employee_id'],
                        transaction_type='UPDATED',
                        previous_status=previous_status,
                        new_status=payroll_data['status'],
                        previous_gross_pay=previous_gross_pay,
                        new_gross_pay=payroll_data['gross_pay'],
                        previous_net_pay=previous_net_pay,
                        new_net_pay=payroll_data['net_pay'],
                        changed_by=changed_by,
                        notes=f"Payroll recomputed with {payroll_data.get('total_regular_hours', 0):.2f} regular hours"
                    )
                except Exception as e:
                    logger.exception(f"Failed to log transaction for payroll entry update: {e}")
                
                return entry_id
            else:
                # Insert new entry
                cur.execute("""
                    INSERT INTO payroll_entries (
                        payroll_period_id, employee_id,
                        basic_pay, overtime_pay, allowances,
                        holiday_pay, vacation_sickleave, salary_adjustment, incentive_pay,
                        gross_pay,
                        sss_contrib, philhealth_contrib, pagibig_contrib, withholding_tax,
                        late_deduction, cash_advance, undertime_deduction, other_deductions,
                        total_deductions, net_pay, status
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    payroll_data['payroll_period_id'],
                    payroll_data['employee_id'],
                    payroll_data['basic_pay'],
                    payroll_data['overtime_pay'],
                    payroll_data['allowances'],
                    payroll_data['holiday_pay'],
                    payroll_data['vacation_sickleave'],
                    payroll_data['salary_adjustment'],
                    payroll_data['incentive_pay'],
                    payroll_data['gross_pay'],
                    payroll_data['sss_contrib'],
                    payroll_data['philhealth_contrib'],
                    payroll_data['pagibig_contrib'],
                    payroll_data['withholding_tax'],
                    payroll_data['late_deduction'],
                    payroll_data['cash_advance'],
                    payroll_data['undertime_deduction'],
                    payroll_data['other_deductions'],
                    payroll_data['total_deductions'],
                    payroll_data['net_pay'],
                    payroll_data['status']
                ))
                conn.commit()
                entry_id = cur.lastrowid
                
                # Log transaction
                try:
                    log_payroll_transaction(
                        payroll_entry_id=entry_id,
                        payroll_period_id=payroll_data['payroll_period_id'],
                        employee_id=payroll_data['employee_id'],
                        transaction_type='CREATED',
                        new_status=payroll_data['status'],
                        new_gross_pay=payroll_data['gross_pay'],
                        new_net_pay=payroll_data['net_pay'],
                        changed_by=changed_by,
                        notes=f"Initial payroll computation with {payroll_data.get('total_regular_hours', 0):.2f} regular hours"
                    )
                except Exception as e:
                    logger.exception(f"Failed to log transaction for new payroll entry: {e}")
                
                return entry_id

