"""
MySQL database connection utilities for the PROLY Payroll Management System.

Tech stack: MySQL (via XAMPP) + mysql-connector-python

Database name is derived from the system name in the 1st Deliverable:
    "PROLY Payroll Management System" -> `proly_payroll_db`
"""

from __future__ import annotations

import os
import logging

import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector import pooling


logger = logging.getLogger(__name__)


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "proly_payroll_db"),
}


_POOL_NAME = "proly_pool"
_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))

_connection_pool: pooling.MySQLConnectionPool | None = None


def _get_pool() -> pooling.MySQLConnectionPool:
    """Lazily initialize and return a global MySQL connection pool."""
    global _connection_pool
    if _connection_pool is None:
        logger.info(
            "Initializing MySQL connection pool '%s' (size=%s) for %s@%s/%s",
            _POOL_NAME,
            _POOL_SIZE,
            DB_CONFIG["user"],
            DB_CONFIG["host"],
            DB_CONFIG["database"],
        )
        _connection_pool = pooling.MySQLConnectionPool(
            pool_name=_POOL_NAME,
            pool_size=_POOL_SIZE,
            **DB_CONFIG,
        )
    return _connection_pool


def get_connection() -> MySQLConnection:
    """
    Get a pooled MySQL connection using the global DB_CONFIG.

    Usage:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute("SELECT 1")
    """

    return _get_pool().get_connection()


def init_database():
    """
    Ensure that the `proly_payroll_db` database and core tables exist.

    This is a minimal bootstrap aligned with the 1st Deliverable:
    - Users & roles (RBAC for Admin, HR Officer, Accountant, Employee)
    - Employees & government IDs
    - Payroll periods and payroll entries
    - Compliance configuration tables (tax & contributions)
    - Audit log

    Run this once after configuring MySQL credentials.
    """
    root_conf = DB_CONFIG.copy()
    db_name = root_conf.pop("database")

    # Connect without specifying database to create it if needed
    root_conn = mysql.connector.connect(**{k: root_conf[k] for k in ("host", "port", "user", "password")})
    root_cur = root_conn.cursor()

    root_cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    root_cur.close()
    root_conn.close()

    # Now connect to the actual DB and create tables
    conn = get_connection()
    cur = conn.cursor()

    # Users & roles
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role_id INT NOT NULL,
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    # Employees
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_code VARCHAR(30) NOT NULL UNIQUE,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            position VARCHAR(100),
            department_id INT,
            date_hired DATE,
            sss_no VARCHAR(50),
            philhealth_no VARCHAR(50),
            pagibig_no VARCHAR(50),
            tin_no VARCHAR(50),
            base_salary DECIMAL(12,2) DEFAULT 0,
            hourly_rate DECIMAL(12,2) DEFAULT 0,
            salary_type ENUM('MONTHLY', 'HOURLY', 'DAILY') DEFAULT 'MONTHLY',
            is_active TINYINT(1) NOT NULL DEFAULT 1,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    
    # Add hourly_rate and salary_type columns if they don't exist (migration)
    try:
        cur.execute("ALTER TABLE employees ADD COLUMN hourly_rate DECIMAL(12,2) DEFAULT 0")
    except:
        pass  # Column already exists
    
    try:
        cur.execute("ALTER TABLE employees ADD COLUMN salary_type ENUM('MONTHLY', 'HOURLY', 'DAILY') DEFAULT 'MONTHLY'")
    except:
        pass  # Column already exists

    # Payroll periods & entries
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll_periods (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status ENUM('OPEN','PROCESSED','SUBMITTED','APPROVED','REJECTED') DEFAULT 'OPEN'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payroll_entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            payroll_period_id INT NOT NULL,
            employee_id INT NOT NULL,
            basic_pay DECIMAL(12,2) DEFAULT 0,
            overtime_pay DECIMAL(12,2) DEFAULT 0,
            allowances DECIMAL(12,2) DEFAULT 0,
            holiday_pay DECIMAL(12,2) DEFAULT 0,
            vacation_sickleave DECIMAL(12,2) DEFAULT 0,
            salary_adjustment DECIMAL(12,2) DEFAULT 0,
            incentive_pay DECIMAL(12,2) DEFAULT 0,
            gross_pay DECIMAL(12,2) DEFAULT 0,
            sss_contrib DECIMAL(12,2) DEFAULT 0,
            philhealth_contrib DECIMAL(12,2) DEFAULT 0,
            pagibig_contrib DECIMAL(12,2) DEFAULT 0,
            withholding_tax DECIMAL(12,2) DEFAULT 0,
            late_deduction DECIMAL(12,2) DEFAULT 0,
            cash_advance DECIMAL(12,2) DEFAULT 0,
            undertime_deduction DECIMAL(12,2) DEFAULT 0,
            other_deductions DECIMAL(12,2) DEFAULT 0,
            total_deductions DECIMAL(12,2) DEFAULT 0,
            net_pay DECIMAL(12,2) DEFAULT 0,
            status ENUM('PENDING','VERIFIED','REJECTED') DEFAULT 'PENDING',
            FOREIGN KEY (payroll_period_id) REFERENCES payroll_periods(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    
    # Company settings table for payslip header information
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS company_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL DEFAULT 'UNICARE MEDICAL CLINIC',
            address_line1 VARCHAR(255) DEFAULT 'Address Line 1, City Name',
            address_line2 VARCHAR(255) DEFAULT '',
            phone VARCHAR(50) DEFAULT '(02) 123-4567',
            email VARCHAR(100) DEFAULT 'unicare@gmail.com',
            logo_path VARCHAR(255) DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    
    # System settings table for application configuration
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS system_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            setting_key VARCHAR(100) NOT NULL UNIQUE,
            setting_value VARCHAR(255) NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    # Compliance configuration (simplified, versioned tables)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tax_tables (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            effective_from DATE NOT NULL,
            version INT NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contribution_tables (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type ENUM('SSS','PHILHEALTH','PAGIBIG') NOT NULL,
            effective_from DATE NOT NULL,
            version INT NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )

    # Audit log
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action VARCHAR(100) NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    
    # Integration log (for Solution 2: Centralized Data Integration)
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

    # Seed core roles if table is empty
    cur.execute("SELECT COUNT(*) FROM roles;")
    (role_count,) = cur.fetchone()
    if role_count == 0:
        cur.executemany(
            "INSERT INTO roles (name) VALUES (%s)",
            [("Administrator",), ("HR Officer",), ("Accountant",), ("Employee",)],
        )
    
    # Seed company settings if table is empty
    cur.execute("SELECT COUNT(*) FROM company_settings;")
    (company_count,) = cur.fetchone()
    if company_count == 0:
        cur.execute(
            """INSERT INTO company_settings (company_name, address_line1, phone, email) 
               VALUES ('UNICARE MEDICAL CLINIC', 'Address Line 1, City Name', '(02) 123-4567', 'unicare@gmail.com')"""
        )
    
    # Seed system settings if table is empty
    cur.execute("SELECT COUNT(*) FROM system_settings;")
    (settings_count,) = cur.fetchone()
    if settings_count == 0:
        cur.executemany(
            "INSERT INTO system_settings (setting_key, setting_value) VALUES (%s, %s)",
            [
                ("pay_period_schedule", "SEMI - MONTHLY"),
                ("date_format", "DD / MM / YY"),
                ("regular_work_hours_per_day", "8"),
                ("regular_work_start_time", "08:00:00"),
                ("regular_work_end_time", "17:00:00"),
                ("overtime_rate_multiplier", "1.25"),
                ("night_differential_start", "22:00:00"),
                ("night_differential_end", "06:00:00"),
                ("night_differential_rate", "0.10"),
                ("holiday_rate_multiplier", "2.0"),
                ("rest_day_rate_multiplier", "1.3")
            ]
        )
    
    # Attendance table for attendance tracking and reports
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            attendance_date DATE NOT NULL,
            time_in TIME,
            time_out TIME,
            hours_worked DECIMAL(5,2) DEFAULT 0,
            regular_hours DECIMAL(5,2) DEFAULT 0,
            overtime_hours DECIMAL(5,2) DEFAULT 0,
            night_differential_hours DECIMAL(5,2) DEFAULT 0,
            is_holiday TINYINT(1) DEFAULT 0,
            is_rest_day TINYINT(1) DEFAULT 0,
            status ENUM('PRESENT', 'ABSENT', 'LATE', 'ON_LEAVE', 'HOLIDAY') DEFAULT 'PRESENT',
            late_minutes INT DEFAULT 0,
            undertime_minutes INT DEFAULT 0,
            notes TEXT,
            created_by INT,
            updated_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id),
            UNIQUE KEY unique_employee_date (employee_id, attendance_date),
            INDEX idx_attendance_date (attendance_date),
            INDEX idx_employee_date (employee_id, attendance_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    
    # Add new columns to attendance table if they don't exist (migration)
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN regular_hours DECIMAL(5,2) DEFAULT 0")
    except:
        pass
    
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN overtime_hours DECIMAL(5,2) DEFAULT 0")
    except:
        pass
    
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN night_differential_hours DECIMAL(5,2) DEFAULT 0")
    except:
        pass
    
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN is_holiday TINYINT(1) DEFAULT 0")
    except:
        pass
    
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN is_rest_day TINYINT(1) DEFAULT 0")
    except:
        pass
    
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN created_by INT, ADD FOREIGN KEY (created_by) REFERENCES users(id)")
    except:
        pass
    
    try:
        cur.execute("ALTER TABLE attendance ADD COLUMN updated_by INT, ADD FOREIGN KEY (updated_by) REFERENCES users(id)")
    except:
        pass
    
    # Performance reviews table (for performance reports)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS performance_reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            review_date DATE NOT NULL,
            review_period_start DATE,
            review_period_end DATE,
            rating DECIMAL(3,2),
            comments TEXT,
            reviewed_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id),
            INDEX idx_employee_review (employee_id, review_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    
    # Salary history table (for tracking salary changes)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS salary_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id INT NOT NULL,
            old_salary DECIMAL(12,2) NOT NULL,
            new_salary DECIMAL(12,2) NOT NULL,
            effective_date DATE NOT NULL,
            reason TEXT,
            changed_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id),
            FOREIGN KEY (changed_by) REFERENCES users(id),
            INDEX idx_employee_salary (employee_id, effective_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    )
    
    # Payroll transaction history table (for audit trail of payroll changes)
    cur.execute(
        """
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
        """
    )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    # Convenience entry point: `python -m models.database` to create DB & tables.
    init_database()
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    logging.getLogger(__name__).info("Database `proly_payroll_db` initialized.")


