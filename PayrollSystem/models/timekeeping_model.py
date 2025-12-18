"""
Timekeeping Model for PROLY Payroll System.
Handles time-in/time-out operations and attendance calculations.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from .database import get_connection
from .audit_model import log_audit


logger = logging.getLogger(__name__)


def get_company_work_settings() -> Dict[str, any]:
    """Get company work hour settings from system_settings."""
    settings = {}
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT setting_key, setting_value 
                FROM system_settings 
                WHERE setting_key IN (
                    'regular_work_hours_per_day',
                    'regular_work_start_time',
                    'regular_work_end_time',
                    'overtime_rate_multiplier',
                    'night_differential_start',
                    'night_differential_end',
                    'night_differential_rate',
                    'holiday_rate_multiplier',
                    'rest_day_rate_multiplier'
                )
            """)
            for row in cur.fetchall():
                key = row['setting_key']
                value = row['setting_value']
                # Convert numeric values
                if key in ['regular_work_hours_per_day', 'overtime_rate_multiplier', 
                          'night_differential_rate', 'holiday_rate_multiplier', 
                          'rest_day_rate_multiplier']:
                    settings[key] = float(value)
                else:
                    settings[key] = value
    return settings


def calculate_hours_worked(time_in: time, time_out: time) -> float:
    """Calculate total hours worked between time_in and time_out."""
    if not time_in or not time_out:
        return 0.0
    
    # Convert to datetime for calculation
    dt_in = datetime.combine(date.today(), time_in)
    dt_out = datetime.combine(date.today(), time_out)
    
    # Handle overnight shifts (time_out is next day)
    if dt_out < dt_in:
        dt_out += timedelta(days=1)
    
    delta = dt_out - dt_in
    hours = delta.total_seconds() / 3600.0
    return round(hours, 2)


def calculate_late_minutes(time_in: time, scheduled_start: time) -> int:
    """Calculate late minutes if time_in is after scheduled_start."""
    if not time_in or not scheduled_start:
        return 0
    
    dt_in = datetime.combine(date.today(), time_in)
    dt_scheduled = datetime.combine(date.today(), scheduled_start)
    
    if dt_in > dt_scheduled:
        delta = dt_in - dt_scheduled
        return int(delta.total_seconds() / 60)
    return 0


def calculate_undertime_minutes(time_out: time, scheduled_end: time) -> int:
    """Calculate undertime minutes if time_out is before scheduled_end."""
    if not time_out or not scheduled_end:
        return 0
    
    dt_out = datetime.combine(date.today(), time_out)
    dt_scheduled = datetime.combine(date.today(), scheduled_end)
    
    if dt_out < dt_scheduled:
        delta = dt_scheduled - dt_out
        return int(delta.total_seconds() / 60)
    return 0


def calculate_overtime_hours(time_out: time, scheduled_end: time, regular_hours: float) -> float:
    """Calculate overtime hours worked beyond scheduled end time."""
    if not time_out or not scheduled_end:
        return 0.0
    
    dt_out = datetime.combine(date.today(), time_out)
    dt_scheduled = datetime.combine(date.today(), scheduled_end)
    
    # Handle overnight shifts
    if dt_out < dt_scheduled:
        dt_out += timedelta(days=1)
    
    if dt_out > dt_scheduled:
        overtime_delta = dt_out - dt_scheduled
        overtime_hours = overtime_delta.total_seconds() / 3600.0
        # Overtime is hours beyond regular hours
        return max(0.0, round(overtime_hours, 2))
    return 0.0


def calculate_night_differential_hours(time_in: time, time_out: time, 
                                       night_start: time, night_end: time) -> float:
    """Calculate hours worked during night differential period."""
    if not time_in or not time_out:
        return 0.0
    
    settings = get_company_work_settings()
    night_start_time = datetime.strptime(settings.get('night_differential_start', '22:00:00'), '%H:%M:%S').time()
    night_end_time = datetime.strptime(settings.get('night_differential_end', '06:00:00'), '%H:%M:%S').time()
    
    # Convert to datetime for easier calculation
    dt_in = datetime.combine(date.today(), time_in)
    dt_out = datetime.combine(date.today(), time_out)
    
    # Handle overnight shifts
    if dt_out < dt_in:
        dt_out += timedelta(days=1)
    
    night_hours = 0.0
    current = dt_in
    
    while current < dt_out:
        current_time = current.time()
        next_hour = current + timedelta(hours=1)
        
        # Check if current hour is in night differential period
        if _is_night_differential_time(current_time, night_start_time, night_end_time):
            night_hours += 1.0
        
        current = next_hour
    
    return round(min(night_hours, (dt_out - dt_in).total_seconds() / 3600.0), 2)


def _is_night_differential_time(check_time: time, night_start: time, night_end: time) -> bool:
    """Check if a time falls within night differential period."""
    # Night differential typically spans midnight (e.g., 10 PM to 6 AM)
    if night_start > night_end:  # Spans midnight
        return check_time >= night_start or check_time < night_end
    else:  # Doesn't span midnight
        return night_start <= check_time < night_end


def time_in(employee_id: int, time_in_time: Optional[time] = None, 
            attendance_date: Optional[date] = None, user_id: Optional[int] = None) -> Tuple[bool, str]:
    """
    Record time-in for an employee.
    
    Args:
        employee_id: Employee ID
        time_in_time: Time-in time (defaults to current time)
        attendance_date: Date of attendance (defaults to today)
        user_id: User ID who recorded the time-in
    
    Returns:
        (success, message)
    """
    if time_in_time is None:
        time_in_time = datetime.now().time()
    if attendance_date is None:
        attendance_date = date.today()
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check if attendance record already exists
                cur.execute("""
                    SELECT id, time_in FROM attendance 
                    WHERE employee_id = %s AND attendance_date = %s
                """, (employee_id, attendance_date))
                existing = cur.fetchone()
                
                if existing:
                    if existing[1]:  # Time-in already recorded
                        return False, "Time-in already recorded for this date."
                    # Update existing record
                    cur.execute("""
                        UPDATE attendance 
                        SET time_in = %s, created_by = %s, status = 'PRESENT',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (time_in_time, user_id, existing[0]))
                else:
                    # Create new attendance record
                    cur.execute("""
                        INSERT INTO attendance 
                        (employee_id, attendance_date, time_in, status, created_by)
                        VALUES (%s, %s, %s, 'PRESENT', %s)
                    """, (employee_id, attendance_date, time_in_time, user_id))
                
                conn.commit()
                
                # Log audit
                log_audit(user_id, "Time In", f"Employee {employee_id} time-in recorded: {time_in_time}")
                
                return True, "Time-in recorded successfully."
    except Exception as e:
        return False, f"Failed to record time-in: {str(e)}"


def time_out(employee_id: int, time_out_time: Optional[time] = None,
             attendance_date: Optional[date] = None, user_id: Optional[int] = None) -> Tuple[bool, str, Optional[Dict]]:
    """
    Record time-out for an employee and calculate hours worked, late, undertime, overtime.
    
    Args:
        employee_id: Employee ID
        time_out_time: Time-out time (defaults to current time)
        attendance_date: Date of attendance (defaults to today)
        user_id: User ID who recorded the time-out
    
    Returns:
        (success, message, attendance_data)
    """
    if time_out_time is None:
        time_out_time = datetime.now().time()
    if attendance_date is None:
        attendance_date = date.today()
    
    try:
        settings = get_company_work_settings()
        scheduled_start = datetime.strptime(settings.get('regular_work_start_time', '08:00:00'), '%H:%M:%S').time()
        scheduled_end = datetime.strptime(settings.get('regular_work_end_time', '17:00:00'), '%H:%M:%S').time()
        regular_hours_per_day = settings.get('regular_work_hours_per_day', 8.0)
        
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                # Get existing attendance record
                cur.execute("""
                    SELECT * FROM attendance 
                    WHERE employee_id = %s AND attendance_date = %s
                """, (employee_id, attendance_date))
                attendance = cur.fetchone()
                
                if not attendance or not attendance['time_in']:
                    return False, "Time-in must be recorded before time-out.", None
                
                if attendance['time_out']:
                    return False, "Time-out already recorded for this date.", None
                
                time_in_time = attendance['time_in']
                
                # Convert timedelta to time if needed
                if isinstance(time_in_time, timedelta):
                    # Convert timedelta to time (extract hours, minutes, seconds)
                    total_seconds = int(time_in_time.total_seconds())
                    hours = (total_seconds // 3600) % 24
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    time_in_time = time(hours, minutes, seconds)
                
                # Calculate hours and metrics
                total_hours = calculate_hours_worked(time_in_time, time_out_time)
                late_minutes = calculate_late_minutes(time_in_time, scheduled_start)
                undertime_minutes = calculate_undertime_minutes(time_out_time, scheduled_end)
                regular_hours = min(total_hours, regular_hours_per_day)
                overtime_hours = calculate_overtime_hours(time_out_time, scheduled_end, regular_hours)
                night_diff_hours = calculate_night_differential_hours(
                    time_in_time, time_out_time,
                    datetime.strptime(settings.get('night_differential_start', '22:00:00'), '%H:%M:%S').time(),
                    datetime.strptime(settings.get('night_differential_end', '06:00:00'), '%H:%M:%S').time()
                )
                
                # Determine status
                status = 'PRESENT'
                if late_minutes > 0:
                    status = 'LATE'
                
                # Update attendance record
                cur.execute("""
                    UPDATE attendance 
                    SET time_out = %s,
                        hours_worked = %s,
                        regular_hours = %s,
                        overtime_hours = %s,
                        night_differential_hours = %s,
                        late_minutes = %s,
                        undertime_minutes = %s,
                        status = %s,
                        updated_by = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    time_out_time, total_hours, regular_hours, overtime_hours,
                    night_diff_hours, late_minutes, undertime_minutes, status,
                    user_id, attendance['id']
                ))
                
                conn.commit()
                
                # Prepare return data
                attendance_data = {
                    'hours_worked': total_hours,
                    'regular_hours': regular_hours,
                    'overtime_hours': overtime_hours,
                    'night_differential_hours': night_diff_hours,
                    'late_minutes': late_minutes,
                    'undertime_minutes': undertime_minutes,
                    'status': status
                }
                
                # Log audit
                log_audit(user_id, "Time Out", 
                         f"Employee {employee_id} time-out recorded: {time_out_time}. Hours: {total_hours}, OT: {overtime_hours}")
                
                return True, "Time-out recorded successfully.", attendance_data
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, f"Failed to record time-out: {str(e)}", None


def get_employee_attendance(employee_id: int, start_date: date, end_date: date) -> List[Dict]:
    """Get attendance records for an employee within a date range."""
    query = """
        SELECT * FROM attendance
        WHERE employee_id = %s 
        AND attendance_date >= %s 
        AND attendance_date <= %s
        ORDER BY attendance_date DESC
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (employee_id, start_date, end_date))
            return cur.fetchall()


def get_today_attendance(employee_id: int) -> Optional[Dict]:
    """Get today's attendance record for an employee."""
    today = date.today()
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT * FROM attendance
                WHERE employee_id = %s AND attendance_date = %s
            """, (employee_id, today))
            return cur.fetchone()


def update_attendance(attendance_id: int, updates: Dict, user_id: int) -> bool:
    """
    Update attendance record (requires authorization - typically HR/Admin only).
    
    Args:
        attendance_id: Attendance record ID
        updates: Dictionary of fields to update
        user_id: User ID making the update
    
    Returns:
        True if successful
    """
    try:
        set_clauses = []
        params = []
        
        allowed_fields = ['time_in', 'time_out', 'status', 'notes', 'is_holiday', 'is_rest_day']
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = %s")
                params.append(value)
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_by = %s")
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        params.append(attendance_id)
        
        query = f"UPDATE attendance SET {', '.join(set_clauses)} WHERE id = %s"
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                
                # Recalculate hours if time_in or time_out changed
                if 'time_in' in updates or 'time_out' in updates:
                    cur.execute("SELECT time_in, time_out FROM attendance WHERE id = %s", (attendance_id,))
                    record = cur.fetchone()
                    if record and record[0] and record[1]:
                        # Recalculate hours
                        total_hours = calculate_hours_worked(record[0], record[1])
                        cur.execute("UPDATE attendance SET hours_worked = %s WHERE id = %s", 
                                  (total_hours, attendance_id))
                        conn.commit()
                
                log_audit(user_id, "Update Attendance", f"Updated attendance record {attendance_id}")
                return True
    except Exception as e:
        logger.exception("Error updating attendance: %s", e)
        return False

