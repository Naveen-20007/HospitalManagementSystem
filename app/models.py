"""
CareSync Data Access Layer (Models & Services)
Provides relational queries, business logic, password security,
conflict validation, and queue computation using SQLite.
"""
from datetime import datetime, date, time, timedelta
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db


# ============================================================================
# USER MANAGEMENT & AUTHENTICATION
# ============================================================================

def create_user(username, email, password, role, full_name, phone=None):
    """Create a new user with hashed password."""
    db = get_db()
    hashed = generate_password_hash(password, method='scrypt')
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, full_name, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username.strip().lower(), email.strip().lower(), hashed, role, full_name.strip(), phone))
    db.commit()
    return cursor.lastrowid


def get_user_by_id(user_id):
    """Retrieve user dictionary by ID."""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def get_user_by_username(username):
    """Retrieve user by username."""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),)).fetchone()
    return dict(row) if row else None


def get_user_by_email(email):
    """Retrieve user by email address."""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    return dict(row) if row else None


def verify_user_credentials(username_or_email, password):
    """Verify username/email and password. Returns user dict or None."""
    db = get_db()
    clean_identifier = username_or_email.strip().lower()
    row = db.execute("""
        SELECT * FROM users 
        WHERE (username = ? OR email = ?) AND is_active = 1
    """, (clean_identifier, clean_identifier)).fetchone()
    if not row:
        return None
    user = dict(row)
    if check_password_hash(user['password_hash'], password):
        return user
    return None


def update_user_profile(user_id, full_name, phone):
    """Update profile details."""
    db = get_db()
    db.execute("""
        UPDATE users 
        SET full_name = ?, phone = ?
        WHERE id = ?
    """, (full_name.strip(), phone, user_id))
    db.commit()


def list_users(role=None):
    """List registered users with optional role filtering."""
    db = get_db()
    if role:
        rows = db.execute("SELECT * FROM users WHERE role = ? ORDER BY created_at DESC", (role,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


# ============================================================================
# DOCTOR MANAGEMENT
# ============================================================================

def create_doctor(user_id, doctor_code, specialty, qualification, consultation_fee=500.0, department='Outpatient'):
    """Link a user account as a doctor profile."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO doctors (user_id, doctor_code, specialty, qualification, consultation_fee, department, is_available)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (user_id, doctor_code.upper().strip(), specialty.strip(), qualification.strip(), float(consultation_fee), department.strip()))
    db.commit()
    return cursor.lastrowid


def get_doctor_by_id(doctor_id):
    """Get doctor details joined with user table."""
    db = get_db()
    row = db.execute("""
        SELECT d.*, u.full_name, u.email, u.phone, u.username
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.id = ?
    """, (doctor_id,)).fetchone()
    return dict(row) if row else None


def get_doctor_by_user_id(user_id):
    """Get doctor profile from user ID."""
    db = get_db()
    row = db.execute("""
        SELECT d.*, u.full_name, u.email, u.phone, u.username
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE d.user_id = ?
    """, (user_id,)).fetchone()
    return dict(row) if row else None


def list_doctors(specialty=None, available_only=False, search=None):
    """List doctors with search and filter capabilities."""
    db = get_db()
    query = """
        SELECT d.*, u.full_name, u.email, u.phone
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        WHERE 1=1
    """
    params = []
    if specialty:
        query += " AND d.specialty = ?"
        params.append(specialty)
    if available_only:
        query += " AND d.is_available = 1"
    if search:
        query += " AND (u.full_name LIKE ? OR d.specialty LIKE ? OR d.department LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])
    query += " ORDER BY u.full_name ASC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def update_doctor(doctor_id, specialty, qualification, consultation_fee, department, is_available):
    """Update doctor parameters."""
    db = get_db()
    db.execute("""
        UPDATE doctors
        SET specialty = ?, qualification = ?, consultation_fee = ?, department = ?, is_available = ?
        WHERE id = ?
    """, (specialty.strip(), qualification.strip(), float(consultation_fee), department.strip(), 1 if is_available else 0, doctor_id))
    db.commit()


def set_doctor_availability(doctor_id, day_of_week, start_time, end_time, slot_duration_mins=30):
    """Set or replace working schedule for a doctor on a specific weekday."""
    db = get_db()
    db.execute("""
        INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_mins)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(doctor_id, day_of_week) DO UPDATE SET
            start_time = excluded.start_time,
            end_time = excluded.end_time,
            slot_duration_mins = excluded.slot_duration_mins
    """, (doctor_id, day_of_week, start_time, end_time, int(slot_duration_mins)))
    db.commit()


def get_doctor_availability(doctor_id):
    """Fetch all working days and hours for a doctor."""
    db = get_db()
    rows = db.execute("""
        SELECT * FROM doctor_availability
        WHERE doctor_id = ?
        ORDER BY 
            CASE day_of_week
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END
    """, (doctor_id,)).fetchall()
    return [dict(r) for r in rows]


def get_available_slots(doctor_id, appointment_date_str):
    """
    Generate all valid time slots for a doctor on a specific date,
    excluding booked active slots and past slots if booking for today.
    """
    db = get_db()
    try:
        app_date = datetime.strptime(appointment_date_str, "%Y-%m-%d").date()
    except ValueError:
        return []

    day_name = app_date.strftime("%A")  # e.g., 'Monday'
    avail = db.execute("""
        SELECT * FROM doctor_availability
        WHERE doctor_id = ? AND day_of_week = ?
    """, (doctor_id, day_name)).fetchone()

    # If no specific schedule is entered, provide default 09:00 - 17:00 weekdays schedule
    if not avail:
        if day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
            start_t = time(9, 0)
            end_t = time(17, 0)
            duration = 30
        else:
            return []  # Sunday closed by default if not set
    else:
        avail_dict = dict(avail)
        start_parts = [int(p) for p in avail_dict['start_time'].split(':')]
        end_parts = [int(p) for p in avail_dict['end_time'].split(':')]
        start_t = time(start_parts[0], start_parts[1])
        end_t = time(end_parts[0], end_parts[1])
        duration = avail_dict['slot_duration_mins']

    # Get already booked non-cancelled slots for this doctor and date
    booked_rows = db.execute("""
        SELECT time_slot FROM appointments
        WHERE doctor_id = ? AND appointment_date = ? AND status != 'Cancelled'
    """, (doctor_id, appointment_date_str)).fetchall()
    booked_slots = set(r['time_slot'] for r in booked_rows)

    # Generate slots from start to end
    slots = []
    curr_dt = datetime.combine(app_date, start_t)
    end_dt = datetime.combine(app_date, end_t)
    now = datetime.now()

    while curr_dt + timedelta(minutes=duration) <= end_dt:
        slot_str = curr_dt.strftime("%H:%M")
        is_booked = slot_str in booked_slots
        # Check if slot is already in the past for today
        is_past = (app_date == now.date() and curr_dt < now)

        slots.append({
            'time': slot_str,
            'is_available': not is_booked and not is_past,
            'status': 'Booked' if is_booked else ('Past' if is_past else 'Available')
        })
        curr_dt += timedelta(minutes=duration)

    return slots


# ============================================================================
# APPOINTMENT MANAGEMENT
# ============================================================================

def generate_appointment_code():
    """Generate a clean, professional appointment reference code (e.g. CS-20261012-A492)."""
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"CS-{date_part}-{random_part}"


def create_appointment(patient_id, doctor_id, appointment_date, time_slot, reason):
    """
    Book an appointment.
    Performs backend validations:
    - Date cannot be in the past.
    - Slot cannot already be booked by an active appointment.
    - Doctor must be marked active/available.
    Returns: (appointment_dict, None) or (None, error_message)
    """
    db = get_db()

    # Validate date
    try:
        app_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()
    except ValueError:
        return None, "Invalid appointment date format. Use YYYY-MM-DD."

    today = date.today()
    if app_date < today:
        return None, "Appointments cannot be booked for past dates."

    # Validate doctor
    doc = get_doctor_by_id(doctor_id)
    if not doc or not doc['is_available']:
        return None, "Selected doctor is currently unavailable for booking."

    # Prevent duplicate booking for the same doctor, date, and slot
    existing = db.execute("""
        SELECT id FROM appointments
        WHERE doctor_id = ? AND appointment_date = ? AND time_slot = ? AND status != 'Cancelled'
    """, (doctor_id, appointment_date, time_slot)).fetchone()

    if existing:
        return None, f"Time slot {time_slot} is already booked for this doctor on {appointment_date}."

    # Generate unique code and insert
    code = generate_appointment_code()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO appointments (appointment_code, patient_id, doctor_id, appointment_date, time_slot, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Confirmed')
    """, (code, patient_id, doctor_id, appointment_date, time_slot, reason.strip()))
    app_id = cursor.lastrowid
    db.commit()

    return get_appointment_by_id(app_id), None


def get_appointment_by_id(appointment_id):
    """Fetch complete appointment record with doctor and patient details."""
    db = get_db()
    row = db.execute("""
        SELECT a.*,
               u_pat.full_name AS patient_name, u_pat.email AS patient_email, u_pat.phone AS patient_phone,
               u_doc.full_name AS doctor_name, d.specialty AS doctor_specialty, d.doctor_code,
               d.consultation_fee, d.department,
               q.queue_number, q.status AS queue_status
        FROM appointments a
        JOIN users u_pat ON a.patient_id = u_pat.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u_doc ON d.user_id = u_doc.id
        LEFT JOIN queue_entries q ON a.id = q.appointment_id
        WHERE a.id = ?
    """, (appointment_id,)).fetchone()
    return dict(row) if row else None


def list_appointments(patient_id=None, doctor_id=None, app_date=None, status=None, search=None):
    """Search and filter appointments by role, date, status, or keyword."""
    db = get_db()
    query = """
        SELECT a.*,
               u_pat.full_name AS patient_name, u_pat.email AS patient_email, u_pat.phone AS patient_phone,
               u_doc.full_name AS doctor_name, d.specialty AS doctor_specialty, d.doctor_code,
               q.queue_number, q.status AS queue_status
        FROM appointments a
        JOIN users u_pat ON a.patient_id = u_pat.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN users u_doc ON d.user_id = u_doc.id
        LEFT JOIN queue_entries q ON a.id = q.appointment_id
        WHERE 1=1
    """
    params = []
    if patient_id:
        query += " AND a.patient_id = ?"
        params.append(patient_id)
    if doctor_id:
        query += " AND a.doctor_id = ?"
        params.append(doctor_id)
    if app_date:
        query += " AND a.appointment_date = ?"
        params.append(app_date)
    if status:
        query += " AND a.status = ?"
        params.append(status)
    if search:
        query += " AND (a.appointment_code LIKE ? OR u_pat.full_name LIKE ? OR u_doc.full_name LIKE ? OR a.reason LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s])

    query += " ORDER BY a.appointment_date DESC, a.time_slot ASC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def update_appointment_status(appointment_id, new_status, notes=None):
    """Update appointment state with valid transitions."""
    valid_statuses = ['Pending', 'Confirmed', 'Checked In', 'Completed', 'Cancelled']
    if new_status not in valid_statuses:
        return False, f"Invalid status: {new_status}"

    db = get_db()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if notes:
        db.execute("""
            UPDATE appointments
            SET status = ?, notes = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, notes, now_str, appointment_id))
    else:
        db.execute("""
            UPDATE appointments
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, now_str, appointment_id))

    # Sync queue status if applicable
    if new_status == 'Completed':
        db.execute("""
            UPDATE queue_entries 
            SET status = 'Completed', completed_time = ?
            WHERE appointment_id = ?
        """, (now_str, appointment_id))
    elif new_status == 'Cancelled':
        db.execute("""
            UPDATE queue_entries 
            SET status = 'Cancelled'
            WHERE appointment_id = ?
        """, (appointment_id,))

    db.commit()
    return True, None


def cancel_appointment(appointment_id, user_id=None, role=None):
    """Cancel an appointment with ownership verification."""
    db = get_db()
    app = get_appointment_by_id(appointment_id)
    if not app:
        return False, "Appointment not found."

    # Authorization check
    if role == 'patient' and app['patient_id'] != user_id:
        return False, "You are not authorized to cancel this appointment."

    if app['status'] in ['Completed', 'Cancelled']:
        return False, f"Cannot cancel an appointment that is already {app['status']}."

    return update_appointment_status(appointment_id, 'Cancelled', notes="Cancelled by user/admin.")


# ============================================================================
# QUEUE MANAGEMENT
# ============================================================================

def check_in_patient(appointment_id):
    """
    Check-in patient upon arrival at hospital.
    Generates incremental queue number per doctor per day.
    Updates appointment status to 'Checked In'.
    """
    db = get_db()
    app = get_appointment_by_id(appointment_id)
    if not app:
        return None, "Appointment not found."

    if app['status'] == 'Cancelled':
        return None, "Cannot check in a cancelled appointment."

    # Check if already has a queue entry
    existing = db.execute("SELECT * FROM queue_entries WHERE appointment_id = ?", (appointment_id,)).fetchone()
    if existing:
        return dict(existing), "Patient is already checked in."

    # Compute next queue number for this doctor on this day
    row = db.execute("""
        SELECT COALESCE(MAX(queue_number), 0) + 1 AS next_num
        FROM queue_entries
        WHERE doctor_id = ? AND queue_date = ?
    """, (app['doctor_id'], app['appointment_date'])).fetchone()
    next_num = row['next_num']

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO queue_entries (appointment_id, queue_number, queue_date, doctor_id, status)
        VALUES (?, ?, ?, ?, 'Waiting')
    """, (appointment_id, next_num, app['appointment_date'], app['doctor_id']))
    queue_id = cursor.lastrowid

    # Update appointment status
    db.execute("UPDATE appointments SET status = 'Checked In', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (appointment_id,))
    db.commit()

    entry = db.execute("SELECT * FROM queue_entries WHERE id = ?", (queue_id,)).fetchone()
    return dict(entry), None


def get_live_queue(date_str=None, doctor_id=None):
    """Get active queue entries for hospital live monitor board."""
    db = get_db()
    target_date = date_str or date.today().strftime("%Y-%m-%d")
    query = """
        SELECT q.*,
               a.appointment_code, a.time_slot,
               u_pat.full_name AS patient_name,
               u_doc.full_name AS doctor_name, d.specialty, d.doctor_code
        FROM queue_entries q
        JOIN appointments a ON q.appointment_id = a.id
        JOIN users u_pat ON a.patient_id = u_pat.id
        JOIN doctors d ON q.doctor_id = d.id
        JOIN users u_doc ON d.user_id = u_doc.id
        WHERE q.queue_date = ?
    """
    params = [target_date]
    if doctor_id:
        query += " AND q.doctor_id = ?"
        params.append(doctor_id)

    query += " ORDER BY q.queue_number ASC"
    rows = db.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def update_queue_status(queue_id, new_status):
    """Change queue state: Waiting -> In Consultation -> Completed / Skipped."""
    valid_statuses = ['Waiting', 'In Consultation', 'Completed', 'Skipped', 'Cancelled']
    if new_status not in valid_statuses:
        return False, f"Invalid queue status: {new_status}"

    db = get_db()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if new_status == 'In Consultation':
        db.execute("UPDATE queue_entries SET status = ?, called_time = ? WHERE id = ?", (new_status, now_str, queue_id))
    elif new_status == 'Completed':
        # Get appointment ID to mark appointment completed as well
        entry = db.execute("SELECT appointment_id FROM queue_entries WHERE id = ?", (queue_id,)).fetchone()
        db.execute("UPDATE queue_entries SET status = ?, completed_time = ? WHERE id = ?", (new_status, now_str, queue_id))
        if entry:
            db.execute("UPDATE appointments SET status = 'Completed', updated_at = ? WHERE id = ?", (now_str, entry['appointment_id']))
    else:
        db.execute("UPDATE queue_entries SET status = ? WHERE id = ?", (new_status, queue_id))

    db.commit()
    return True, None


# ============================================================================
# AUDIT LOGGING & SYSTEM ACTIVITY
# ============================================================================

def log_activity(user_id, action, details=None, ip_address=None):
    """Record an audit trail entry."""
    db = get_db()
    db.execute("""
        INSERT INTO activity_logs (user_id, action, details, ip_address)
        VALUES (?, ?, ?, ?)
    """, (user_id, action, details, ip_address))
    db.commit()


def list_recent_activity(limit=15):
    """Retrieve the most recent audit activity records."""
    db = get_db()
    rows = db.execute("""
        SELECT l.*, u.username, u.full_name, u.role
        FROM activity_logs l
        LEFT JOIN users u ON l.user_id = u.id
        ORDER BY l.timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()
    return [dict(r) for r in rows]


# ============================================================================
# REAL-TIME DASHBOARD STATISTICS & REPORTING
# ============================================================================

def get_hospital_stats():
    """Calculate aggregate hospital statistics dynamically from the database."""
    db = get_db()
    today_str = date.today().strftime("%Y-%m-%d")

    total_patients = db.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'patient'").fetchone()['c']
    total_doctors = db.execute("SELECT COUNT(*) AS c FROM doctors WHERE is_available = 1").fetchone()['c']
    today_appointments = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE appointment_date = ?", (today_str,)).fetchone()['c']
    pending_appointments = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE status = 'Confirmed'").fetchone()['c']
    completed_appointments = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE status = 'Completed'").fetchone()['c']
    cancelled_appointments = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE status = 'Cancelled'").fetchone()['c']
    waiting_in_queue = db.execute("SELECT COUNT(*) AS c FROM queue_entries WHERE queue_date = ? AND status = 'Waiting'", (today_str,)).fetchone()['c']
    serving_in_queue = db.execute("SELECT COUNT(*) AS c FROM queue_entries WHERE queue_date = ? AND status = 'In Consultation'", (today_str,)).fetchone()['c']

    return {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'waiting_in_queue': waiting_in_queue,
        'serving_in_queue': serving_in_queue,
    }


def get_doctor_stats(doctor_id):
    """Calculate statistics for a specific doctor's portal."""
    db = get_db()
    today_str = date.today().strftime("%Y-%m-%d")

    total_assigned = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_id = ?", (doctor_id,)).fetchone()['c']
    today_total = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_id = ? AND appointment_date = ?", (doctor_id, today_str)).fetchone()['c']
    today_completed = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_id = ? AND appointment_date = ? AND status = 'Completed'", (doctor_id, today_str)).fetchone()['c']
    today_waiting = db.execute("""
        SELECT COUNT(*) AS c FROM queue_entries
        WHERE doctor_id = ? AND queue_date = ? AND status = 'Waiting'
    """, (doctor_id, today_str)).fetchone()['c']

    return {
        'total_assigned': total_assigned,
        'today_total': today_total,
        'today_completed': today_completed,
        'today_waiting': today_waiting,
    }


def get_patient_stats(patient_id):
    """Calculate statistics for a patient portal."""
    db = get_db()
    today_str = date.today().strftime("%Y-%m-%d")

    total = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE patient_id = ?", (patient_id,)).fetchone()['c']
    upcoming = db.execute("""
        SELECT COUNT(*) AS c FROM appointments 
        WHERE patient_id = ? AND appointment_date >= ? AND status IN ('Confirmed', 'Checked In')
    """, (patient_id, today_str)).fetchone()['c']
    completed = db.execute("SELECT COUNT(*) AS c FROM appointments WHERE patient_id = ? AND status = 'Completed'", (patient_id,)).fetchone()['c']

    return {
        'total': total,
        'upcoming': upcoming,
        'completed': completed,
    }


def get_report_data(start_date=None, end_date=None, doctor_id=None):
    """Generate analytical reports across specified date range."""
    db = get_db()
    query = """
        SELECT a.status, COUNT(*) AS count
        FROM appointments a
        WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND a.appointment_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND a.appointment_date <= ?"
        params.append(end_date)
    if doctor_id:
        query += " AND a.doctor_id = ?"
        params.append(doctor_id)

    query += " GROUP BY a.status"
    status_counts = {r['status']: r['count'] for r in db.execute(query, params).fetchall()}

    # Doctor workload summary
    workload_query = """
        SELECT d.id AS doctor_id, u.full_name AS doctor_name, d.specialty,
               COUNT(a.id) AS total_appointments,
               SUM(CASE WHEN a.status = 'Completed' THEN 1 ELSE 0 END) AS completed_count,
               SUM(CASE WHEN a.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_count
        FROM doctors d
        JOIN users u ON d.user_id = u.id
        LEFT JOIN appointments a ON d.id = a.doctor_id
    """
    w_params = []
    if start_date or end_date:
        workload_query += " AND 1=1"
        if start_date:
            workload_query += " AND a.appointment_date >= ?"
            w_params.append(start_date)
        if end_date:
            workload_query += " AND a.appointment_date <= ?"
            w_params.append(end_date)

    workload_query += " GROUP BY d.id, u.full_name, d.specialty ORDER BY total_appointments DESC"
    workload_rows = [dict(r) for r in db.execute(workload_query, w_params).fetchall()]

    return {
        'status_counts': status_counts,
        'doctor_workload': workload_rows,
        'total_appointments': sum(status_counts.values())
    }
