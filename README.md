# CareSync — Hospital Appointment Management System
### Automated CI/CD Deployment & DevOps Automation
**College Project for Course: 23IT723 — DevOps Laboratory**

---

## 📌 Project Overview

**CareSync** is a production-grade, full-stack Hospital Appointment Management System paired with a complete, automated DevOps CI/CD pipeline. The platform solves real-world healthcare challenges by enabling patients to book appointments with specialists, doctors to manage clinical consultations, receptionists to manage patient queues, and administrators to monitor hospital metrics.

Every phase of the project demonstrates the **13 experiments** outlined in the **23IT723 DevOps Laboratory** course curriculum:
- **Version Control**: Git branching, synchronization (`fetch`/`pull`), and conflict resolution.
- **Continuous Integration**: Jenkins Freestyle jobs and a 9-stage Declarative Pipeline (`Jenkinsfile`).
- **Automated Testing**: 30 automated Pytest test cases generating standardized JUnit XML reports.
- **Event-Driven Automation**: Push-triggered builds via GitHub Webhooks.
- **Containerization**: Production Dockerfiles, Alpine vs. Debian image comparisons, and Docker Compose orchestration.
- **Configuration Management**: Idempotent Ansible playbooks for Nginx web server provisioning and Docker management.
- **Reverse Proxy**: Nginx routing, client body limits, and operational `/health` probes.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+ / Flask 3.1 | Modular architecture using Flask Blueprints |
| **Database** | SQLite 3 | Relational database with foreign keys, indexes, and transactions |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 | Modern medical dashboard, live queue board, responsive design |
| **Automated Testing**| Pytest 8.x | 30 test cases covering auth, conflicts, queue, and API |
| **Version Control** | Git & GitHub | GitFlow model (`main`, `develop`, `feature/*`, `bugfix/*`) |
| **CI/CD Automation** | Jenkins | Freestyle projects & 9-stage Declarative `Jenkinsfile` |
| **Containerization** | Docker & Docker Compose | Multi-container stack with persistent volume storage |
| **Web Server / Proxy**| Nginx 1.25+ (Alpine) | Reverse proxy on port 8080 routing to Gunicorn |
| **Config Management**| Ansible 2.15+ (WSL2/Linux) | Idempotent playbooks for Nginx and container lifecycle |

---

## 🚀 Quick Start Guide (Windows Laptop)

### 1. Running Locally with Python Virtual Environment
```powershell
# 1. Clone repository (or open workspace directory)
cd "c:\Users\lenovo\OneDrive\Desktop\Devops cat2"

# 2. Run the automated Windows launcher:
.\scripts\run_app.bat

# Or execute manually:
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts\seed_data.py
python app.py
```
Open your browser at: **`http://localhost:5000`**

### 2. Running Automated Tests with JUnit XML Report
```powershell
.\scripts\run_tests.bat
# Or:
.\.venv\Scripts\pytest -v --junitxml=reports/junit.xml
```
*Result: All 30 tests pass and create `reports/junit.xml` for Jenkins!*

### 3. Running Containerized Stack with Docker Compose
```bash
docker compose up -d --build
```
Access the application through the Nginx reverse proxy at: **`http://localhost:8080`**

---

## 🔑 Default Credentials for Viva & Demonstration

The database is pre-seeded with sample medical staff, patients, schedules, and queue tokens:

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Hospital statistics, doctor management, audit logs |
| **Doctor (Cardiology)** | `dr.sarah` | `doctor123` | Clinical workspace, patient consultations, queue calls |
| **Doctor (Neurology)** | `dr.david` | `doctor123` | Assigned patients, timetable updates |
| **Patient** | `john_doe` | `patient123` | Appointment booking, token receipt, visit history |
| **Patient** | `jane_smith` | `patient123` | Scheduled appointments, profile management |

*(Quick demo buttons are also present on the login screen to automatically fill credentials in one click during lab evaluation!)*

---

## 📁 Repository Structure

```
caresync-devops/
├── app/                      # Application Package
│   ├── __init__.py           # Flask application factory & blueprint registry
│   ├── db.py                 # SQLite connection management & schema definition
│   ├── models.py             # Data access models, validations & queue logic
│   ├── routes/               # Modular Flask Blueprints
│   │   ├── auth.py           # Login, registration, session, RBAC decorators
│   │   ├── dashboard.py      # Admin, Doctor, and Patient custom dashboards
│   │   ├── doctors.py        # Doctor directory, administration & schedules
│   │   ├── appointments.py   # Booking flow, conflict checks & cancellations
│   │   ├── queue.py          # Patient check-in, token generator, live board
│   │   ├── reports.py        # Date-filtered analytics & doctor workloads
│   │   ├── health.py         # /health, /health/ready, and /metrics probes
│   │   └── api.py            # Machine-readable JSON REST API endpoints
│   ├── static/
│   │   ├── css/style.css     # Medical theme, custom cards & animations
│   │   └── js/
│   │       ├── main.js       # Dynamic slot picker, mobile nav, confirmation
│   │       └── queue.js      # Automatic live queue background polling
│   └── templates/            # Responsive Jinja2 HTML templates
│       ├── base.html         # Sidebar, top navbar, flash alert banners
│       ├── auth/             # Login, register, profile
│       ├── dashboard/        # Role-tailored dashboards
│       ├── doctors/          # Doctor catalog & management
│       ├── appointments/     # Booking interface & receipt cards
│       ├── queue/            # Public waiting display & reception desk
│       ├── reports/          # Workload analytics
│       └── errors/           # Custom 403, 404, 500 error pages
├── tests/                    # Automated Pytest Suite (30 Test Cases)
│   ├── conftest.py           # Isolated test database fixtures & auth helpers
│   ├── test_app.py           # App startup & custom 404 tests
│   ├── test_auth.py          # Registration, login, and RBAC security tests
│   ├── test_doctors.py       # Doctor management & timetable slot calculation
│   ├── test_appointments.py  # Booking, duplicate prevention & cancellations
│   ├── test_queue.py         # Sequential token generation & progression
│   ├── test_health_and_api.py# Health probes & REST API authorization tests
│   └── test_database_persistence.py # SQLite connection persistence tests
├── scripts/                  # Management Scripts
│   ├── init_db.py            # Database schema creator
│   ├── seed_data.py          # Seeds sample medical staff & demo records
│   ├── reset_db.py           # Clean development database reset
│   ├── run_app.bat           # Windows development server launcher
│   └── run_tests.bat         # Automated test runner with JUnit XML output
├── reports/                  # Automated CI/CD Reports
│   └── junit.xml             # Generated JUnit XML report for Jenkins
├── docker/                   # Docker Artifacts
│   ├── Dockerfile.alpine     # Alpine Linux base for Experiment 8 comparison
│   └── docker-entrypoint.sh  # Auto-seeds volume on container startup
├── nginx/                    # Reverse Proxy Configuration
│   └── default.conf          # Nginx virtual host, headers & health proxy
├── ansible/                  # Configuration Management (Experiments 11 & 12)
│   ├── inventory.ini.example # Managed hosts inventory
│   ├── playbook.yml          # Idempotent Nginx & Gunicorn web server playbook
│   ├── deploy-docker.yml     # Automated Docker container management playbook
│   ├── templates/            # Jinja2 templates (nginx.conf.j2, caresync.service.j2)
│   └── README.md             # WSL2 prerequisites & execution instructions
├── docs/                     # Laboratory Documentation
│   ├── lab-experiments.md    # ALL 13 experiments with aims, steps, viva explanations
│   ├── viva-questions.md     # 18+ high-yield viva questions with concise answers
│   ├── architecture.md       # Architectural diagrams & database ER specifications
│   ├── git-workflow.md       # Branching model & conflict resolution guide
│   ├── jenkins-setup.md      # Freestyle & Pipeline configuration guide
│   ├── webhook-setup.md      # GitHub Webhook setup with localtunnel guide
│   ├── docker-setup.md       # Docker lifecycle commands & port mapping guide
│   └── ansible-setup.md      # Ansible playbooks and idempotence concepts
├── Dockerfile                # Production Debian Slim Dockerfile
├── compose.yaml              # Docker Compose multi-service definition
├── Jenkinsfile               # 9-Stage Declarative CI/CD Pipeline
├── pytest.ini                # Pytest configuration
├── requirements.txt          # Pinned project dependencies
├── .dockerignore             # Docker build exclusions
├── .gitignore                # Git exclusions
└── README.md                 # This master documentation file
```

---

## 📚 Laboratory Experiments Documentation

Complete instructions, commands, expected results, and verification steps for all 13 experiments can be found in:

👉 **[docs/lab-experiments.md](docs/lab-experiments.md)**

| # | Experiment Title | Documentation Link |
| :-: | :--- | :--- |
| **1** | Git Local and Remote Repositories | [Experiment 1](docs/lab-experiments.md#experiment-1-git-local-and-remote-repositories) |
| **2** | Git Fetch and Synchronization | [Experiment 2](docs/lab-experiments.md#experiment-2-git-fetch-and-synchronization) |
| **3** | Branching, Merging, and Conflict Resolution | [Experiment 3](docs/lab-experiments.md#experiment-3-branching-merging-and-conflict-resolution) |
| **4** | Jenkins Freestyle Job with GitHub | [Experiment 4](docs/lab-experiments.md#experiment-4-jenkins-freestyle-job-with-github) |
| **5** | Jenkins CI/CD Pipeline | [Experiment 5](docs/lab-experiments.md#experiment-5-jenkins-cicd-pipeline) |
| **6** | GitHub Webhook Integration | [Experiment 6](docs/lab-experiments.md#experiment-6-github-webhook-integration) |
| **7** | Docker Image and Container Lifecycle | [Experiment 7](docs/lab-experiments.md#experiment-7-docker-image-and-container-lifecycle) |
| **8** | Dockerfiles and OS Image Comparison | [Experiment 8](docs/lab-experiments.md#experiment-8-dockerfiles-and-operating-system-image-comparison) |
| **9** | Docker Deployment, Port Mapping & Volumes | [Experiment 9](docs/lab-experiments.md#experiment-9-docker-deployment-port-mapping-and-volume-mounting) |
| **10**| Continuous Testing and Test Reports | [Experiment 10](docs/lab-experiments.md#experiment-10-continuous-testing-and-test-reports) |
| **11**| Ansible Web-Server Configuration | [Experiment 11](docs/lab-experiments.md#experiment-11-ansible-web-server-configuration) |
| **12**| Automated Container Management using Ansible| [Experiment 12](docs/lab-experiments.md#experiment-12-automated-docker-container-management-using-ansible) |
| **13**| Integrated DevOps Mini-Project | [Experiment 13](docs/lab-experiments.md#experiment-13-integrated-devops-mini-project) |

---

## 🎓 Viva Examination Preparation

Prepare for viva questions and project presentation using:

👉 **[docs/viva-questions.md](docs/viva-questions.md)**

---

## 🔒 Verification & Health Check Endpoints

CareSync includes dedicated health endpoints used by Docker healthchecks, Jenkins pipeline stages, and monitoring services:
- **`GET /health`**: Liveness probe returning `{ "status": "healthy", "version": "1.0.0" }`.
- **`GET /health/ready`**: Readiness probe executing test queries against SQLite (`SELECT 1`).
- **`GET /metrics`**: Operational metrics returning system uptime and counts.
- **`GET /api/doctors`**: RESTful doctor catalog JSON endpoint.
- **`GET /queue/api/live`**: Real-time waiting-room queue JSON feed.
