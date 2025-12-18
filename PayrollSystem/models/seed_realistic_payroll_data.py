"""
Comprehensive seed script for realistic payroll data.
Creates 100+ employees with attendance, payroll periods, and computed payroll.
"""

import logging
import random
from datetime import date, datetime, timedelta
from models.database import get_connection, init_database
from models.payroll_computation_model import compute_payroll_period
from utils.security import hash_password

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Realistic employee data
FIRST_NAMES = [
    "Juan", "Maria", "Jose", "Ana", "Pedro", "Rosa", "Carlos", "Elena", "Luis", "Sofia",
    "Miguel", "Isabel", "Antonio", "Carmen", "Manuel", "Teresa", "Francisco", "Laura",
    "Rafael", "Patricia", "Angel", "Linda", "Roberto", "Sandra", "Fernando", "Monica",
    "Enrique", "Diana", "Jorge", "Gloria", "Ricardo", "Veronica", "Alejandro", "Martha",
    "Eduardo", "Raquel", "Sergio", "Lucia", "Alberto", "Beatriz", "Victor", "Cristina",
    "Gabriel", "Silvia", "Raul", "Adriana", "Oscar", "Gabriela", "Javier", "Daniela"
]

LAST_NAMES = [
    "Dela Cruz", "Santos", "Reyes", "Garcia", "Lopez", "Fernandez", "Torres", "Villanueva",
    "Martinez", "Gonzales", "Rodriguez", "Hernandez", "Mendoza", "Rivera", "Cruz", "Ramos",
    "Flores", "Castro", "Diaz", "Valdez", "Morales", "Aquino", "Pascual", "Mercado",
    "Santiago", "Bautista", "Castillo", "Navarro", "Guzman", "Perez", "Jimenez", "Salazar",
    "Aguilar", "Romero", "Mendez", "Campos", "Ortiz", "Silva", "Gutierrez", "Marquez",
    "Alvarez", "Domingo", "Vasquez", "Luna", "Solis", "Medina", "Cortez", "Rojas"
]

POSITIONS = {
    "Medical": ["Physician", "Nurse", "Medical Technologist", "Radiologist", "Pharmacist"],
    "Administrative": ["Administrative Assistant", "Receptionist", "Records Officer", "Office Manager"],
    "Support": ["Janitor", "Security Guard", "Maintenance Staff", "Driver"],
    "Finance": ["Accountant", "Billing Specialist", "Finance Officer", "Cashier"],
    "IT": ["IT Support Specialist", "System Administrator", "Database Administrator"]
}

DEPARTMENTS = ["Medical", "Administrative", "Support", "Finance", "IT"]

# Salary ranges by position type (monthly)
SALARY_RANGES = {
    "Physician": (60000, 120000),
    "Nurse": (25000, 45000),
    "Medical Technologist": (20000, 35000),
    "Radiologist": (50000, 90000),
    "Pharmacist": (30000, 50000),
    "Administrative Assistant": (18000, 28000),
    "Receptionist": (15000, 22000),
    "Records Officer": (18000, 25000),
    "Office Manager": (35000, 55000),
    "Janitor": (13000, 18000),
    "Security Guard": (15000, 20000),
    "Maintenance Staff": (16000, 23000),
    "Driver": (16000, 24000),
    "Accountant": (30000, 50000),
    "Billing Specialist": (22000, 35000),
    "Finance Officer": (35000, 60000),
    "Cashier": (16000, 24000),
    "IT Support Specialist": (25000, 40000),
    "System Administrator": (35000, 60000),
    "Database Administrator": (40000, 70000)
}


def clear_existing_data():
    """Clear existing seed data."""
    logger.info("Clearing existing seed data...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")
            cur.execute("DELETE FROM payroll_transaction_history WHERE id > 0")
            cur.execute("DELETE FROM attendance WHERE id > 0")
            cur.execute("DELETE FROM payroll_entries WHERE id > 0")
            cur.execute("DELETE FROM payroll_periods WHERE id > 0")
            cur.execute("DELETE FROM employees WHERE id > 0")
            cur.execute("DELETE FROM users WHERE id > 1")  # Keep admin
            cur.execute("DELETE FROM departments WHERE id > 0")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.commit()
    logger.info("Existing data cleared.")


def seed_departments():
    """Seed departments."""
    logger.info("Seeding departments...")
    with get_connection() as conn:
        with conn.cursor() as cur:
            for dept in DEPARTMENTS:
                cur.execute("INSERT INTO departments (name) VALUES (%s)", (dept,))
            conn.commit()
    logger.info(f"Seeded {len(DEPARTMENTS)} departments.")


def generate_government_id(prefix, index):
    """Generate realistic government ID numbers."""
    return f"{prefix}-{index:04d}-{random.randint(1000, 9999):04d}-{random.randint(0, 9)}"


def seed_employees(count=100):
    """Seed employees with realistic data."""
    logger.info(f"Seeding {count} employees...")
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Get department IDs
            cur.execute("SELECT id, name FROM departments")
            depts = {d['name']: d['id'] for d in cur.fetchall()}
            
            employees_added = 0
            for i in range(1, count + 1):
                # Random name
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                
                # Random department and position
                dept_name = random.choice(DEPARTMENTS)
                dept_id = depts[dept_name]
                position = random.choice(POSITIONS[dept_name])
                
                # Salary based on position
                min_sal, max_sal = SALARY_RANGES[position]
                base_salary = random.randint(min_sal, max_sal)
                
                # Random hire date (last 5 years)
                days_ago = random.randint(30, 1825)  # 1 month to 5 years
                date_hired = date.today() - timedelta(days=days_ago)
                
                # Government IDs
                sss_no = generate_government_id("SSS", i)
                philhealth_no = generate_government_id("PH", i)
                pagibig_no = generate_government_id("HDMF", i)
                tin_no = generate_government_id("TIN", i)
                
                employee_code = f"EMP-{i:04d}"
                
                try:
                    cur.execute("""
                        INSERT INTO employees (
                            employee_code, first_name, last_name, position, department_id,
                            date_hired, sss_no, philhealth_no, pagibig_no, tin_no,
                            base_salary, salary_type, is_active
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'MONTHLY', 1)
                    """, (
                        employee_code, first_name, last_name, position, dept_id,
                        date_hired, sss_no, philhealth_no, pagibig_no, tin_no, base_salary
                    ))
                    employees_added += 1
                    
                    # Create user account for each employee
                    employee_id = cur.lastrowid
                    username = employee_code.lower()
                    password_hash = hash_password("password123")
                    
                    cur.execute("SELECT id FROM roles WHERE name = 'Employee'")
                    role_id = cur.fetchone()['id']
                    
                    cur.execute("""
                        INSERT INTO users (username, password_hash, role_id, is_active, created_at)
                        VALUES (%s, %s, %s, 1, NOW())
                    """, (username, password_hash, role_id))
                    
                except Exception as e:
                    logger.error(f"Error inserting employee {employee_code}: {e}")
                    continue
            
            conn.commit()
    
    logger.info(f"Successfully seeded {employees_added} employees.")
    return employees_added


def seed_payroll_periods():
    """Seed payroll periods for the last 6 months."""
    logger.info("Seeding payroll periods...")
    
    periods = []
    today = date.today()
    
    # Generate periods for last 6 months (semi-monthly)
    for month_offset in range(6, 0, -1):
        # Calculate target month
        target_date = today - timedelta(days=month_offset * 30)
        year = target_date.year
        month = target_date.month
        
        # First half (1-15)
        period_1_start = date(year, month, 1)
        period_1_end = date(year, month, 15)
        period_1_name = f"{period_1_start.strftime('%B')} 1-15, {year}"
        status_1 = "APPROVED" if month_offset > 1 else "PROCESSED"
        periods.append((period_1_name, period_1_start, period_1_end, status_1))
        
        # Second half (16-end)
        period_2_start = date(year, month, 16)
        # Calculate last day of month
        if month == 12:
            period_2_end = date(year, 12, 31)
        else:
            period_2_end = date(year, month + 1, 1) - timedelta(days=1)
        period_2_name = f"{period_2_start.strftime('%B')} 16-{period_2_end.day}, {year}"
        status_2 = "APPROVED" if month_offset > 1 else "PROCESSED"
        periods.append((period_2_name, period_2_start, period_2_end, status_2))
    
    # Add current period as OPEN
    current_start = date(today.year, today.month, 1)
    if today.day <= 15:
        current_end = date(today.year, today.month, 15)
    else:
        current_end = date(today.year, today.month, 16)
        if today.month == 12:
            current_end = date(today.year, 12, 31)
        else:
            current_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    current_name = f"{current_start.strftime('%B')} {current_start.day}-{current_end.day}, {current_start.year}"
    periods.append((current_name, current_start, current_end, "OPEN"))
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany("""
                INSERT INTO payroll_periods (name, start_date, end_date, status)
                VALUES (%s, %s, %s, %s)
            """, periods)
            conn.commit()
    
    logger.info(f"Seeded {len(periods)} payroll periods.")
    return len(periods)


def seed_attendance_for_period(period_id, start_date, end_date):
    """Generate realistic attendance records for all employees in a period."""
    logger.info(f"Generating attendance for period {period_id} ({start_date} to {end_date})...")
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            # Get all employees
            cur.execute("SELECT id FROM employees WHERE is_active = 1")
            employees = cur.fetchall()
            
            attendance_records = []
            current_date = start_date
            
            while current_date <= end_date:
                # Skip weekends (5=Saturday, 6=Sunday)
                if current_date.weekday() < 5:
                    for emp in employees:
                        # 95% attendance rate (5% absent)
                        if random.random() < 0.95:
                            # Random time in (7:30 AM to 9:00 AM)
                            time_in_hour = random.randint(7, 8)
                            time_in_minute = random.randint(0, 59)
                            time_in = datetime.combine(current_date, datetime.min.time().replace(
                                hour=time_in_hour, minute=time_in_minute
                            ))
                            
                            # Regular hours: 8 hours (mostly on time, some overtime)
                            regular_hours = 8.0
                            overtime_hours = random.choices([0, 1, 2, 3], weights=[0.7, 0.15, 0.1, 0.05])[0]
                            
                            # Time out (5:00 PM + overtime)
                            time_out = time_in + timedelta(hours=8 + overtime_hours, minutes=random.randint(0, 30))
                            
                            total_hours = regular_hours + overtime_hours
                            
                            # Late if time_in after 8:00 AM
                            late_minutes = max(0, (time_in_hour - 8) * 60 + time_in_minute) if time_in_hour >= 8 else 0
                            
                            # Undertime (10% chance)
                            undertime_minutes = random.randint(15, 60) if random.random() < 0.1 else 0
                            
                            # Night differential (10 PM to 6 AM = 10% extra)
                            night_diff_hours = min(2, overtime_hours) if overtime_hours > 0 else 0
                            
                            status = "LATE" if late_minutes > 0 else "PRESENT"
                            
                            attendance_records.append((
                                emp['id'], current_date, time_in, time_out,
                                total_hours, regular_hours, overtime_hours, night_diff_hours,
                                status, late_minutes, undertime_minutes, 0, 0
                            ))
                
                current_date += timedelta(days=1)
            
            # Bulk insert attendance
            if attendance_records:
                cur.executemany("""
                    INSERT INTO attendance (
                        employee_id, attendance_date, time_in, time_out,
                        hours_worked, regular_hours, overtime_hours, night_differential_hours,
                        status, late_minutes, undertime_minutes, is_holiday, is_rest_day
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, attendance_records)
                conn.commit()
    
    logger.info(f"Generated {len(attendance_records)} attendance records.")
    return len(attendance_records)


def compute_payroll_for_periods():
    """Compute payroll for all periods."""
    logger.info("Computing payroll for all periods...")
    
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, name, start_date, end_date FROM payroll_periods ORDER BY start_date")
            periods = cur.fetchall()
    
    total_computed = 0
    for period in periods:
        logger.info(f"Computing payroll for period: {period['name']}")
        try:
            results = compute_payroll_period(period['id'])
            total_computed += results['computed']
            logger.info(f"  Computed: {results['computed']}/{results['total_employees']}, Errors: {len(results['errors'])}")
        except Exception as e:
            logger.error(f"Error computing payroll for period {period['id']}: {e}")
    
    logger.info(f"Total payroll entries computed: {total_computed}")
    return total_computed


def main():
    """Main seeding function."""
    logger.info("=" * 80)
    logger.info("REALISTIC PAYROLL DATA SEEDING - 100+ Employees")
    logger.info("=" * 80)
    
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    
    # Clear existing data
    clear_existing_data()
    
    # Seed departments
    seed_departments()
    
    # Seed 100+ employees
    employee_count = seed_employees(count=100)
    
    # Seed payroll periods (last 6 months + current)
    period_count = seed_payroll_periods()
    
    # Generate attendance for each period
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, start_date, end_date FROM payroll_periods ORDER BY start_date")
            periods = cur.fetchall()
    
    total_attendance = 0
    for period in periods:
        attendance_count = seed_attendance_for_period(
            period['id'], 
            period['start_date'], 
            period['end_date']
        )
        total_attendance += attendance_count
    
    # Compute payroll for all periods
    payroll_entries = compute_payroll_for_periods()
    
    # Summary
    logger.info("=" * 80)
    logger.info("SEEDING COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)
    logger.info(f"Departments: {len(DEPARTMENTS)}")
    logger.info(f"Employees: {employee_count}")
    logger.info(f"Payroll Periods: {period_count}")
    logger.info(f"Attendance Records: {total_attendance}")
    logger.info(f"Payroll Entries: {payroll_entries}")
    logger.info("=" * 80)
    
    # Display sample data
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT e.employee_code, e.first_name, e.last_name, e.position, 
                       d.name as department, e.base_salary
                FROM employees e
                JOIN departments d ON e.department_id = d.id
                LIMIT 10
            """)
            sample_employees = cur.fetchall()
            
            logger.info("\nSample Employees (first 10):")
            for emp in sample_employees:
                logger.info(f"  {emp['employee_code']}: {emp['first_name']} {emp['last_name']} - "
                          f"{emp['position']} ({emp['department']}) - PHP {emp['base_salary']:,.2f}")


if __name__ == "__main__":
    main()

