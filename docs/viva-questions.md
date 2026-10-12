# CareSync — DevOps Laboratory Viva Preparation Guide
## Course: 23IT723 — DevOps Laboratory

This guide contains concise, clear, and accurate answers to the most frequently asked questions during DevOps laboratory viva examinations.

---

### Q1: What is CareSync?
**Answer:**  
CareSync is a full-stack Hospital Appointment Management System built with Python Flask, SQLite, and Bootstrap 5, integrated with an end-to-end DevOps automation pipeline. It allows patients to book consultations, doctors to manage clinical schedules, and receptionists to monitor live patient queues, with automated CI/CD via Jenkins, containerization via Docker, and configuration management via Ansible.

---

### Q2: Why is Python Flask used for the backend?
**Answer:**  
Flask is a lightweight, modular WSGI micro-framework. It provides essential web routing, templating, and request handling without forcing heavy ORM overhead. It allows clean separation of concerns using Blueprints (`auth`, `doctors`, `appointments`, `queue`, `health`, `api`) and makes unit testing straightforward with Pytest.

---

### Q3: What is Git, and why do we use branches?
**Answer:**  
Git is a distributed Version Control System (VCS) that records changes to source code over time. We use **branches** (`main`, `develop`, `feature/*`) to isolate development work. Branching allows multiple developers to build new features simultaneously without destabilizing the production code on the `main` branch.

---

### Q4: What is the difference between `git fetch` and `git pull`?
**Answer:**  
- **`git fetch`**: Downloads commits, files, and branch refs from the remote repository without modifying your local working branch. It is safe and non-destructive.
- **`git pull`**: Performs a `git fetch` immediately followed by `git merge`. It directly integrates remote changes into your active local working directory.

---

### Q5: What is Jenkins?
**Answer:**  
Jenkins is an open-source automation server written in Java. It acts as the central orchestrator for Continuous Integration (CI) and Continuous Deployment (CD), automating tasks such as pulling code from GitHub, running test suites, compiling images, and triggering deployments.

---

### Q6: What is a CI/CD Pipeline?
**Answer:**  
A CI/CD Pipeline is an automated series of sequential steps that code passes through on its path from commit to production:
- **Continuous Integration (CI)**: Automatically integrates code changes from multiple contributors, installs dependencies, and runs automated tests on every push.
- **Continuous Deployment (CD)**: Automatically deploys tested, passing code into staging or production environments.

---

### Q7: What is a Webhook?
**Answer:**  
A webhook is an event-driven HTTP POST callback. Instead of Jenkins constantly polling GitHub to ask if new commits exist, GitHub pushes an HTTP request to the Jenkins URL (`/github-webhook/`) the instant a developer pushes code, triggering immediate automated builds.

---

### Q8: What is Docker?
**Answer:**  
Docker is an open-source platform that uses OS-level virtualization to package an application and all its dependencies into standardized, lightweight units called containers. This eliminates the *"it works on my machine"* problem across development, testing, and production.

---

### Q9: What is the difference between a Docker Image and a Docker Container?
**Answer:**  
- **Docker Image**: An immutable, read-only template built from a `Dockerfile` containing the application code, runtime libraries, and environment configurations.
- **Docker Container**: A runnable, isolated instance of an image executing in user space, with a thin read-write container layer on top of the image layers.

---

### Q10: What is Port Mapping in Docker?
**Answer:**  
By default, container networks are isolated from the host. Port mapping (e.g. `-p 8080:80`) maps an external port on the host machine (`8080`) to an internal listening port inside the container (`80`) using host iptables NAT routing, allowing web browsers to reach containerized services.

---

### Q11: Why do we use persistent volumes for the SQLite database?
**Answer:**  
Docker container filesystems are ephemeral (stateless). When a container is stopped and deleted (`docker rm`), any data written inside it is lost. A persistent volume (`caresync_persistent_db`) maps a directory on the host to `/app/data` inside the container, preserving database records across container restarts and upgrades.

---

### Q12: What is Continuous Testing?
**Answer:**  
Continuous Testing is the practice of executing automated test cases (such as Pytest unit tests, conflict validations, and integration tests) as part of the software delivery pipeline. In CareSync, if any of the 30 tests fail, the pipeline halts immediately, preventing defective builds from reaching deployment.

---

### Q13: What is Ansible?
**Answer:**  
Ansible is an open-source, agentless configuration management and automation tool. It executes human-readable YAML playbooks over SSH to provision software, manage configurations, and deploy applications across target servers.

---

### Q14: What is an Idempotent Playbook in Ansible?
**Answer:**  
Idempotence means that applying an operation once produces the desired state, and applying it multiple times subsequently produces the exact same outcome without causing unintended side effects. If Nginx is already installed and configured, Ansible leaves it unchanged (`changed=0`), avoiding service disruption.

---

### Q15: Why is Nginx used as a reverse proxy?
**Answer:**  
While WSGI servers like Gunicorn run Python applications, Nginx sits in front as an edge reverse proxy to:
- Buffer slow client connections.
- Handle SSL/TLS termination and HTTP header security.
- Compress responses using Gzip.
- Route requests and proxy `/health` checks.
- Prevent exposing internal application ports directly to public networks.

---

### Q16: How does the complete CareSync DevOps deployment workflow operate?
**Answer:**  
1. A developer commits code and pushes to GitHub.
2. GitHub Webhook notifies the Jenkins server.
3. Jenkins checks out the repository and verifies the environment.
4. Jenkins installs dependencies into a clean virtual environment.
5. Pytest runs the 30 automated test cases and publishes JUnit XML.
6. If tests pass, Jenkins builds the Docker container image.
7. Docker Compose / Ansible starts the containerized stack with persistent storage.
8. Nginx routes incoming browser traffic on port 8080 to the application.
9. An automated health check queries `/health` to verify that the service is live.

---

### Q17: What happens if an automated test fails?
**Answer:**  
If any test assertion fails in Stage 5:
- Pytest exits with a non-zero exit code.
- Jenkins marks Stage 5 as **FAILED**.
- All downstream stages (Docker Build, Deployment, Health Check) are immediately **ABORTED**.
- The build status changes to **RED (FAILED)**, and an alert is recorded. No broken code is deployed.

---

### Q18: How can the deployed CareSync application be verified?
**Answer:**  
Verification is performed through three levels:
1. **Liveness Probe**: Calling `GET /health` returns HTTP 200 with `{ "status": "healthy" }`.
2. **Readiness Probe**: Calling `GET /health/ready` executes a database test query (`SELECT 1`) to confirm SQLite connectivity.
3. **End-to-End Functional Check**: Logging into the web UI at `http://localhost:8080`, booking an appointment, verifying duplicate slot rejection, and confirming token appearance on the live queue monitor board.
