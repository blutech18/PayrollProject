"""
Leave Balance Model for PROLY Payroll System.
Tracks employee leave balances (vacation, sick leave, etc.).
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional
import logging

from .database import get_connection


logger = logging.getLogger(__name__)


def init_leave_balance_tables():
    """Initialize leave balance tables."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                # Leave types table
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS leave_types (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        max_days_per_year INT DEFAULT 0,
                        is_paid TINYINT(1) DEFAULT 1,
                        description TEXT
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )

                # Leave balances table
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS leave_balances (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        employee_id INT NOT NULL,
                        leave_type_id INT NOT NULL,
                        year INT NOT NULL,
                        total_allocated DECIMAL(5,2) DEFAULT 0,
                        used DECIMAL(5,2) DEFAULT 0,
                        pending DECIMAL(5,2) DEFAULT 0,
                        balance DECIMAL(5,2) DEFAULT 0,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES employees(id),
                        FOREIGN KEY (leave_type_id) REFERENCES leave_types(id),
                        UNIQUE KEY unique_employee_leave_year (employee_id, leave_type_id, year)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                    """
                )

                # Seed default leave types
                cur.execute("SELECT COUNT(*) FROM leave_types")
                if cur.fetchone()[0] == 0:
                    cur.executemany(
                        "INSERT INTO leave_types (name, max_days_per_year, is_paid, description) VALUES (%s, %s, %s, %s)",
                        [
                            ("Vacation Leave", 15, 1, "Annual vacation leave"),
                            ("Sick Leave", 15, 1, "Medical leave"),
                            ("Emergency Leave", 5, 1, "Emergency situations"),
                            ("Maternity Leave", 105, 1, "Maternity leave"),
                            ("Paternity Leave", 7, 1, "Paternity leave"),
                        ],
                    )

                conn.commit()
                logger.info("Leave balance tables initialized")
            except Exception as e:
                conn.rollback()
                logger.exception("Failed to initialize leave balance tables: %s", e)
                raise


def get_employee_leave_balances(employee_id: int, year: Optional[int] = None) -> List[Dict]:
    """
    Get leave balances for an employee.
    
    Args:
        employee_id: Employee ID
        year: Year (defaults to current year)
    
    Returns:
        List of leave balance records
    """
    if year is None:
        year = date.today().year
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT 
                    lb.id,
                    lt.name as leave_type,
                    lb.year,
                    lb.total_allocated,
                    lb.used,
                    lb.pending,
                    lb.balance,
                    lt.max_days_per_year,
                    lt.is_paid
                FROM leave_balances lb
                JOIN leave_types lt ON lb.leave_type_id = lt.id
                WHERE lb.employee_id = %s AND lb.year = %s
                ORDER BY lt.name
            """, (employee_id, year))
            return cur.fetchall()


def initialize_employee_leave_balance(employee_id: int, year: int):
    """
    Initialize leave balances for an employee for a given year.
    Creates entries for all leave types with default allocations.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Get all leave types
            cur.execute("SELECT id, max_days_per_year FROM leave_types")
            leave_types = cur.fetchall()
            
            for leave_type_id, max_days in leave_types:
                # Check if balance already exists
                cur.execute("""
                    SELECT id FROM leave_balances 
                    WHERE employee_id = %s AND leave_type_id = %s AND year = %s
                """, (employee_id, leave_type_id, year))
                
                if not cur.fetchone():
                    # Create initial balance
                    cur.execute("""
                        INSERT INTO leave_balances 
                        (employee_id, leave_type_id, year, total_allocated, used, pending, balance)
                        VALUES (%s, %s, %s, %s, 0, 0, %s)
                    """, (employee_id, leave_type_id, year, max_days, max_days))
            
            conn.commit()

