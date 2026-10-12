# CareSync — System Architecture & Design Specification
## 23IT723 — DevOps Laboratory Project

---

## 1. System Overview

**CareSync** is a full-stack Hospital Appointment Management System engineered with an automated CI/CD deployment pipeline. The platform addresses core clinical operational workflows:
- Patient self-registration, specialty browsing, and dynamic slot reservation.
- Real-time double-booking validation and appointment lifecycle management.
- Sequential patient queue token generation and waiting-room live status display.
- Doctor consultation scheduling and administrative clinical auditing.
- Automated testing, containerization, configuration management, and reverse proxying.

---

## 2. Architectural Diagram

```mermaid
graph TD
    User["Patient / Doctor / Admin Browser"] -->|HTTP / Port 8080| Nginx["Nginx Reverse Proxy (caresync-nginx:80)"]
    
    subgraph Docker Network: caresync-net
        Nginx -->|Proxy Pass / Port 5000| Gunicorn["Gunicorn WSGI Server (2 Workers, 2 Threads)"]
        Gunicorn --> FlaskApp["CareSync Flask Application"]
        
        subgraph Flask Modular Blueprints
            FlaskApp --> AuthBP["Auth & RBAC Blueprint (/auth)"]
            FlaskApp --> DashBP["Dashboard Blueprint (/dashboard)"]
            FlaskApp --> DocBP["Doctors Blueprint (/doctors)"]
            FlaskApp --> AppBP["Appointments Blueprint (/appointments)"]
            FlaskApp --> QueueBP["Live Queue Blueprint (/queue)"]
            FlaskApp --> RepBP["Analytics & Reports (/reports)"]
            FlaskApp --> HealthBP["Liveness & Readiness Probes (/health, /metrics)"]
            FlaskApp --> RestBP["JSON REST API (/api)"]
        end
        
        FlaskApp --> SQLiteDB[("SQLite Relational Database (caresync.db)")]
    end
    
    subgraph Persistent Storage
        SQLiteDB --- VolMount["Named Docker Volume: caresync_persistent_db (/app/data)"]
    end
```

---

## 3. Relational Database Schema Design

The SQLite database employs strict foreign key constraints, indexes, and transactions:

```mermaid
erDiagram
    USERS ||--o{ DOCTORS : "has profile"
    USERS ||--o{ APPOINTMENTS : "books"
    USERS ||--o{ ACTIVITY_LOGS : "logs"
    DOCTORS ||--o{ DOCTOR_AVAILABILITY : "defines hours"
    DOCTORS ||--o{ APPOINTMENTS : "conducts"
    APPOINTMENTS ||--o| QUEUE_ENTRIES : "generates token"

    USERS {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        string full_name
        string phone
        timestamp created_at
        int is_active
    }

    DOCTORS {
        int id PK
        int user_id FK, UK
        string doctor_code UK
        string specialty
        string qualification
        float consultation_fee
        string department
        int is_available
    }

    DOCTOR_AVAILABILITY {
        int id PK
        int doctor_id FK
        string day_of_week
        string start_time
        string end_time
        int slot_duration_mins
    }

    APPOINTMENTS {
        int id PK
        string appointment_code UK
        int patient_id FK
        int doctor_id FK
        string appointment_date
        string time_slot
        string reason
        string status
        string notes
        timestamp created_at
    }

    QUEUE_ENTRIES {
        int id PK
        int appointment_id FK, UK
        int queue_number
        string queue_date
        int doctor_id FK
        string status
        timestamp check_in_time
        timestamp called_time
        timestamp completed_time
    }

    ACTIVITY_LOGS {
        int id PK
        int user_id FK
        string action
        string details
        string ip_address
        timestamp timestamp
    }
```

---

## 4. End-to-End DevOps Pipeline Architecture

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer
    participant Git as GitHub Repository
    participant Jenkins as Jenkins CI/CD Server
    participant Pytest as Pytest Test Runner
    participant Docker as Docker Engine
    participant Compose as Docker Compose / Nginx
    participant App as CareSync App

    Dev->>Git: git push origin develop
    Git->>Jenkins: GitHub Webhook (POST /github-webhook/)
    Jenkins->>Jenkins: Stage 1: Checkout SCM
    Jenkins->>Jenkins: Stage 2: Verify Environment
    Jenkins->>Jenkins: Stage 3: Install Dependencies (.venv)
    Jenkins->>Jenkins: Stage 4: Validate Code (py_compile)
    Jenkins->>Pytest: Stage 5: Run Automated Tests
    Pytest-->>Jenkins: 30 Passed Tests (junit.xml)
    Jenkins->>Jenkins: Stage 6: Publish JUnit Reports
    Jenkins->>Docker: Stage 7: Build Docker Image (caresync-app:latest)
    Jenkins->>Compose: Stage 8: Deploy Containers with Persistent Storage
    Compose->>App: Start Gunicorn on port 5000 & Nginx on 8080
    Jenkins->>App: Stage 9: Query /health & /health/ready
    App-->>Jenkins: HTTP 200 OK (Deployment Verified)
```

---

## 5. Security & Authentication Architecture

1. **Password Hashing**: Passwords hashed using Werkzeug's `scrypt` algorithm with unique salt per user. Plaintext passwords are never stored.
2. **Role-Based Access Control (RBAC)**: Route decorators (`@login_required`, `@role_required`) enforce authorization before view functions execute. Patients cannot access administrative logs or other patients' appointments.
3. **Double Booking Guard**: The database and model layer enforce unique constraints on active appointments for `(doctor_id, appointment_date, time_slot)` preventing race conditions.
4. **Least-Privilege Docker Containers**: Containers run under the unprivileged `caresync` non-root system user.
