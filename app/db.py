"""
CareSync Database Management Module
Handles SQLite connection, schema definition, initialization, and transactions.
"""
import sqlite3
import os
from flask import g, current_app

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'caresync.db')

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient')),
    full_name TEXT NOT NULL,
    phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    doctor_code TEXT UNIQUE NOT NULL,
    specialty TEXT NOT NULL,
    qualification TEXT NOT NULL,
    consultation_fee REAL DEFAULT 500.0,
    department TEXT NOT NULL,
    is_available INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS doctor_availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    slot_duration_mins INTEGER DEFAULT 30,
    UNIQUE(doctor_id, day_of_week),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_code TEXT UNIQUE NOT NULL,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Confirmed', 'Checked In', 'Completed', 'Cancelled')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS queue_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER UNIQUE NOT NULL,
    queue_number INTEGER NOT NULL,
    queue_date TEXT NOT NULL,
    doctor_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Waiting' CHECK(status IN ('Waiting', 'In Consultation', 'Completed', 'Skipped', 'Cancelled')),
    check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    called_time TIMESTAMP,
    completed_time TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Indices for rapid lookup in dashboards and scheduling queries
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date ON appointments(doctor_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_queue_date_doc ON queue_entries(queue_date, doctor_id, status);
CREATE INDEX IF NOT EXISTS idx_activity_time ON activity_logs(timestamp DESC);
"""


def get_db_path():
    """Retrieve active database path from Flask config, environment, or default."""
    try:
        if current_app:
            return current_app.config.get('DATABASE', os.environ.get('DATABASE_PATH', DEFAULT_DB_PATH))
    except RuntimeError:
        pass
    return os.environ.get('DATABASE_PATH', DEFAULT_DB_PATH)


def get_db(db_path=None):
    """
    Get a database connection.
    In Flask request context, reuses g._database; otherwise opens a direct connection.
    """
    path = db_path or get_db_path()

    # Ensure parent directory exists (for instance/ or volume paths)
    db_dir = os.path.dirname(path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    if current_app:
        if '_database' not in g or g.get('_db_path') != path:
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            g._database = conn
            g._db_path = path
        return g._database

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('_database', None)
    if db is not None:
        db.close()


def init_db(db_path=None):
    """Initialize SQLite database with schema."""
    conn = get_db(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    if not current_app:
        conn.close()
