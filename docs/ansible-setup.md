# CareSync — Ansible Automation & Configuration Management

This document explains the Ansible automation architecture, playbook structure, idempotence, and lab procedures for **23IT723 DevOps Laboratory Experiments 11 & 12**.

---

## 1. Role of Ansible in CareSync DevOps Architecture

In the CareSync end-to-end DevOps pipeline:
1. **Jenkins** builds the application and verifies tests.
2. **Ansible** acts as the configuration management and deployment orchestrator:
   - Sets up infrastructure dependencies (Nginx, Python, Docker).
   - Manages service configurations through version-controlled templates.
   - Deploys or upgrades the CareSync application.
   - Restarts dependent services gracefully.
   - Performs automated post-deployment validation against `/health`.

---

## 2. Playbooks Overview

### Playbook 1: `ansible/playbook.yml` (Experiment 11)
Automates host-level web server provisioning:
- Installs `nginx`, `python3-venv`, and system dependencies via `apt`.
- Creates deployment directories with proper ownership (`www-data`).
- Deploys CareSync code and virtual environment.
- Provisions `systemd` service for Gunicorn.
- Deploys dynamic Nginx virtual host with proxy headers.
- Tests Nginx syntax with `nginx -t`.
- Uses handlers to restart/reload services only when files change.
- Queries `/health` with the `uri` module to ensure HTTP 200 OK.

### Playbook 2: `ansible/deploy-docker.yml` (Experiment 12)
Automates container management:
- Creates dedicated bridge network `caresync-network`.
- Provisions persistent volume `caresync_persistent_db`.
- Deploys `caresync-app` container with volume mount and health check.
- Deploys `caresync-nginx` reverse proxy container mapping port 8080 to 80.
- Asserts that containers reach `healthy` state.

---

## 3. Key Ansible Concepts to Explain in Viva

- **Control Node vs Managed Node**: The control node runs Ansible and parses YAML playbooks (must be Linux / WSL2). Managed nodes are the target servers managed over agentless SSH.
- **Idempotence**: Running the playbook multiple times yields the same final system state without unintended side effects or duplicate tasks.
- **Handlers**: Special tasks executed once at the end of a play only when notified by a task that made an actual change (`changed=true`).
- **Templates (Jinja2)**: Files ending in `.j2` with variables (e.g., `{{ app_port }}`) rendered dynamically into static config files on the target machine.
