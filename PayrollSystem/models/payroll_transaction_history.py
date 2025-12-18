"""
Payroll Transaction History Model
Tracks all changes and transactions related to payroll entries for audit trail.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional

from .database import get_connection

logger = logging.getLogger(__name__)


def init_payroll_transaction_tables():
    """
    Create payroll_transaction_history table if it doesn't exist.
    This table tracks all changes to payroll entries.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS payroll_transaction_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    payroll_entry_id INT NOT NULL,
                    payroll_period_id INT NOT NULL,
                    employee_id INT NOT NULL,
                    transaction_type ENUM('CREATED', 'UPDATED', 'SUBMITTED', 'VERIFIED', 'REJECTED', 'REVISION_REQUESTED') NOT NULL,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    previous_status VARCHAR(50),
                    new_status VARCHAR(50),
                    previous_gross_pay DECIMAL(12,2),
                    new_gross_pay DECIMAL(12,2),
                    previous_net_pay DECIMAL(12,2),
                    new_net_pay DECIMAL(12,2),
                    changed_by INT,
                    notes TEXT,
                    FOREIGN KEY (payroll_entry_id) REFERENCES payroll_entries(id) ON DELETE CASCADE,
                    FOREIGN KEY (payroll_period_id) REFERENCES payroll_periods(id),
                    FOREIGN KEY (employee_id) REFERENCES employees(id),
                    FOREIGN KEY (changed_by) REFERENCES users(id),
                    INDEX idx_transaction_date (transaction_date),
                    INDEX idx_payroll_entry (payroll_entry_id),
                    INDEX idx_employee (employee_id),
                    INDEX idx_period (payroll_period_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()
            logger.info("Payroll transaction history table initialized.")


def log_payroll_transaction(
    payroll_entry_id: int,
    payroll_period_id: int,
    employee_id: int,
    transaction_type: str,
    previous_status: Optional[str] = None,
    new_status: Optional[str] = None,
    previous_gross_pay: Optional[float] = None,
    new_gross_pay: Optional[float] = None,
    previous_net_pay: Optional[float] = None,
    new_net_pay: Optional[float] = None,
    changed_by: Optional[int] = None,
    notes: Optional[str] = None
) -> int:
    """
    Log a payroll transaction to the history table.
    
    Args:
        payroll_entry_id: ID of the payroll entry
        payroll_period_id: ID of the payroll period
        employee_id: ID of the employee
        transaction_type: Type of transaction (CREATED, UPDATED, SUBMITTED, VERIFIED, REJECTED, REVISION_REQUESTED)
        previous_status: Previous status (for updates)
        new_status: New status
        previous_gross_pay: Previous gross pay (for updates)
        new_gross_pay: New gross pay
        previous_net_pay: Previous net pay (for updates)
        new_net_pay: New net pay
        changed_by: User ID who made the change
        notes: Additional notes
    
    Returns:
        ID of the created transaction history record
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO payroll_transaction_history (
                        payroll_entry_id, payroll_period_id, employee_id,
                        transaction_type, previous_status, new_status,
                        previous_gross_pay, new_gross_pay,
                        previous_net_pay, new_net_pay,
                        changed_by, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    payroll_entry_id, payroll_period_id, employee_id,
                    transaction_type, previous_status, new_status,
                    previous_gross_pay, new_gross_pay,
                    previous_net_pay, new_net_pay,
                    changed_by, notes
                ))
                conn.commit()
                transaction_id = cur.lastrowid
                logger.info(f"Logged payroll transaction: {transaction_type} for entry {payroll_entry_id}")
                return transaction_id
    except Exception as e:
        logger.exception(f"Failed to log payroll transaction: {e}")
        raise


def get_payroll_transaction_history(
    payroll_entry_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    payroll_period_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict]:
    """
    Get payroll transaction history with optional filters.
    
    Args:
        payroll_entry_id: Filter by payroll entry ID
        employee_id: Filter by employee ID
        payroll_period_id: Filter by payroll period ID
        transaction_type: Filter by transaction type
        start_date: Filter by start date
        end_date: Filter by end date
    
    Returns:
        List of transaction history records
    """
    query = """
        SELECT 
            pth.*,
            e.employee_code,
            CONCAT(e.first_name, ' ', e.last_name) as employee_name,
            pp.name as period_name,
            u.username as changed_by_username
        FROM payroll_transaction_history pth
        JOIN employees e ON pth.employee_id = e.id
        JOIN payroll_periods pp ON pth.payroll_period_id = pp.id
        LEFT JOIN users u ON pth.changed_by = u.id
        WHERE 1=1
    """
    params = []
    
    if payroll_entry_id:
        query += " AND pth.payroll_entry_id = %s"
        params.append(payroll_entry_id)
    
    if employee_id:
        query += " AND pth.employee_id = %s"
        params.append(employee_id)
    
    if payroll_period_id:
        query += " AND pth.payroll_period_id = %s"
        params.append(payroll_period_id)
    
    if transaction_type:
        query += " AND pth.transaction_type = %s"
        params.append(transaction_type)
    
    if start_date:
        query += " AND pth.transaction_date >= %s"
        params.append(start_date)
    
    if end_date:
        query += " AND pth.transaction_date <= %s"
        params.append(end_date)
    
    query += " ORDER BY pth.transaction_date DESC"
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def get_payroll_entry_history_summary(payroll_entry_id: int) -> Dict:
    """
    Get a summary of all transactions for a specific payroll entry.
    
    Args:
        payroll_entry_id: ID of the payroll entry
    
    Returns:
        Dictionary with transaction counts and latest status
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN transaction_type = 'CREATED' THEN 1 ELSE 0 END) as created_count,
                    SUM(CASE WHEN transaction_type = 'UPDATED' THEN 1 ELSE 0 END) as updated_count,
                    SUM(CASE WHEN transaction_type = 'SUBMITTED' THEN 1 ELSE 0 END) as submitted_count,
                    SUM(CASE WHEN transaction_type = 'VERIFIED' THEN 1 ELSE 0 END) as verified_count,
                    SUM(CASE WHEN transaction_type = 'REJECTED' THEN 1 ELSE 0 END) as rejected_count,
                    MAX(transaction_date) as latest_transaction_date,
                    (SELECT new_status FROM payroll_transaction_history 
                     WHERE payroll_entry_id = %s 
                     ORDER BY transaction_date DESC LIMIT 1) as latest_status
                FROM payroll_transaction_history
                WHERE payroll_entry_id = %s
            """, (payroll_entry_id, payroll_entry_id))
            return cur.fetchone() or {}


if __name__ == "__main__":
    # Initialize the transaction history table
    init_payroll_transaction_tables()
    logger.info("Payroll transaction history table created successfully.")

