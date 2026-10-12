# 23IT723 — DevOps Laboratory Course Plan
## Comprehensive Lab Experiments Manual: CareSync System

This document contains step-by-step procedures, commands, verification criteria, troubleshooting guides, and viva explanations for **all 13 experiments** in the **23IT723 DevOps Laboratory** course curriculum.

---

# Table of Contents
1. [Experiment 1: Git Local and Remote Repositories](#experiment-1-git-local-and-remote-repositories)
2. [Experiment 2: Git Fetch and Synchronization](#experiment-2-git-fetch-and-synchronization)
3. [Experiment 3: Branching, Merging, and Conflict Resolution](#experiment-3-branching-merging-and-conflict-resolution)
4. [Experiment 4: Jenkins Freestyle Job with GitHub](#experiment-4-jenkins-freestyle-job-with-github)
5. [Experiment 5: Jenkins CI/CD Pipeline](#experiment-5-jenkins-cicd-pipeline)
6. [Experiment 6: GitHub Webhook Integration](#experiment-6-github-webhook-integration)
7. [Experiment 7: Docker Image and Container Lifecycle](#experiment-7-docker-image-and-container-lifecycle)
8. [Experiment 8: Dockerfiles and Operating-System Image Comparison](#experiment-8-dockerfiles-and-operating-system-image-comparison)
9. [Experiment 9: Docker Deployment, Port Mapping, and Volume Mounting](#experiment-9-docker-deployment-port-mapping-and-volume-mounting)
10. [Experiment 10: Continuous Testing and Test Reports](#experiment-10-continuous-testing-and-test-reports)
11. [Experiment 11: Ansible Web-Server Configuration](#experiment-11-ansible-web-server-configuration)
12. [Experiment 12: Automated Docker Container Management using Ansible](#experiment-12-automated-docker-container-management-using-ansible)
13. [Experiment 13: Integrated DevOps Mini-Project](#experiment-13-integrated-devops-mini-project)

---

## Experiment 1: Git Local and Remote Repositories

### 1. Aim
To initialize a local Git repository for the CareSync Hospital Management System, configure user credentials, track project files, create commits, link to a remote GitHub repository, and push code to the remote server.

### 2. Tools Required
- Git CLI (Version 2.x+)
- GitHub Account
- Windows PowerShell / Bash

### 3. Files Involved
- `.gitignore`
- `README.md`
- Application source files (`app/`, `tests/`, `scripts/`)

### 4. Commands to Execute

#### On Windows PowerShell / Linux:
```bash
# 1. Initialize local repository
git init

# 2. Configure user name and email
git config user.name "Student Developer"
git config user.email "student@caresync.local"

# 3. Check tracking status
git status

# 4. Stage all project files
git add .

# 5. Commit staged files
git commit -m "feat: initial commit for CareSync hospital system"

# 6. Set primary branch name to main
git branch -M main

# 7. Add remote repository URL (replace with your repository)
git remote add origin https://github.com/<your-username>/caresync-devops.git

# 8. Push to GitHub
git push -u origin main
```

### 5. Expected Result
The repository is initialized locally, all project files are committed under the `main` branch, and the remote GitHub repository mirrors the local repository.

### 6. How to Verify
- Run `git log -1` to inspect the latest commit ID, author, and timestamp.
- Run `git remote -v` to confirm the fetch and push remote URLs.
- Open your GitHub repository in the web browser to verify that files are visible.

### 7. Common Errors & Troubleshooting
- **Error: `fatal: remote origin already exists`**:
  *Fix*: Run `git remote remove origin` and then run `git remote add origin <url>`.
- **Error: `Support for password authentication was removed`**:
  *Fix*: Use a GitHub Personal Access Token (PAT) with `repo` scope instead of your account password.

### 8. Viva Explanation
*"Git is a distributed version control system that tracks file modifications over time. In this experiment, we initialized a repository with `git init`, tracked code changes across commits, and synchronized local snapshots with a central GitHub remote repository."*

---

## Experiment 2: Git Fetch and Synchronization

### 1. Aim
To demonstrate the difference between `git fetch` and `git pull`, inspect remote branch changes without modifying working files, and safely synchronize the local workspace with remote updates.

### 2. Tools Required
- Git CLI, GitHub remote repository

### 3. Files Involved
- Any project files updated on the remote repository.

### 4. Commands to Execute
```bash
# 1. Download latest references from remote without merging
git fetch origin

# 2. Inspect commits present on remote main but absent locally
git log HEAD..origin/main --oneline

# 3. Compare file diffs between local and fetched remote
git diff HEAD origin/main

# 4. Safely merge remote updates into local branch
git merge origin/main

# 5. Alternatively, combine fetch and merge in a single command
git pull origin main
```

### 5. Expected Result
`git fetch` updates `.git/FETCH_HEAD` and remote-tracking branches (`origin/main`) without altering the local working tree, giving the developer an opportunity to inspect incoming changes before merging.

### 6. How to Verify
- Run `git status` after `git fetch`: Git will report: `"Your branch is behind 'origin/main' by N commits, and can be fast-forwarded."`
- Run `git status` after `git merge`: Git will report: `"Your branch is up to date with 'origin/main'."`

### 7. Common Errors & Troubleshooting
- **Error: `Your local changes to the following files would be overwritten by merge`**:
  *Fix*: Stash your uncommitted changes (`git stash`), execute `git pull`, then re-apply (`git stash pop`).

### 8. Viva Explanation
*"While `git pull` blindly fetches and merges changes in one step, `git fetch` safely downloads remote refs without touching working files. This allows developers to review code diffs before merging into production."*

---

## Experiment 3: Branching, Merging, and Conflict Resolution

### 1. Aim
To implement a standard Git branching strategy (`main`, `develop`, `feature/*`), create and merge feature branches, intentionally trigger a merge conflict, and resolve it systematically.

### 2. Tools Required
- Git CLI

### 3. Files Involved
- `app/models.py` or a demo conflict file (`conflict_demo.txt`)

### 4. Commands to Execute
```bash
# 1. Create and switch to develop branch
git checkout -b develop

# 2. Create feature branch
git checkout -b feature/appointment-notes

# 3. Make changes, stage and commit
git commit -am "feat: add notes support"

# 4. Switch back to develop and merge
git checkout develop
git merge --no-ff feature/appointment-notes -m "merge: incorporate feature/appointment-notes into develop"

# 5. Conflict Simulation: Create two divergent branches modifying same line
git checkout -b branch-a
echo "Emergency Contact: +1-800-DOCTORS" > hotline.txt
git add hotline.txt && git commit -m "update hotline to doctors"

git checkout develop
git checkout -b branch-b
echo "Emergency Contact: +1-800-AMBULANCE" > hotline.txt
git add hotline.txt && git commit -m "update hotline to ambulance"

# 6. Merge branch-a (clean)
git checkout develop
git merge branch-a

# 7. Merge branch-b (triggers CONFLICT)
git merge branch-b
```

#### Resolving the Conflict:
Open `hotline.txt` and inspect conflict markers:
```text
<<<<<<< HEAD
Emergency Contact: +1-800-DOCTORS
=======
Emergency Contact: +1-800-AMBULANCE
>>>>>>> branch-b
```
Edit the file to the resolved combined text:
```text
Emergency Contact: +1-800-DOCTORS / Ambulance: +1-800-AMBULANCE
```
Finalize resolution:
```bash
git add hotline.txt
git commit -m "fix(merge): resolve emergency contact conflict"
```

### 5. Expected Result
Both feature branches merge cleanly; the simulated conflict halts automated merging, marks conflicting lines with markers (`<<<<<<<`, `=======`, `>>>>>>>`), and resolves cleanly upon manual resolution and commit.

### 6. How to Verify
- Run `git log --graph --oneline --all` to view the visual branch merge graph.
- Run `git status` to ensure working tree is clean.

### 7. Viva Explanation
*"Branching isolates changes so multiple developers can work simultaneously without breaking the main codebase. A merge conflict occurs when two branches edit the exact same lines of code. Git pauses the merge, inserts conflict markers, and requires a human developer to decide which version to retain."*

---

## Experiment 4: Jenkins Freestyle Job with GitHub

### 1. Aim
To configure a Jenkins Freestyle project that connects to the CareSync GitHub repository, pulls the source code on demand, installs Python dependencies, runs the Pytest test suite, and reports build success or failure.

### 2. Tools Required
- Jenkins Server (v2.400+)
- Git Plugin, Python 3.x

### 3. Files Involved
- `requirements.txt`
- `tests/`
- `scripts/run_tests.bat` (Windows) or shell commands

### 4. Step-by-Step Configuration
1. Open Jenkins at `http://localhost:8080`.
2. Click **New Item** -> Name: `CareSync-Freestyle-CI` -> Select **Freestyle project** -> Click **OK**.
3. Under **Source Code Management**:
   - Select **Git**.
   - Set **Repository URL**: `https://github.com/<your-username>/caresync-devops.git`.
   - Branch Specifier: `*/main` or `*/develop`.
4. Under **Build Steps**:
   - On Windows: Add **Execute Windows batch command**:
     ```bat
     cd /d "%WORKSPACE%"
     if not exist ".venv" ( python -m venv .venv )
     call .venv\Scripts\activate.bat
     pip install -r requirements.txt
     if not exist "reports" ( mkdir reports )
     pytest -v --junitxml=reports/junit.xml
     ```
5. Under **Post-build Actions**:
   - Add **Publish JUnit test result report**: `reports/junit.xml`.
6. Click **Save** and click **Build Now**.

### 5. Expected Result
Jenkins checks out the code into `%WORKSPACE%`, executes the test suite, records 30 passing tests, and flags the build with a blue/green circle (**SUCCESS**).

### 6. How to Verify
- Check **Console Output** for exit code `0`.
- Check **Test Result Trend** graph in the job overview.

### 7. Viva Explanation
*"A Freestyle job is a configurable build task in Jenkins that provides a simple web UI for executing sequential steps (checkout, build, test, archive) without writing pipeline-as-code scripts."*

---

## Experiment 5: Jenkins CI/CD Pipeline

### 1. Aim
To create and execute an automated 9-stage Declarative Pipeline (`Jenkinsfile`) implementing checkout, environment verification, dependency installation, syntax checks, testing, report publication, container build, deployment, and health verification.

### 2. Tools Required
- Jenkins Pipeline Plugin, Git, Python 3.x, Docker

### 3. Files Involved
- `Jenkinsfile`
- `pytest.ini`
- `reports/junit.xml`

### 4. Pipeline Stages Implemented
1. `Checkout`: Checks out branch from Git.
2. `Environment Verification`: Verifies CLI tools (Python, Git, Docker).
3. `Dependency Installation`: Sets up `.venv` and installs `requirements.txt`.
4. `Application Validation`: Performs syntax validation with `py_compile`.
5. `Automated Tests`: Executes Pytest test suite.
6. `Test Report Publication`: Publishes `reports/junit.xml` to Jenkins UI.
7. `Docker Image Build`: Builds container image `caresync-app:${BUILD_NUMBER}`.
8. `Deployment`: Deploys conditionally on `main` or `develop` branches.
9. `Health Verification`: Queries `/health` and `/health/ready` to verify liveness.

### 5. How to Configure
1. Jenkins Dashboard -> **New Item** -> Name: `CareSync-Pipeline-CD` -> Select **Pipeline**.
2. Set **Definition**: `Pipeline script from SCM` -> SCM: `Git` -> Script Path: `Jenkinsfile`.
3. Click **Save** and **Build Now**.

### 6. Expected Result
The Jenkins Pipeline Stage View displays all 9 stages in sequential green blocks, with stage durations and test result counts.

### 7. How to Verify
- Click the build number -> **Stage View** -> verify all 9 stages passed.
- Click **Test Result** to review passing unit tests.

### 8. Viva Explanation
*"Pipeline-as-code stores the entire build, test, and release workflow in a version-controlled `Jenkinsfile`. This ensures repeatable, auditable deployments and allows team members to track CI/CD changes alongside application code."*

---

## Experiment 6: GitHub Webhook Integration

### 1. Aim
To configure a GitHub Webhook that automatically notifies Jenkins on every `git push` event, triggering immediate automated builds without manual intervention.

### 2. Tools Required
- GitHub Repository, Jenkins Server, Localtunnel / Ngrok (for local Windows setup)

### 3. Files Involved
- `Jenkinsfile`
- GitHub Webhook configuration

### 4. Configuration Steps

#### Step 1: Expose Local Jenkins via Tunnel (Windows)
```powershell
npx localtunnel --port 8080
# Output: https://my-caresync-lab.loca.lt
```

#### Step 2: Configure Webhook in GitHub
1. Open GitHub repository -> **Settings** -> **Webhooks** -> **Add webhook**.
2. **Payload URL**: `https://my-caresync-lab.loca.lt/github-webhook/`
3. **Content type**: `application/json`.
4. **Events**: `Just the push event`.
5. Click **Add webhook**.

#### Step 3: Enable Trigger in Jenkins
1. Open your Jenkins job -> **Configure**.
2. Check **GitHub hook trigger for GITScm polling**.
3. Click **Save**.

### 5. Expected Result
Pushing any commit to GitHub results in an immediate HTTP POST to `/github-webhook/`, triggering a new build automatically in Jenkins within seconds.

### 6. How to Verify
- Push a commit: `git commit -am "test webhook" && git push origin develop`.
- Observe GitHub **Settings -> Webhooks -> Recent Deliveries** showing HTTP `200 OK`.
- Observe Jenkins build queue starting build `#N` with message *"Started by GitHub push"*.

### 7. Viva Explanation
*"A webhook is an event-driven HTTP POST callback. Instead of wasteful polling, GitHub immediately notifies Jenkins when a push event occurs, enabling real-time continuous integration."*

---

## Experiment 7: Docker Image and Container Lifecycle

### 1. Aim
To master Docker container lifecycle commands including image pulling, building, running, inspecting, streaming logs, stopping, starting, and removing containers.

### 2. Tools Required
- Docker Engine / Docker Desktop, CLI

### 3. Files Involved
- `Dockerfile`

### 4. Commands to Execute
```bash
# 1. Pull base image
docker pull python:3.11-slim

# 2. Build CareSync image
docker build -t caresync:1.0 .

# 3. View images
docker images

# 4. Run detached container with port mapping
docker run -d -p 5000:5000 --name caresync-app caresync:1.0

# 5. Check active containers
docker ps

# 6. Stream application logs
docker logs -f caresync-app

# 7. Inspect container metadata and health
docker inspect caresync-app

# 8. Execute commands inside container
docker exec -it caresync-app curl http://localhost:5000/health

# 9. Stop, start, and restart container
docker stop caresync-app
docker start caresync-app
docker restart caresync-app

# 10. Clean up container and image
docker stop caresync-app
docker rm caresync-app
docker rmi caresync:1.0
```

### 5. Expected Result
Container transitions through states: *Created -> Running -> Paused/Stopped -> Removed*.

### 6. How to Verify
- `docker ps -a` confirms status changes (e.g., `Up 2 minutes (healthy)` vs `Exited (0)`).

### 7. Viva Explanation
*"A Docker image is an immutable template containing application code, runtime, and libraries. A container is a runnable, isolated instance of that image executing in user space with kernel namespaces and cgroups."*

---

## Experiment 8: Dockerfiles and Operating-System Image Comparison

### 1. Aim
To build CareSync using two distinct base operating system images (`Debian Slim` vs `Alpine Linux`), analyze package manager differences (`apt` vs `apk`), and compare layer sizes.

### 2. Tools Required
- Docker CLI

### 3. Files Involved
- `Dockerfile` (Debian Slim base: `python:3.11-slim`)
- `docker/Dockerfile.alpine` (Alpine Linux base: `python:3.11-alpine`)

### 4. Commands to Execute
```bash
# 1. Build Debian Slim variant
docker build -t caresync:debian -f Dockerfile .

# 2. Build Alpine Linux variant
docker build -t caresync:alpine -f docker/Dockerfile.alpine .

# 3. Compare virtual image sizes
docker images | grep caresync
```

### 5. Expected Result & Comparison
- `caresync:debian`: ~160 MB (Uses `glibc`, Debian `apt`, highly compatible with pre-built binary wheels).
- `caresync:alpine`: ~75 MB (Uses `musl libc`, Alpine `apk`, ultra-lightweight, 50% smaller footprint).

### 6. How to Verify
Check output of `docker images` comparing virtual size columns.

### 7. Viva Explanation
*"Alpine Linux uses musl libc and BusyBox to achieve an extremely minimal footprint (~5MB base), whereas Debian Slim uses glibc (~120MB base). While Alpine produces smaller image sizes, Debian Slim provides broader binary compatibility with Python C-extensions."*

---

## Experiment 9: Docker Deployment, Port Mapping, and Volume Mounting

### 1. Aim
To orchestrate multi-container deployment using Docker Compose, implement host-to-container port mapping (`8080:80`), mount persistent storage for the SQLite database, and verify data persistence across container restarts.

### 2. Tools Required
- Docker Compose, Web Browser

### 3. Files Involved
- `compose.yaml`
- `nginx/default.conf`
- `Dockerfile`

### 4. Commands to Execute
```bash
# 1. Start all services in background
docker compose up -d --build

# 2. Check running services and health status
docker compose ps

# 3. Access web application in browser
curl http://localhost:8080/health

# 4. Verify volume persistence
# Book an appointment, then destroy containers:
docker compose down
# Recreate containers:
docker compose up -d
# Verify that the appointment is still present!

# 5. Teardown
docker compose down
```

### 5. Expected Result
Nginx routes host port 8080 traffic to internal `caresync-app:5000`. The named volume `caresync_persistent_db` keeps the SQLite database safe even when containers are deleted and recreated.

### 6. How to Verify
- Access `http://localhost:8080` in browser.
- Run `docker volume ls` to verify `caresync_persistent_db` exists.

### 7. Viva Explanation
*"Port mapping translates host network ports to container internal ports using iptables NAT. Named volumes map a storage directory on the host to the container filesystem, ensuring database state persists beyond container lifecycles."*

---

## Experiment 10: Continuous Testing and Test Reports

### 1. Aim
To implement an automated test suite with Pytest covering health checks, authentication, appointment conflicts, and queue numbering, and generate standardized JUnit XML reports for Jenkins CI integration.

### 2. Tools Required
- Pytest, Python 3.x, Jenkins JUnit Plugin

### 3. Files Involved
- `tests/conftest.py`, `tests/test_*.py`
- `pytest.ini`
- `reports/junit.xml`

### 4. Commands to Execute
```bash
# 1. Run tests with verbose output
pytest -v

# 2. Generate machine-readable JUnit XML report
pytest -v --junitxml=reports/junit.xml

# 3. On Windows via batch runner:
.\scripts\run_tests.bat
```

### 5. Expected Result
All 30 automated test cases pass with exit code `0`. A valid XML file `reports/junit.xml` is generated conforming to the JUnit schema.

### 6. How to Verify
- Open `reports/junit.xml` in an editor to confirm `<testsuites tests="30" failures="0">`.
- In Jenkins, view the **Test Result Trend** graph.

### 7. Viva Explanation
*"Continuous testing runs automated assertions on every build. JUnit XML is a standard reporting format parsed by CI/CD servers to visualize test history, detect flaky tests, and halt deployment upon failure."*

---

## Experiment 11: Ansible Web-Server Configuration

### 1. Aim
To automate Nginx web server installation, reverse proxy configuration from Jinja2 templates, service startup, and configuration validation on target Linux hosts using idempotent Ansible playbooks.

### 2. Tools Required
- Ansible (via WSL2 or Linux control node), SSH

### 3. Files Involved
- `ansible/inventory.ini.example`
- `ansible/playbook.yml`
- `ansible/templates/nginx.conf.j2`
- `ansible/templates/caresync.service.j2`

### 4. Commands to Execute (in WSL2 / Linux)
```bash
# 1. Check playbook syntax
ansible-playbook --syntax-check playbook.yml

# 2. Perform dry run check
ansible-playbook -i inventory.ini.example playbook.yml --check

# 3. Execute playbook against target hosts
ansible-playbook -i inventory.ini playbook.yml

# 4. Verify idempotence: run the playbook a second time!
ansible-playbook -i inventory.ini playbook.yml
```

### 5. Expected Result
First run completes with tasks marked `changed`. The second run reports `changed=0`, proving idempotence. Nginx is configured and reverse-proxies requests to the CareSync backend.

### 6. How to Verify
- Check Ansible summary: `changed=0, failed=0`.
- Run `curl http://localhost/health` returning `200 OK`.

### 7. Viva Explanation
*"Ansible is an agentless configuration management tool that uses YAML playbooks over SSH. Idempotence guarantees that applying a playbook multiple times produces the exact same system state without redundant changes or service disruptions."*

---

## Experiment 12: Automated Docker Container Management using Ansible

### 1. Aim
To automate Docker container lifecycles (bridge network creation, persistent volumes, container provisioning, health monitoring) using Ansible Docker modules (`community.docker`).

### 2. Tools Required
- Ansible, Docker Engine, Python `docker` SDK

### 3. Files Involved
- `ansible/deploy-docker.yml`
- `compose.yaml`

### 4. Commands to Execute (in WSL2 / Linux)
```bash
# 1. Install Docker Ansible collection
ansible-galaxy collection install community.docker

# 2. Syntax check
ansible-playbook --syntax-check deploy-docker.yml

# 3. Run container deployment playbook
ansible-playbook -i inventory.ini deploy-docker.yml
```

### 5. Expected Result
Ansible ensures network `caresync-network` and volume `caresync_persistent_db` exist, starts `caresync-app` and `caresync-nginx` containers, and verifies readiness via the `uri` module.

### 6. How to Verify
- Run `docker ps` to verify containers started via Ansible.
- Check Ansible task output showing successful health check assertion.

### 7. Viva Explanation
*"Combining Ansible with Docker provides declarative Infrastructure-as-Code for container orchestration, automating network setup, volume mapping, environment variables, and rolling updates across remote servers."*

---

## Experiment 13: Integrated DevOps Mini-Project

### 1. Aim
To execute the end-to-end integrated DevOps lifecycle: developer writes code -> commits and pushes to GitHub -> GitHub Webhook triggers Jenkins CI/CD -> Jenkins runs Pytest tests -> generates JUnit reports -> builds Docker image -> Ansible/Compose deploys containers -> Nginx serves traffic -> Health probe validates deployment.

### 2. Tools Required
- Git, GitHub, Jenkins, Docker, Nginx, Pytest, Ansible, Flask

### 3. End-to-End Workflow Diagram
```
Developer (VS Code / Antigravity)
       │ git commit & git push
       ▼
GitHub Repository (caresync-devops)
       │ Webhook (HTTP POST)
       ▼
Jenkins CI/CD Automation Server
  ├─ 1. Checkout SCM
  ├─ 2. Verify Environment
  ├─ 3. Install Dependencies (.venv)
  ├─ 4. Application Validation (py_compile)
  ├─ 5. Automated Tests (Pytest: 30 tests)
  ├─ 6. Publish Test Results (JUnit XML)
  ├─ 7. Build Docker Image (caresync-app:latest)
  ├─ 8. Deploy Containers (Docker Compose / Ansible)
  └─ 9. Health Verification (/health -> 200 OK)
       │
       ▼
Production Web Server (Nginx Reverse Proxy on Port 8080)
       │
       ▼
CareSync Healthcare Web Application (http://localhost:8080)
```

### 4. Step-by-Step Demonstration for Viva
1. **Show Source Code & Architecture**: Open `app/`, demonstrate database models and role-based access control.
2. **Execute Automated Tests Locally**: Run `pytest -v`, showing 30 passing tests.
3. **Trigger Pipeline via Git Push**: Push a commit, switch to Jenkins UI, watch webhook trigger the 9-stage pipeline automatically.
4. **Show JUnit Reports**: Open test trend graph in Jenkins showing zero failures.
5. **Show Docker Deployment**: Run `docker compose ps` to show both services healthy.
6. **Live Application Demo**:
   - Open `http://localhost:8080` in the browser.
   - Log in as Patient (`john_doe` / `patient123`) -> Book appointment.
   - Log in as Doctor (`dr.sarah` / `doctor123`) -> View consultation.
   - Show Live Queue Monitor (`/queue`) updating tokens in real-time!
   - Log in as Admin (`admin` / `admin123`) -> View hospital statistics and reports.
7. **Verify Operational Health Probe**: Open `http://localhost:8080/health` and `/metrics`.

### 5. Viva Explanation
*"This mini-project demonstrates a complete modern DevOps software delivery lifecycle. Code is validated automatically on every push, containerized into immutable images, deployed reproducibly, and monitored continuously, eliminating human deployment errors and achieving true CI/CD."*
