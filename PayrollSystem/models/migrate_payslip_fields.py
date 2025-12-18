"""
Migration script to add payslip-specific fields to payroll_entries table
and create company_settings table.
"""

from __future__ import annotations

from .database import get_connection
import logging


logger = logging.getLogger(__name__)


def migrate_payslip_fields():
    """Add new fields to payroll_entries table and create company_settings table."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                # Check if columns already exist and add them if they don't
                cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'holiday_pay'")
                if cur.fetchone() is None:
                    cur.execute("ALTER TABLE payroll_entries ADD COLUMN holiday_pay DECIMAL(12,2) DEFAULT 0 AFTER allowances")
                    logger.info("Added holiday_pay column")
                
                cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'vacation_sickleave'")
                if cur.fetchone() is None:
                    cur.execute("ALTER TABLE payroll_entries ADD COLUMN vacation_sickleave DECIMAL(12,2) DEFAULT 0 AFTER holiday_pay")
                    logger.info("Added vacation_sickleave column")
                
                cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'salary_adjustment'")
                if cur.fetchone() is None:
                    cur.execute("ALTER TABLE payroll_entries ADD COLUMN salary_adjustment DECIMAL(12,2) DEFAULT 0 AFTER vacation_sickleave")
                    logger.info("Added salary_adjustment column")
                
                cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'incentive_pay'")
                if cur.fetchone() is None:
                    cur.execute("ALTER TABLE payroll_entries ADD COLUMN incentive_pay DECIMAL(12,2) DEFAULT 0 AFTER salary_adjustment")
                    logger.info("Added incentive_pay column")
                
                cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'late_deduction'")
                if cur.fetchone() is None:
                    cur.execute("ALTER TABLE payroll_entries ADD COLUMN late_deduction DECIMAL(12,2) DEFAULT 0 AFTER withholding_tax")
                    logger.info("Added late_deduction column")
                
                cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'cash_advance'")
                if cur.fetchone() is None:
                    cur.execute("ALTER TABLE payroll_entries ADD COLUMN cash_advance DECIMAL(12,2) DEFAULT 0 AFTER late_deduction")
                    logger.info("Added cash_advance column")
                
                cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'undertime_deduction'")
                if cur.fetchone() is None:
                    cur.execute("ALTER TABLE payroll_entries ADD COLUMN undertime_deduction DECIMAL(12,2) DEFAULT 0 AFTER cash_advance")
                    logger.info("Added undertime_deduction column")
                
                cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'other_deductions'")
                if cur.fetchone() is None:
                    cur.execute("ALTER TABLE payroll_entries ADD COLUMN other_deductions DECIMAL(12,2) DEFAULT 0 AFTER undertime_deduction")
                    logger.info("Added other_deductions column")
                
                # Create company_settings table if it doesn't exist
                cur.execute("""
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
        """)
                logger.info("Ensured company_settings table exists")
                
                # Seed company settings if empty
                cur.execute("SELECT COUNT(*) FROM company_settings")
                if cur.fetchone()[0] == 0:
                    cur.execute(
                        """INSERT INTO company_settings (company_name, address_line1, phone, email) 
                           VALUES ('UNICARE MEDICAL CLINIC', 'Address Line 1, City Name', '(02) 123-4567', 'unicare@gmail.com')"""
                    )
                    logger.info("Seeded company settings")
                
                conn.commit()
                logger.info("Migration completed successfully")
            except Exception as e:
                conn.rollback()
                logger.exception("Migration failed: %s", e)
                raise


if __name__ == "__main__":
    migrate_payslip_fields()

