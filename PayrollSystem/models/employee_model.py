from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .database import get_connection


@dataclass
class Employee:
    id: int
    employee_code: str
    first_name: str
    last_name: str
    position: str
    department_id: Optional[int]
    date_hired: Optional[str]
    sss_no: Optional[str]
    philhealth_no: Optional[str]
    pagibig_no: Optional[str]
    tin_no: Optional[str]
    base_salary: float
    hourly_rate: float
    salary_type: str
    is_active: bool


def create_employee(data: dict) -> int:
    """
    Insert a new employee row and return its generated ID.
    Expects keys consistent with the EmployeeInformation wireframe.
    """
    query = """
        INSERT INTO employees (
            employee_code, first_name, last_name, position,
            department_id, date_hired, sss_no, philhealth_no,
            pagibig_no, tin_no, base_salary, hourly_rate, salary_type
        )
        VALUES (%(employee_code)s, %(first_name)s, %(last_name)s, %(position)s,
                %(department_id)s, %(date_hired)s, %(sss_no)s, %(philhealth_no)s,
                %(pagibig_no)s, %(tin_no)s, %(base_salary)s, %(hourly_rate)s, %(salary_type)s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, data)
            conn.commit()
            return cur.lastrowid


def get_all_employees(active_only: bool = True) -> List[Employee]:
    cond = "WHERE e.is_active = 1" if active_only else ""
    query = f"""
        SELECT e.id, e.employee_code, e.first_name, e.last_name, e.position,
               e.department_id, e.date_hired, e.sss_no, e.philhealth_no,
               e.pagibig_no, e.tin_no, e.base_salary, e.hourly_rate, e.salary_type, e.is_active,
               d.name as department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        {cond}
        ORDER BY e.last_name, e.first_name
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query)
            rows = cur.fetchall()

    employees = []
    for row in rows:
        emp = Employee(
            id=row["id"],
            employee_code=row["employee_code"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            position=row["position"],
            department_id=row["department_id"],
            date_hired=str(row["date_hired"]) if row["date_hired"] else None,
            sss_no=row["sss_no"],
            philhealth_no=row["philhealth_no"],
            pagibig_no=row["pagibig_no"],
            tin_no=row["tin_no"],
            base_salary=float(row["base_salary"]),
            hourly_rate=float(row.get("hourly_rate", 0)),
            salary_type=row.get("salary_type", "MONTHLY"),
            is_active=bool(row["is_active"]),
        )
        # Add department_name as attribute (not in dataclass)
        emp.department_name = row.get("department_name")
        employees.append(emp)
    
    return employees


def update_employee(employee_id: int, data: dict) -> bool:
    """
    Update an existing employee record.
    Returns True if successful, False otherwise.
    """
    query = """
        UPDATE employees
        SET first_name = %(first_name)s,
            last_name = %(last_name)s,
            position = %(position)s,
            department_id = %(department_id)s,
            date_hired = %(date_hired)s,
            sss_no = %(sss_no)s,
            philhealth_no = %(philhealth_no)s,
            pagibig_no = %(pagibig_no)s,
            tin_no = %(tin_no)s,
            base_salary = %(base_salary)s,
            hourly_rate = %(hourly_rate)s,
            salary_type = %(salary_type)s,
            is_active = %(is_active)s
        WHERE id = %(employee_id)s
    """
    data['employee_id'] = employee_id
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, data)
                conn.commit()
                return cur.rowcount > 0
    except Exception as e:
        print(f"Error updating employee: {e}")
        return False


def get_employee_by_code(employee_code: str) -> Optional[Employee]:
    """Get employee by employee code."""
    query = """
        SELECT e.id, e.employee_code, e.first_name, e.last_name, e.position,
               e.department_id, e.date_hired, e.sss_no, e.philhealth_no,
               e.pagibig_no, e.tin_no, e.base_salary, e.hourly_rate, e.salary_type, e.is_active,
               d.name as department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.employee_code = %s
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (employee_code,))
            row = cur.fetchone()
    
    if not row:
        return None
    
    emp = Employee(
        id=row["id"],
        employee_code=row["employee_code"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        position=row["position"],
        department_id=row["department_id"],
        date_hired=str(row["date_hired"]) if row["date_hired"] else None,
        sss_no=row["sss_no"],
        philhealth_no=row["philhealth_no"],
        pagibig_no=row["pagibig_no"],
        tin_no=row["tin_no"],
        base_salary=float(row["base_salary"]),
        hourly_rate=float(row.get("hourly_rate", 0)),
        salary_type=row.get("salary_type", "MONTHLY"),
        is_active=bool(row["is_active"]),
    )
    emp.department_name = row.get("department_name")
    return emp


def get_employee_by_id(employee_id: int) -> Optional[Employee]:
    """Get employee by ID."""
    query = """
        SELECT e.id, e.employee_code, e.first_name, e.last_name, e.position,
               e.department_id, e.date_hired, e.sss_no, e.philhealth_no,
               e.pagibig_no, e.tin_no, e.base_salary, e.hourly_rate, e.salary_type, e.is_active,
               d.name as department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.id = %s
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (employee_id,))
            row = cur.fetchone()
    
    if not row:
        return None
    
    emp = Employee(
        id=row["id"],
        employee_code=row["employee_code"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        position=row["position"],
        department_id=row["department_id"],
        date_hired=str(row["date_hired"]) if row["date_hired"] else None,
        sss_no=row["sss_no"],
        philhealth_no=row["philhealth_no"],
        pagibig_no=row["pagibig_no"],
        tin_no=row["tin_no"],
        base_salary=float(row["base_salary"]),
        hourly_rate=float(row.get("hourly_rate", 0)),
        salary_type=row.get("salary_type", "MONTHLY"),
        is_active=bool(row["is_active"]),
    )
    emp.department_name = row.get("department_name")
    return emp


def get_latest_payslip_for_employee(employee_id: int) -> Optional[dict]:
    """Get the latest payslip for an employee."""
    query = """
        SELECT pe.*, pp.name as period_name, pp.start_date, pp.end_date
        FROM payroll_entries pe
        JOIN payroll_periods pp ON pe.payroll_period_id = pp.id
        WHERE pe.employee_id = %s
        ORDER BY pp.start_date DESC
        LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (employee_id,))
            result = cur.fetchone()
            if result:
                # Ensure all fields have default values if columns don't exist
                defaults = {
                    'holiday_pay': 0.0,
                    'vacation_sickleave': 0.0,
                    'salary_adjustment': 0.0,
                    'incentive_pay': 0.0,
                    'late_deduction': 0.0,
                    'cash_advance': 0.0,
                    'undertime_deduction': 0.0,
                    'other_deductions': 0.0,
                }
                for key, default_value in defaults.items():
                    if key not in result:
                        result[key] = default_value
            return result
