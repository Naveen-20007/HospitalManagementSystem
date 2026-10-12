"""
CareSync Database Persistence & Constraint Tests
Verifies that SQLite transactions persist across distinct connection instances
and that foreign key constraints remain active.
"""
import sqlite3
import os
import tempfile
from app.db import init_db
from app.models import create_user, get_user_by_username


def test_sqlite_persistence_across_connections():
    """Verify data written to SQLite persists after closing and reopening connections."""
    fd, path = tempfile.mkstemp(suffix='.db', prefix='persist_test_')
    os.close(fd)

    try:
        # Initialize schema
        init_db(path)

        # Connection 1: Insert user
        conn1 = sqlite3.connect(path)
        conn1.execute("PRAGMA foreign_keys = ON;")
        conn1.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, ('persist_user', 'persist@test.com', 'hash123', 'patient', 'Persistent Patient'))
        conn1.commit()
        conn1.close()  # Completely closed

        # Connection 2: Re-open from disk and read back
        conn2 = sqlite3.connect(path)
        conn2.row_factory = sqlite3.Row
        row = conn2.execute("SELECT * FROM users WHERE username = 'persist_user'").fetchone()
        assert row is not None
        assert row['full_name'] == 'Persistent Patient'
        assert row['email'] == 'persist@test.com'
        conn2.close()

    finally:
        if os.path.exists(path):
            os.remove(path)


def test_foreign_key_enforcement():
    """Verify that foreign key constraints prevent orphan records."""
    fd, path = tempfile.mkstemp(suffix='.db', prefix='fk_test_')
    os.close(fd)

    try:
        init_db(path)
        conn = sqlite3.connect(path)
        conn.execute("PRAGMA foreign_keys = ON;")

        # Attempt to insert doctor with non-existent user_id (99999)
        import pytest
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO doctors (user_id, doctor_code, specialty, qualification, department)
                VALUES (99999, 'INVALID-DOC', 'Cardiology', 'MD', 'Cardio')
            """)
        conn.close()

    finally:
        if os.path.exists(path):
            os.remove(path)
