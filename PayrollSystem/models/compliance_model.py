"""
Compliance Management Model for PROLY Payroll System.
Handles storage, versioning, and retrieval of compliance files (BIR, SSS, PhilHealth, Pag-IBIG).
Implements Solution 1: Configurable Compliance Management.
"""

from __future__ import annotations

import os
import shutil
from datetime import date, datetime
from typing import Dict, List, Optional

from .database import get_connection


def get_compliance_uploads_dir() -> str:
    """Get the directory for storing compliance uploads."""
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "compliance")
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir


def upload_compliance_file(file_type: str, file_path: str, effective_from: date, version: int = 1) -> int:
    """
    Upload and store a compliance file with version control.
    
    Args:
        file_type: Type of compliance file ('BIR Tax', 'SSS', 'PHILHEALTH', 'PAGIBIG')
        file_path: Path to the uploaded file
        effective_from: Date when this version becomes effective
        version: Version number (auto-incremented if not provided)
    
    Returns:
        ID of the created record
    """
    uploads_dir = get_compliance_uploads_dir()
    
    # Map file types to database types
    type_mapping = {
        'BIR Tax': 'TAX',
        'SSS Contributions': 'SSS',
        'PhilHealth Rates': 'PHILHEALTH',
        'Pag-IBIG Rates': 'PAGIBIG'
    }
    
    db_type = type_mapping.get(file_type, file_type.upper())
    
    # Get next version if not provided
    if version == 1:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if db_type == 'TAX':
                    cur.execute("SELECT MAX(version) FROM tax_tables")
                else:
                    cur.execute("SELECT MAX(version) FROM contribution_tables WHERE type = %s", (db_type,))
                result = cur.fetchone()
                version = (result[0] or 0) + 1
    
    # Copy file to uploads directory
    file_name = f"{db_type}_{effective_from.strftime('%Y%m%d')}_v{version}{os.path.splitext(file_path)[1]}"
    dest_path = os.path.join(uploads_dir, file_name)
    shutil.copy2(file_path, dest_path)
    
    # Store in database
    with get_connection() as conn:
        with conn.cursor() as cur:
            if db_type == 'TAX':
                cur.execute(
                    """INSERT INTO tax_tables (name, effective_from, version, file_path)
                       VALUES (%s, %s, %s, %s)""",
                    (file_type, effective_from, version, dest_path)
                )
            else:
                cur.execute(
                    """INSERT INTO contribution_tables (type, effective_from, version, file_path)
                       VALUES (%s, %s, %s, %s)""",
                    (db_type, effective_from, version, dest_path)
                )
            conn.commit()
            return cur.lastrowid


def get_latest_compliance_file(file_type: str) -> Optional[Dict]:
    """
    Get the latest version of a compliance file.
    
    Args:
        file_type: Type of compliance file ('BIR Tax', 'SSS', 'PHILHEALTH', 'PAGIBIG')
    
    Returns:
        Dictionary with file information or None
    """
    type_mapping = {
        'BIR Tax': 'TAX',
        'SSS Contributions': 'SSS',
        'PhilHealth Rates': 'PHILHEALTH',
        'Pag-IBIG Rates': 'PAGIBIG'
    }
    
    db_type = type_mapping.get(file_type, file_type.upper())
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            if db_type == 'TAX':
                cur.execute(
                    """SELECT * FROM tax_tables 
                       WHERE effective_from <= CURDATE()
                       ORDER BY effective_from DESC, version DESC
                       LIMIT 1"""
                )
            else:
                cur.execute(
                    """SELECT * FROM contribution_tables 
                       WHERE type = %s AND effective_from <= CURDATE()
                       ORDER BY effective_from DESC, version DESC
                       LIMIT 1""",
                    (db_type,)
                )
            return cur.fetchone()


def get_all_compliance_files(file_type: Optional[str] = None) -> List[Dict]:
    """
    Get all compliance files, optionally filtered by type.
    
    Args:
        file_type: Optional filter by file type
    
    Returns:
        List of compliance file records
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            if file_type:
                type_mapping = {
                    'BIR Tax': 'TAX',
                    'SSS Contributions': 'SSS',
                    'PhilHealth Rates': 'PHILHEALTH',
                    'Pag-IBIG Rates': 'PAGIBIG'
                }
                db_type = type_mapping.get(file_type, file_type.upper())
                
                if db_type == 'TAX':
                    cur.execute("SELECT * FROM tax_tables ORDER BY effective_from DESC, version DESC")
                else:
                    cur.execute(
                        "SELECT * FROM contribution_tables WHERE type = %s ORDER BY effective_from DESC, version DESC",
                        (db_type,)
                    )
            else:
                # Get all files
                cur.execute("SELECT * FROM tax_tables ORDER BY effective_from DESC, version DESC")
                tax_files = cur.fetchall()
                cur.execute("SELECT * FROM contribution_tables ORDER BY effective_from DESC, version DESC")
                contrib_files = cur.fetchall()
                return tax_files + contrib_files
            
            return cur.fetchall()


def calculate_compliance_deductions(gross_pay: float, period_date: date) -> Dict[str, float]:
    """
    Calculate compliance deductions (SSS, PhilHealth, Pag-IBIG, Tax) using latest rates.
    Parses uploaded compliance files if available, otherwise uses default rates.
    
    Args:
        gross_pay: Gross pay amount
        period_date: Date for which to calculate (uses effective rates for this date)
    
    Returns:
        Dictionary with deduction amounts
    """
    from .compliance_parser import parse_compliance_file
    
    # Get latest compliance files
    sss_file = get_latest_compliance_file('SSS Contributions')
    philhealth_file = get_latest_compliance_file('PhilHealth Rates')
    pagibig_file = get_latest_compliance_file('Pag-IBIG Rates')
    tax_file = get_latest_compliance_file('BIR Tax')
    
    # Default calculations (fallback if no files uploaded or parsing fails)
    deductions = {
        'sss': 0.0,
        'philhealth': 0.0,
        'pagibig': 0.0,
        'tax': 0.0
    }
    
    # SSS Calculation
    if sss_file and sss_file.get('file_path'):
        parsed_data = parse_compliance_file('SSS Contributions', sss_file['file_path'])
        if parsed_data and parsed_data.get('brackets'):
            # Find matching bracket
            for bracket in parsed_data['brackets']:
                if bracket['min'] <= gross_pay <= bracket['max']:
                    deductions['sss'] = bracket['employee_share']
                    break
        else:
            # Fallback to default rates
            if gross_pay <= 3250:
                deductions['sss'] = 135.0
            elif gross_pay <= 24750:
                deductions['sss'] = min(gross_pay * 0.045, 1125.0)
            else:
                deductions['sss'] = 1125.0
    else:
        # Use default rates
        if gross_pay <= 3250:
            deductions['sss'] = 135.0
        elif gross_pay <= 24750:
            deductions['sss'] = min(gross_pay * 0.045, 1125.0)
        else:
            deductions['sss'] = 1125.0
    
    # PhilHealth Calculation
    if philhealth_file and philhealth_file.get('file_path'):
        parsed_data = parse_compliance_file('PhilHealth Rates', philhealth_file['file_path'])
        if parsed_data and parsed_data.get('brackets'):
            # Find matching bracket
            for bracket in parsed_data['brackets']:
                if bracket['min'] <= gross_pay <= bracket['max']:
                    if bracket.get('employee_fixed'):
                        deductions['philhealth'] = bracket['employee_fixed']
                    elif bracket.get('employee_rate'):
                        deductions['philhealth'] = gross_pay * bracket['employee_rate']
                    break
        else:
            # Fallback to default rates
            if gross_pay <= 10000:
                deductions['philhealth'] = 300.0
            elif gross_pay <= 80000:
                deductions['philhealth'] = gross_pay * 0.03
            else:
                deductions['philhealth'] = 2400.0
    else:
        # Use default rates
        if gross_pay <= 10000:
            deductions['philhealth'] = 300.0
        elif gross_pay <= 80000:
            deductions['philhealth'] = gross_pay * 0.03
        else:
            deductions['philhealth'] = 2400.0
    
    # Pag-IBIG Calculation
    if pagibig_file and pagibig_file.get('file_path'):
        parsed_data = parse_compliance_file('Pag-IBIG Rates', pagibig_file['file_path'])
        if parsed_data and parsed_data.get('brackets'):
            max_contrib = parsed_data.get('max_contribution', 100.0)
            # Find matching bracket
            for bracket in parsed_data['brackets']:
                if bracket['min'] <= gross_pay <= bracket['max']:
                    if bracket.get('employee_rate'):
                        deductions['pagibig'] = min(gross_pay * bracket['employee_rate'], max_contrib)
                    break
        else:
            # Fallback to default rates
            if gross_pay <= 1500:
                deductions['pagibig'] = gross_pay * 0.01
            else:
                deductions['pagibig'] = min(gross_pay * 0.02, 100.0)
    else:
        # Use default rates
        if gross_pay <= 1500:
            deductions['pagibig'] = gross_pay * 0.01
        else:
            deductions['pagibig'] = min(gross_pay * 0.02, 100.0)
    
    # Tax Calculation (BIR Withholding Tax)
    taxable = gross_pay - (deductions['sss'] + deductions['philhealth'] + deductions['pagibig'])
    if tax_file and tax_file.get('file_path'):
        parsed_data = parse_compliance_file('BIR Tax', tax_file['file_path'])
        if parsed_data and parsed_data.get('brackets'):
            # Find matching tax bracket
            for bracket in parsed_data['brackets']:
                if bracket['from'] <= taxable < bracket['to']:
                    excess = taxable - bracket['from']
                    deductions['tax'] = bracket['base_tax'] + (excess * bracket['rate'])
                    break
        else:
            # Fallback to default tax brackets
            if taxable <= 20833:
                deductions['tax'] = 0.0
            elif taxable <= 33332:
                deductions['tax'] = (taxable - 20833) * 0.20
            elif taxable <= 66666:
                deductions['tax'] = 2500 + (taxable - 33332) * 0.25
            elif taxable <= 166666:
                deductions['tax'] = 10833 + (taxable - 66666) * 0.30
            else:
                deductions['tax'] = 40833 + (taxable - 166666) * 0.32
    else:
        # Use default tax brackets
        if taxable <= 20833:
            deductions['tax'] = 0.0
        elif taxable <= 33332:
            deductions['tax'] = (taxable - 20833) * 0.20
        elif taxable <= 66666:
            deductions['tax'] = 2500 + (taxable - 33332) * 0.25
        elif taxable <= 166666:
            deductions['tax'] = 10833 + (taxable - 66666) * 0.30
        else:
            deductions['tax'] = 40833 + (taxable - 166666) * 0.32
    
    return deductions

