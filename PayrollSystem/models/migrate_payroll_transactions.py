"""
Migration script to add payroll transaction history table and seed existing data.
Run this script to add transaction tracking to an existing database.
"""

import logging
from datetime import datetime
from models.database import get_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_payroll_transaction_history():
    """
    Add payroll_transaction_history table if it doesn't exist
    and seed it with historical data from existing payroll_entries.
    """
    logger.info("Starting payroll transaction history migration...")
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Create the table if it doesn't exist
            logger.info("Creating payroll_transaction_history table...")
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
            logger.info("Table created successfully.")
            
            # Check if we need to seed historical data
            cur.execute("SELECT COUNT(*) as count FROM payroll_transaction_history")
            existing_count = cur.fetchone()['count']
            
            if existing_count > 0:
                logger.info(f"Transaction history already has {existing_count} records. Skipping seed.")
                conn.commit()
                return
            
            # Seed historical data from existing payroll_entries
            logger.info("Seeding historical data from existing payroll entries...")
            cur.execute("""
                SELECT 
                    id, payroll_period_id, employee_id, 
                    gross_pay, net_pay, status
                FROM payroll_entries
                ORDER BY id
            """)
            entries = cur.fetchall()
            
            seeded_count = 0
            for entry in entries:
                try:
                    # Determine transaction type based on status
                    if entry['status'] == 'VERIFIED':
                        transaction_type = 'VERIFIED'
                    elif entry['status'] == 'PENDING':
                        transaction_type = 'SUBMITTED'
                    elif entry['status'] == 'REJECTED':
                        transaction_type = 'REJECTED'
                    else:
                        transaction_type = 'CREATED'
                    
                    cur.execute("""
                        INSERT INTO payroll_transaction_history (
                            payroll_entry_id, payroll_period_id, employee_id,
                            transaction_type, new_status, 
                            new_gross_pay, new_net_pay,
                            notes
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        entry['id'],
                        entry['payroll_period_id'],
                        entry['employee_id'],
                        transaction_type,
                        entry['status'],
                        entry['gross_pay'],
                        entry['net_pay'],
                        "Historical data migration"
                    ))
                    seeded_count += 1
                except Exception as e:
                    logger.error(f"Error seeding entry {entry['id']}: {e}")
            
            conn.commit()
            logger.info(f"Successfully seeded {seeded_count} historical transaction records.")
    
    logger.info("Migration completed successfully!")


if __name__ == "__main__":
    migrate_payroll_transaction_history()

