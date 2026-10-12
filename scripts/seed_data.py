"""
CareSync Database Seeding Script
Populates fictional medical staff, patient accounts, realistic schedules,
sample appointments, and queue tokens for demonstration and lab viva.
"""
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db, get_db_path, get_db
from app.models import (
    create_user, create_doctor, set_doctor_availability,
    create_appointment, check_in_patient, update_queue_status,
    log_activity
)

def seed_database():
    db_path = get_db_path()
    print(f"[CareSync] Seeding database at: {db_path}")
    init_db(db_path)
    db = get_db(db_path)

    # Check if admin already exists
    existing = db.execute("SELECT id FROM users WHERE username = 'admin'").fetchone()
    if existing:
        print("[CareSync] Database already seeded. Skipping to prevent duplicate records.")
        return

    # 1. Create Administrator
    admin_id = create_user(
        username='admin',
        email='admin@caresync.hospital',
        password='admin123',
        role='admin',
        full_name='Hospital Administrator',
        phone='+1-800-555-0100'
    )
    print("  + Created Administrator: admin / admin123")

    # 2. Create Doctors
    doctors_meta = [
        {
            'username': 'dr.sarah',
            'email': 'sarah.jenkins@caresync.hospital',
            'full_name': 'Dr. Sarah Jenkins',
            'doctor_code': 'DOC-101',
            'specialty': 'Cardiology',
            'qualification': 'MD, FACC - Harvard Medical',
            'fee': 600.0,
            'dept': 'Cardiovascular Sciences',
            'phone': '+1-800-555-0101'
        },
        {
            'username': 'dr.david',
            'email': 'david.chen@caresync.hospital',
            'full_name': 'Dr. David Chen',
            'doctor_code': 'DOC-102',
            'specialty': 'Neurology',
            'qualification': 'MD, PhD - Johns Hopkins',
            'fee': 700.0,
            'dept': 'Neurosciences',
            'phone': '+1-800-555-0102'
        },
        {
            'username': 'dr.emily',
            'email': 'emily.watson@caresync.hospital',
            'full_name': 'Dr. Emily Watson',
            'doctor_code': 'DOC-103',
            'specialty': 'Pediatrics',
            'qualification': 'MBBS, DCH, MD - Stanford',
            'fee': 450.0,
            'dept': 'Child Healthcare',
            'phone': '+1-800-555-0103'
        },
        {
            'username': 'dr.robert',
            'email': 'robert.miller@caresync.hospital',
            'full_name': 'Dr. Robert Miller',
            'doctor_code': 'DOC-104',
            'specialty': 'Orthopedics',
            'qualification': 'MS, M.Ch (Ortho) - Oxford',
            'fee': 550.0,
            'dept': 'Orthopedic Surgery',
            'phone': '+1-800-555-0104'
        }
    ]

    doctor_ids = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    for doc in doctors_meta:
        uid = create_user(
            username=doc['username'],
            email=doc['email'],
            password='doctor123',
            role='doctor',
            full_name=doc['full_name'],
            phone=doc['phone']
        )
        doc_id = create_doctor(
            user_id=uid,
            doctor_code=doc['doctor_code'],
            specialty=doc['specialty'],
            qualification=doc['qualification'],
            consultation_fee=doc['fee'],
            department=doc['dept']
        )
        doctor_ids.append(doc_id)

        # Set standard schedules (09:00 to 17:00, 30 min slots)
        for day in days:
            set_doctor_availability(doc_id, day, "09:00", "17:00", 30)

        print(f"  + Created Doctor: {doc['username']} / doctor123 ({doc['specialty']})")

    # 3. Create Sample Patients
    patients_meta = [
        {'username': 'john_doe', 'email': 'john@example.com', 'full_name': 'John Doe', 'phone': '+1-555-0191'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'full_name': 'Jane Smith', 'phone': '+1-555-0192'},
        {'username': 'alex_taylor', 'email': 'alex@example.com', 'full_name': 'Alex Taylor', 'phone': '+1-555-0193'},
        {'username': 'maria_garcia', 'email': 'maria@example.com', 'full_name': 'Maria Garcia', 'phone': '+1-555-0194'},
    ]

    patient_ids = []
    for pat in patients_meta:
        pid = create_user(
            username=pat['username'],
            email=pat['email'],
            password='patient123',
            role='patient',
            full_name=pat['full_name'],
            phone=pat['phone']
        )
        patient_ids.append(pid)
        print(f"  + Created Patient: {pat['username']} / patient123")

    # 4. Create Appointments
    today_str = date.today().strftime("%Y-%m-%d")
    tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Today's appointments for Dr. Sarah Jenkins (Cardiology)
    app1, _ = create_appointment(patient_ids[0], doctor_ids[0], today_str, "09:00", "Routine hypertension checkup and ECG")
    app2, _ = create_appointment(patient_ids[1], doctor_ids[0], today_str, "09:30", "Follow-up for elevated cholesterol levels")
    app3, _ = create_appointment(patient_ids[2], doctor_ids[0], today_str, "10:00", "Mild chest pain consultation")

    # Today's appointments for Dr. David Chen (Neurology)
    app4, _ = create_appointment(patient_ids[3], doctor_ids[1], today_str, "09:30", "Recurring migraine headaches assessment")

    # Tomorrow's appointment
    app5, _ = create_appointment(patient_ids[0], doctor_ids[2], tomorrow_str, "10:30", "Pediatric consultation for newborn vaccination")

    print("  + Created 5 sample appointments across doctors.")

    # 5. Check in some patients to populate live queue board
    if app1:
        entry1, _ = check_in_patient(app1['id'])
        if entry1:
            update_queue_status(entry1['id'], 'In Consultation')
            print(f"  + Patient John Doe checked in -> Token #{entry1['queue_number']} (In Consultation)")

    if app2:
        entry2, _ = check_in_patient(app2['id'])
        if entry2:
            print(f"  + Patient Jane Smith checked in -> Token #{entry2['queue_number']} (Waiting)")

    if app4:
        entry4, _ = check_in_patient(app4['id'])
        if entry4:
            print(f"  + Patient Maria Garcia checked in -> Token #{entry4['queue_number']} (Waiting)")

    # 6. Audit logs
    log_activity(admin_id, 'SYSTEM_INIT', "System initialization and sample dataset seeded", '127.0.0.1')
    print("[CareSync] Database seeding completed successfully!")
    print("\nDefault Logins:")
    print("  Admin:   admin / admin123")
    print("  Doctor:  dr.sarah / doctor123")
    print("  Patient: john_doe / patient123\n")


if __name__ == '__main__':
    seed_database()
