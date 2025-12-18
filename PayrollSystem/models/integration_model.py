"""
Centralized Data Integration Model for PROLY Payroll System.
Handles integration logging and data synchronization tracking.
Implements Solution 2: Centralized Data Integration.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
import logging

from .database import get_connection


logger = logging.getLogger(__name__)


def init_integration_tables():
    """Initialize integration logging tables."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                # Integration log table
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS integration_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        source_system VARCHAR(100) NOT NULL,
                        target_system VARCHAR(100) NOT NULL,
                        integration_type ENUM('HR_SYNC', 'TIMESHEET_SYNC', 'ACCOUNTING_SYNC', 'EMPLOYEE_UPDATE', 'ATTENDANCE_UPDATE') NOT NULL,
                        record_type VARCHAR(100) NOT NULL,
                        record_id VARCHAR(255),
                        action VARCHAR(50) NOT NULL,
                        status ENUM('SUCCESS', 'FAILED', 'PENDING') NOT NULL,
                        details TEXT,
                        error_message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_source_target (source_system, target_system),
                        INDEX idx_integration_type (integration_type),
                        INDEX idx_status (status),
                        INDEX idx_created_at (created_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )

                conn.commit()
                logger.info("Integration tables initialized")
            except Exception as e:
                conn.rollback()
                logger.exception("Failed to initialize integration tables: %s", e)
                raise


def log_integration(
    source_system: str,
    target_system: str,
    integration_type: str,
    record_type: str,
    action: str,
    status: str,
    record_id: Optional[str] = None,
    details: Optional[str] = None,
    error_message: Optional[str] = None
) -> int:
    """
    Log an integration activity.
    
    Args:
        source_system: Source system name (e.g., 'HR_SYSTEM', 'TIMESHEET_SYSTEM')
        target_system: Target system name (e.g., 'PAYROLL_SYSTEM')
        integration_type: Type of integration
        record_type: Type of record being synced (e.g., 'EMPLOYEE', 'ATTENDANCE')
        action: Action performed (e.g., 'CREATE', 'UPDATE', 'DELETE', 'SYNC')
        status: Status of integration ('SUCCESS', 'FAILED', 'PENDING')
        record_id: ID of the record being synced
        details: Additional details about the integration
        error_message: Error message if status is 'FAILED'
    
    Returns:
        ID of the created log entry
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """INSERT INTO integration_logs 
                       (source_system, target_system, integration_type, record_type, record_id, 
                        action, status, details, error_message)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        source_system,
                        target_system,
                        integration_type,
                        record_type,
                        record_id,
                        action,
                        status,
                        details,
                        error_message,
                    ),
                )
                conn.commit()
                return cur.lastrowid
            except Exception as e:
                conn.rollback()
                logger.exception("Failed to log integration: %s", e)
                raise


def get_integration_logs(
    source_system: Optional[str] = None,
    target_system: Optional[str] = None,
    integration_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Dict]:
    """
    Get integration logs with optional filters.
    
    Args:
        source_system: Filter by source system
        target_system: Filter by target system
        integration_type: Filter by integration type
        status: Filter by status
        limit: Maximum number of records to return
    
    Returns:
        List of integration log records
    """
    query = "SELECT * FROM integration_logs WHERE 1=1"
    params = []
    
    if source_system:
        query += " AND source_system = %s"
        params.append(source_system)
    
    if target_system:
        query += " AND target_system = %s"
        params.append(target_system)
    
    if integration_type:
        query += " AND integration_type = %s"
        params.append(integration_type)
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def sync_employee_data(employee_id: int, source: str = 'HR_SYSTEM') -> bool:
    """
    Simulate employee data synchronization from HR system.
    
    Args:
        employee_id: ID of employee to sync
        source: Source system name
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # In a real implementation, this would fetch data from external HR system
        # and update the payroll database
        
        log_integration(
            source_system=source,
            target_system='PAYROLL_SYSTEM',
            integration_type='HR_SYNC',
            record_type='EMPLOYEE',
            action='SYNC',
            status='SUCCESS',
            record_id=str(employee_id),
            details=f"Employee {employee_id} data synchronized from {source}"
        )
        return True
    except Exception as e:
        log_integration(
            source_system=source,
            target_system='PAYROLL_SYSTEM',
            integration_type='HR_SYNC',
            record_type='EMPLOYEE',
            action='SYNC',
            status='FAILED',
            record_id=str(employee_id),
            error_message=str(e)
        )
        return False


def sync_attendance_data(employee_id: int, period_start: datetime, period_end: datetime) -> bool:
    """
    Simulate attendance data synchronization from timesheet system.
    
    Args:
        employee_id: ID of employee
        period_start: Start of period
        period_end: End of period
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # In a real implementation, this would fetch attendance data from external system
        log_integration(
            source_system='TIMESHEET_SYSTEM',
            target_system='PAYROLL_SYSTEM',
            integration_type='TIMESHEET_SYNC',
            record_type='ATTENDANCE',
            action='SYNC',
            status='SUCCESS',
            record_id=str(employee_id),
            details=f"Attendance data synced for employee {employee_id} from {period_start} to {period_end}"
        )
        return True
    except Exception as e:
        log_integration(
            source_system='TIMESHEET_SYSTEM',
            target_system='PAYROLL_SYSTEM',
            integration_type='TIMESHEET_SYNC',
            record_type='ATTENDANCE',
            action='SYNC',
            status='FAILED',
            record_id=str(employee_id),
            error_message=str(e)
        )
        return False

