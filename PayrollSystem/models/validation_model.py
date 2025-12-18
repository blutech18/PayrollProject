"""
Data Validation Model for PROLY Payroll System.
Provides comprehensive validation rules for all data inputs.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple


def validate_employee_code(employee_code: str) -> Tuple[bool, str]:
    """
    Validate employee code format.
    
    Returns:
        (is_valid, error_message)
    """
    if not employee_code:
        return False, "Employee code is required"
    
    if len(employee_code) < 3 or len(employee_code) > 30:
        return False, "Employee code must be between 3 and 30 characters"
    
    if not re.match(r'^[A-Z0-9\-_]+$', employee_code.upper()):
        return False, "Employee code can only contain letters, numbers, hyphens, and underscores"
    
    return True, ""


def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, str]:
    """
    Validate name fields (first name, last name).
    
    Returns:
        (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, f"{field_name} is required"
    
    if len(name.strip()) < 2:
        return False, f"{field_name} must be at least 2 characters"
    
    if len(name.strip()) > 100:
        return False, f"{field_name} must not exceed 100 characters"
    
    if not re.match(r'^[A-Za-z\s\-\'\.]+$', name):
        return False, f"{field_name} can only contain letters, spaces, hyphens, apostrophes, and periods"
    
    return True, ""


def validate_salary(salary: float) -> Tuple[bool, str]:
    """
    Validate salary amount.
    
    Returns:
        (is_valid, error_message)
    """
    if salary is None:
        return False, "Salary is required"
    
    if salary < 0:
        return False, "Salary cannot be negative"
    
    if salary > 1000000:
        return False, "Salary exceeds maximum allowed amount (PHP 1,000,000)"
    
    return True, ""


def validate_government_id(id_number: str, id_type: str) -> Tuple[bool, str]:
    """
    Validate government ID numbers (SSS, PhilHealth, Pag-IBIG, TIN).
    
    Returns:
        (is_valid, error_message)
    """
    if not id_number:
        return True, ""  # Optional field
    
    id_number = id_number.strip()
    
    if id_type == "SSS":
        # SSS format: XX-XXXXXXX-X
        if not re.match(r'^\d{2}-\d{7}-\d{1}$', id_number):
            return False, "SSS number must be in format XX-XXXXXXX-X"
    
    elif id_type == "PhilHealth":
        # PhilHealth format: XX-XXXXXXXXX-X
        if not re.match(r'^\d{2}-\d{9}-\d{1}$', id_number):
            return False, "PhilHealth number must be in format XX-XXXXXXXXX-X"
    
    elif id_type == "Pag-IBIG":
        # Pag-IBIG format: XXXX-XXXX-XXXX
        if not re.match(r'^\d{4}-\d{4}-\d{4}$', id_number):
            return False, "Pag-IBIG number must be in format XXXX-XXXX-XXXX"
    
    elif id_type == "TIN":
        # TIN format: XXX-XXX-XXX-XXX
        if not re.match(r'^\d{3}-\d{3}-\d{3}-\d{3}$', id_number):
            return False, "TIN must be in format XXX-XXX-XXX-XXX"
    
    return True, ""


def validate_date(date_value: date, field_name: str = "Date", allow_future: bool = True) -> Tuple[bool, str]:
    """
    Validate date fields.
    
    Returns:
        (is_valid, error_message)
    """
    if not date_value:
        return False, f"{field_name} is required"
    
    if not allow_future and date_value > date.today():
        return False, f"{field_name} cannot be in the future"
    
    # Check reasonable date range (not before 1900, not too far in future)
    if date_value.year < 1900:
        return False, f"{field_name} is too far in the past"
    
    if date_value.year > 2100:
        return False, f"{field_name} is too far in the future"
    
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.
    
    Returns:
        (is_valid, error_message)
    """
    if not username or not username.strip():
        return False, "Username is required"
    
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username.strip()) > 50:
        return False, "Username must not exceed 50 characters"
    
    if not re.match(r'^[A-Za-z0-9_\-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    return True, ""


def validate_password(password: str, min_length: int = 4) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if len(password) > 128:
        return False, "Password is too long (maximum 128 characters)"
    
    return True, ""


def validate_compliance_file(file_path: str, file_type: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Validate compliance file format and content.
    
    Returns:
        (is_valid, error_message, parsed_data)
    """
    import os
    
    if not os.path.exists(file_path):
        return False, "File does not exist", None
    
    # Check file size (max 10MB)
    file_size = os.path.getsize(file_path)
    if file_size > 10 * 1024 * 1024:  # 10MB
        return False, "File size exceeds 10MB limit", None
    
    if file_size == 0:
        return False, "File is empty", None
    
    # Try to parse the file
    try:
        from .compliance_parser import parse_compliance_file
        parsed_data = parse_compliance_file(file_type, file_path)
        
        if parsed_data and parsed_data.get('brackets'):
            return True, "File is valid", parsed_data
        else:
            return False, "File format is not recognized or file is empty", None
    except Exception as e:
        return False, f"Error parsing file: {str(e)}", None


def validate_payroll_period(start_date: date, end_date: date) -> Tuple[bool, str]:
    """
    Validate payroll period dates.
    
    Returns:
        (is_valid, error_message)
    """
    if not start_date or not end_date:
        return False, "Both start date and end date are required"
    
    if end_date <= start_date:
        return False, "End date must be after start date"
    
    # Check period length (reasonable range: 1 day to 5 years for flexibility)
    days_diff = (end_date - start_date).days
    if days_diff < 1:
        return False, "Period must be at least 1 day"
    
    if days_diff > 1825:  # 5 years - more flexible for long-term reports
        return False, "Period cannot exceed 5 years"
    
    return True, ""


def validate_payroll_amounts(amounts: Dict[str, float]) -> Tuple[bool, str]:
    """
    Validate payroll calculation amounts.
    
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['basic_pay', 'gross_pay', 'total_deductions', 'net_pay']
    
    for field in required_fields:
        if field not in amounts:
            return False, f"{field} is required"
        
        if amounts[field] < 0:
            return False, f"{field} cannot be negative"
    
    # Validate gross pay calculation
    earnings = amounts.get('basic_pay', 0) + amounts.get('overtime_pay', 0) + \
               amounts.get('allowances', 0) + amounts.get('holiday_pay', 0) + \
               amounts.get('vacation_sickleave', 0) + amounts.get('salary_adjustment', 0) + \
               amounts.get('incentive_pay', 0)
    
    gross_pay = amounts.get('gross_pay', 0)
    if abs(earnings - gross_pay) > 0.01:  # Allow small rounding differences
        return False, f"Gross pay calculation mismatch. Expected: {earnings:.2f}, Got: {gross_pay:.2f}"
    
    # Validate net pay calculation
    calculated_net = gross_pay - amounts.get('total_deductions', 0)
    net_pay = amounts.get('net_pay', 0)
    if abs(calculated_net - net_pay) > 0.01:
        return False, f"Net pay calculation mismatch. Expected: {calculated_net:.2f}, Got: {net_pay:.2f}"
    
    return True, ""

