"""
Seed data script to populate the PROLY Payroll Management System database
with realistic sample data for testing and demonstration.

This script deletes all existing data before reseeding to ensure a clean state.
"""

from __future__ import annotations

from datetime import date, timedelta

from .database import get_connection
import logging


logger = logging.getLogger(__name__)
from utils.security import hash_password


def clear_database():
    """Delete all data from tables in the correct order (respecting foreign keys)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                logger.info("Clearing existing data...")

                # Disable foreign key checks temporarily
                cur.execute("SET FOREIGN_KEY_CHECKS = 0")

                # Delete data from all tables (in correct order to avoid FK conflicts)
                tables_to_clear = [
                    "audit_logs",
                    "payroll_entries",
                    "payroll_periods",
                    "employees",
                    "users",
                    "departments",
                ]

                for table in tables_to_clear:
                    cur.execute(f"DELETE FROM {table}")
                    cur.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")  # Reset auto-increment
                    logger.info("Cleared table %s", table)

                # Re-enable foreign key checks
                cur.execute("SET FOREIGN_KEY_CHECKS = 1")

                conn.commit()
                logger.info("All data cleared successfully")

            except Exception as e:
                conn.rollback()
                logger.exception("Error clearing database: %s", e)
                raise


def seed_database():
    """
    Clear and repopulate the database with seed data:
    - Departments
    - Users (all roles)
    - Employees
    - Payroll periods
    - Payroll entries
    - Audit logs
    """
    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)

        try:
            # First, clear all existing data
            cur.close()  # Close dictionary cursor before clearing
            clear_database()

            # Reopen cursor for seeding
            cur = conn.cursor(dictionary=True)

            logger.info("Starting database seeding...")
            
            # 1. Departments
            departments = ["IT", "HR", "Sales", "Finance", "Operations"]
            cur.executemany("INSERT INTO departments (name) VALUES (%s)", [(d,) for d in departments])
            logger.info("Seeded departments")

            # 2. Users (get role IDs first)
            cur.execute("SELECT id, name FROM roles")
            roles = {row["name"]: row["id"] for row in cur.fetchall()}

            users_data = [
                ("admin", hash_password("admin123"), roles["Administrator"], 1),
                ("hr_officer", hash_password("hr123"), roles["HR Officer"], 1),
                ("accountant", hash_password("acc123"), roles["Accountant"], 1),
                ("EMP-001", hash_password("emp123"), roles["Employee"], 1),  # Juan Dela Cruz - Software Engineer
                ("hr_jane", hash_password("hr123"), roles["HR Officer"], 1),
                ("acc_mark", hash_password("acc123"), roles["Accountant"], 0),  # Inactive
                ("EMP-003", hash_password("emp123"), roles["Employee"], 1),  # John Reyes - Sales Representative
                ("EMP-005", hash_password("emp123"), roles["Employee"], 1),  # Carlos Lopez - Senior Developer
            ]
            cur.executemany(
                "INSERT INTO users (username, password_hash, role_id, is_active) VALUES (%s, %s, %s, %s)",
                users_data,
            )
            logger.info("Seeded users")

            # 3. Employees
            cur.execute("SELECT id FROM departments WHERE name IN ('IT', 'HR', 'Sales', 'Finance')")
            dept_ids = [row["id"] for row in cur.fetchall()]
            it_dept = dept_ids[0] if len(dept_ids) > 0 else None
            hr_dept = dept_ids[1] if len(dept_ids) > 1 else None
            sales_dept = dept_ids[2] if len(dept_ids) > 2 else None
            finance_dept = dept_ids[3] if len(dept_ids) > 3 else None

            employees_data = [
            ("EMP-001", "Juan", "Dela Cruz", "Software Engineer", it_dept, date(2023, 1, 15), "03-1234567-8", "12-345678901-2", "121234567890", "123-456-789-000", 25000.00),
            ("EMP-002", "Maria", "Santos", "HR Manager", hr_dept, date(2022, 6, 1), "03-2345678-9", "12-456789012-3", "122345678901", "234-567-890-000", 35000.00),
            ("EMP-003", "John", "Reyes", "Sales Representative", sales_dept, date(2023, 3, 20), "03-3456789-0", "12-567890123-4", "123456789012", "345-678-901-000", 20000.00),
            ("EMP-004", "Anna", "Garcia", "Accountant", finance_dept, date(2022, 9, 10), "03-4567890-1", "12-678901234-5", "124567890123", "456-789-012-000", 30000.00),
            ("EMP-005", "Carlos", "Lopez", "Senior Developer", it_dept, date(2021, 11, 5), "03-5678901-2", "12-789012345-6", "125678901234", "567-890-123-000", 40000.00),
            ("EMP-006", "Lisa", "Fernandez", "HR Assistant", hr_dept, date(2023, 7, 1), "03-6789012-3", "12-890123456-7", "126789012345", "678-901-234-000", 18000.00),
            ("EMP-007", "Michael", "Torres", "Sales Manager", sales_dept, date(2022, 2, 14), "03-7890123-4", "12-901234567-8", "127890123456", "789-012-345-000", 38000.00),
            ("EMP-008", "Sarah", "Villanueva", "Junior Developer", it_dept, date(2024, 1, 8), "03-8901234-5", "12-012345678-9", "128901234567", "890-123-456-000", 22000.00),
            ]
            cur.executemany(
            """INSERT INTO employees (
                employee_code, first_name, last_name, position, department_id,
                date_hired, sss_no, philhealth_no, pagibig_no, tin_no, base_salary
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            employees_data,
            )
            logger.info("Seeded employees")

            # 4. Payroll Periods
            today = date.today()
            # Create last month's period
            if today.month > 1:
                last_month_start = date(today.year, today.month - 1, 1)
            else:
                last_month_start = date(today.year - 1, 12, 1)
            last_month_end = date(today.year, today.month, 1) - timedelta(days=1)
            
            # Current period
            current_start = date(today.year, today.month, 1)
            if today.day <= 15:
                current_end = date(today.year, today.month, 15)
            else:
                # Calculate end of current month
                if today.month == 12:
                    next_month_start = date(today.year + 1, 1, 1)
                else:
                    next_month_start = date(today.year, today.month + 1, 1)
                current_end = next_month_start - timedelta(days=1)
            
            periods_data = [
                (f"November 1-15, 2024", date(2024, 11, 1), date(2024, 11, 15), "APPROVED"),
                (f"November 16-30, 2024", date(2024, 11, 16), date(2024, 11, 30), "APPROVED"),
                (f"{last_month_start.strftime('%B')} 1-15, {last_month_start.year}", last_month_start, last_month_end, "PROCESSED"),
                (f"{current_start.strftime('%B')} 1-15, {current_start.year}", current_start, current_end, "OPEN"),
            ]
            cur.executemany(
                "INSERT INTO payroll_periods (name, start_date, end_date, status) VALUES (%s, %s, %s, %s)",
                periods_data,
            )
            logger.info("Seeded payroll periods")

        # 5. Payroll Entries (for multiple periods with realistic data)
            cur.execute("SELECT id, status FROM payroll_periods ORDER BY start_date")
            periods = cur.fetchall()
        
            cur.execute("SELECT id, base_salary FROM employees WHERE is_active = 1")
            employees = cur.fetchall()
        
        # Check if new columns exist
            cur.execute("SHOW COLUMNS FROM payroll_entries LIKE 'holiday_pay'")
            has_new_fields = cur.fetchone() is not None
        
            import random
            random.seed(42)  # For consistent random data
        
            for period in periods:
                period_id = period["id"]
                period_status = period["status"]
                
                # Determine entry status based on period status
                if period_status == "APPROVED":
                    entry_status = "VERIFIED"
                elif period_status == "PROCESSED":
                    entry_status = "VERIFIED"
                elif period_status == "OPEN":
                    entry_status = "PENDING"
                else:
                    entry_status = "DRAFT"
                
                entries_data = []
                simplified_data = []
                
                for emp in employees:
                    base = float(emp["base_salary"])
                    
                    # Add realistic variations
                    overtime = base * random.uniform(0.05, 0.15)  # 5-15% overtime
                    allowances = random.choice([1500.0, 2000.0, 2500.0, 3000.0])  # Varied allowances
                    holiday_pay = random.choice([0.0, 0.0, 0.0, base * 0.1])  # Occasional holiday pay
                    vacation_sickleave = random.choice([0.0, 0.0, base * 0.05])  # Occasional leave pay
                    salary_adjustment = random.choice([0.0, 0.0, 0.0, 500.0, -200.0])  # Rare adjustments
                    incentive_pay = random.choice([0.0, 0.0, 0.0, 1000.0, 2000.0])  # Performance bonuses
                    
                    gross = base + overtime + allowances + holiday_pay + vacation_sickleave + salary_adjustment + incentive_pay
                
                # Realistic deductions based on Philippine payroll standards
                # SSS (Social Security System)
                if gross <= 3250:
                    sss = 135.0
                elif gross <= 24750:
                    sss = min(gross * 0.045, 1125.0)
                else:
                    sss = 1125.0
                
                # PhilHealth
                if gross <= 10000:
                    philhealth = 300.0
                elif gross <= 80000:
                    philhealth = gross * 0.03
                else:
                    philhealth = 2400.0
                
                # Pag-IBIG
                if gross <= 1500:
                    pagibig = gross * 0.01
                else:
                    pagibig = min(gross * 0.02, 100.0)
                
                # Withholding Tax (simplified progressive tax)
                taxable = gross - (sss + philhealth + pagibig)
                if taxable <= 20833:
                    tax = 0.0
                elif taxable <= 33332:
                    tax = (taxable - 20833) * 0.20
                elif taxable <= 66666:
                    tax = 2500 + (taxable - 33332) * 0.25
                elif taxable <= 166666:
                    tax = 10833 + (taxable - 66666) * 0.30
                else:
                    tax = 40833 + (taxable - 166666) * 0.32
                
                # Other deductions
                late_deduction = random.choice([0.0, 0.0, 0.0, 0.0, random.uniform(100, 500)])
                cash_advance = random.choice([0.0, 0.0, 0.0, 500.0, 1000.0])
                undertime_deduction = random.choice([0.0, 0.0, 0.0, random.uniform(50, 300)])
                other_deductions = random.choice([0.0, 0.0, 0.0, 0.0, 200.0])
                
                total_deductions = sss + philhealth + pagibig + tax + late_deduction + cash_advance + undertime_deduction + other_deductions
                net_pay = gross - total_deductions
                
                if has_new_fields:
                    entries_data.append((
                        period_id, emp["id"], base, overtime, allowances, holiday_pay, vacation_sickleave,
                        salary_adjustment, incentive_pay, gross, sss, philhealth, pagibig, tax,
                        late_deduction, cash_advance, undertime_deduction, other_deductions,
                        total_deductions, net_pay, entry_status
                    ))
                else:
                    simplified_data.append((
                        period_id, emp["id"], base, overtime, allowances, gross,
                        sss, philhealth, pagibig, tax, total_deductions, net_pay, entry_status
                        ))
                
                # Insert entries for this period
                if has_new_fields and entries_data:
                    cur.executemany(
                        """INSERT INTO payroll_entries (
                            payroll_period_id, employee_id, basic_pay, overtime_pay, allowances,
                            holiday_pay, vacation_sickleave, salary_adjustment, incentive_pay,
                            gross_pay, sss_contrib, philhealth_contrib, pagibig_contrib,
                            withholding_tax, late_deduction, cash_advance, undertime_deduction,
                            other_deductions, total_deductions, net_pay, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        entries_data,
                    )
                elif simplified_data:
                    cur.executemany(
                        """INSERT INTO payroll_entries (
                            payroll_period_id, employee_id, basic_pay, overtime_pay, allowances,
                            gross_pay, sss_contrib, philhealth_contrib, pagibig_contrib,
                            withholding_tax, total_deductions, net_pay, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        simplified_data,
                    )
            
            logger.info(
                "Seeded payroll entries for %s periods with %s employees each",
                len(periods),
                len(employees),
            )

            # 6. Comprehensive Audit Logs
            cur.execute("SELECT id, username FROM users")
            users = {row["username"]: row["id"] for row in cur.fetchall()}
            
            if users:
                # Create comprehensive audit logs showing various activities
                logs_data = [
                # Admin activities
                (users.get("admin"), "Login", "Administrator logged in successfully"),
                (users.get("admin"), "Create", "Created new user account: hr_jane"),
                (users.get("admin"), "Edit", "Updated system settings: Pay period schedule changed to SEMI-MONTHLY"),
                (users.get("admin"), "Upload Compliance", "Uploaded BIR Tax compliance file"),
                (users.get("admin"), "Edit", "Modified user role for accountant"),
                (users.get("admin"), "Create", "Added new department: Marketing"),
                (users.get("admin"), "Delete", "Deactivated user account: acc_mark"),
                (users.get("admin"), "Save Settings", "Updated system settings: Date format changed to DD/MM/YY"),
                (users.get("admin"), "Logout", "Administrator logged out"),
                
                # HR Officer activities
                (users.get("hr_officer"), "Login", "HR Officer logged in successfully"),
                (users.get("hr_officer"), "Create", "Registered new employee: EMP-008 - Sarah Villanueva"),
                (users.get("hr_officer"), "Edit", "Updated employee record: EMP-001 - Changed department"),
                (users.get("hr_officer"), "Edit", "Updated employee salary: EMP-005 - Increased to PHP 42,000"),
                (users.get("hr_officer"), "Create", "Generated employee report: Active employees by department"),
                (users.get("hr_officer"), "Edit", "Updated employee information: EMP-003 - Contact details"),
                (users.get("hr_officer"), "Create", "Added employee: EMP-006 - Lisa Fernandez"),
                (users.get("hr_officer"), "Logout", "HR Officer logged out"),
                
                # Accountant activities
                (users.get("accountant"), "Login", "Accountant logged in successfully"),
                (users.get("accountant"), "Run Payroll", "Computed payroll for period: November 1-15, 2024"),
                (users.get("accountant"), "Submit Payroll", "Submitted payroll period November 1-15, 2024 for verification"),
                (users.get("accountant"), "Run Payroll", "Computed payroll for period: November 16-30, 2024"),
                (users.get("accountant"), "Submit Payroll", "Submitted payroll period November 16-30, 2024 for verification"),
                (users.get("accountant"), "Edit", "Modified payroll entry for EMP-002: Adjusted overtime"),
                (users.get("accountant"), "Edit", "Updated deductions for EMP-004"),
                (users.get("accountant"), "Logout", "Accountant logged out"),
                
                # Employee activities (Juan Dela Cruz - EMP-001)
                (users.get("EMP-001"), "Login", "Employee logged in successfully"),
                (users.get("EMP-001"), "View", "Employee viewed payslip for November 2024"),
                (users.get("EMP-001"), "View", "Employee checked dashboard"),
                (users.get("EMP-001"), "Logout", "Employee logged out"),
                
                # More employee activities (John Reyes - EMP-003)
                (users.get("EMP-003"), "Login", "Employee logged in successfully"),
                (users.get("EMP-003"), "View", "Employee viewed payslip"),
                (users.get("EMP-003"), "Logout", "Employee logged out"),
                
                # Senior Developer activities (Carlos Lopez - EMP-005)
                (users.get("EMP-005"), "Login", "Employee logged in successfully"),
                (users.get("EMP-005"), "View", "Employee viewed dashboard"),
                (users.get("EMP-005"), "View", "Employee reviewed payslip details"),
                (users.get("EMP-005"), "Logout", "Employee logged out"),
                
                # Additional HR activities
                (users.get("hr_jane"), "Login", "HR Officer logged in successfully"),
                (users.get("hr_jane"), "Create", "Generated departmental report"),
                (users.get("hr_jane"), "Edit", "Updated employee position: EMP-007 promoted to Senior Sales Manager"),
                (users.get("hr_jane"), "Logout", "HR Officer logged out"),
                
                # More admin activities
                (users.get("admin"), "Login", "Administrator logged in successfully"),
                (users.get("admin"), "Upload Compliance", "Uploaded SSS Contributions compliance file"),
                (users.get("admin"), "Upload Compliance", "Uploaded PhilHealth Rates compliance file"),
                (users.get("admin"), "Upload Compliance", "Uploaded Pag-IBIG Rates compliance file"),
                (users.get("admin"), "Edit", "System maintenance: Updated tax rates"),
                
                # Recent payroll activities
                (users.get("accountant"), "Login", "Accountant logged in successfully"),
                (users.get("accountant"), "Run Payroll", f"Computed payroll for period: {current_start.strftime('%B')} 1-15, {current_start.year}"),
                (users.get("accountant"), "Edit", "Reviewed payroll calculations for accuracy"),
                
                # User management activities
                (users.get("admin"), "Update User", "Updated user: accountant - Changed role permissions"),
                (users.get("admin"), "Create User", "Created new user: manager_operations"),
                
                # Final logins
                (users.get("hr_officer"), "Login", "HR Officer logged in successfully"),
                (users.get("accountant"), "Login", "Accountant logged in successfully"),
                (users.get("admin"), "Login", "Administrator logged in successfully"),
            ]
            
                # Filter out None user_ids (in case some users don't exist)
                logs_data = [(uid, action, details) for uid, action, details in logs_data if uid is not None]
                
                cur.executemany(
                    "INSERT INTO audit_logs (user_id, action, details) VALUES (%s, %s, %s)",
                    logs_data,
                )
                logger.info("Seeded %s comprehensive audit log entries", len(logs_data))

            conn.commit()
            logger.info("Seed data populated successfully")

        except Exception as e:
            conn.rollback()
            logger.exception("Error seeding database: %s", e)
            raise
        finally:
            cur.close()


if __name__ == "__main__":
    seed_database()
