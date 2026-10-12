# CareSync — Ansible Configuration Management Guide

This directory contains configuration management playbooks for **23IT723 DevOps Laboratory Experiments 11 and 12**.

---

## 1. Important Note for Windows Developers

> [!IMPORTANT]
> **Why Ansible Control Nodes Require Linux / WSL2:**
> The Ansible control machine relies on POSIX system calls (specifically `fork()`, UNIX domain sockets, and pseudo-terminals) that do not exist natively in the Windows Win32 API. Therefore, Ansible **cannot be installed as a control node directly inside native Windows PowerShell**.
>
> On Windows laptops, the standard industry and academic workflow is to run Ansible through **WSL2 (Windows Subsystem for Linux)** or a Linux Virtual Machine targeting remote servers or local containers.

---

## 2. Setting Up the Control Environment in WSL2

### Step 1: Install WSL2 (if not already installed)
In an Administrator PowerShell terminal:
```powershell
wsl --install -d Ubuntu
```
Restart your computer if prompted.

### Step 2: Install Ansible inside WSL2 Ubuntu
Open your Ubuntu terminal from the Start menu and execute:
```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install -y ansible python3-pip
```

Verify the installation:
```bash
ansible --version
```

### Step 3: Install Docker Community Collection (for Experiment 12)
```bash
ansible-galaxy collection install community.docker
```

---

## 3. Directory Contents

- **`inventory.ini.example`**: Inventory file containing managed host definitions and connection parameters.
- **`playbook.yml`**: Playbook for **Experiment 11** (Automates Nginx installation, Gunicorn systemd service, configuration validation, handlers, and `/health` verification).
- **`deploy-docker.yml`**: Playbook for **Experiment 12** (Automates Docker network creation, persistent volume setup, container deployment, restart policies, and health verification).
- **`templates/nginx.conf.j2`**: Jinja2 dynamic template for Nginx reverse proxy configuration.
- **`templates/caresync.service.j2`**: Jinja2 systemd unit service template.

---

## 4. Running the Playbooks

Navigate to the Ansible directory inside WSL:
```bash
cd "/mnt/c/Users/lenovo/OneDrive/Desktop/Devops cat2/ansible"
```

### A. Validating Syntax (No execution)
Always perform a syntax check before running playbooks:
```bash
# Check web-server playbook
ansible-playbook --syntax-check playbook.yml

# Check Docker container playbook
ansible-playbook --syntax-check deploy-docker.yml
```

### B. Dry-Run / Check Mode
Test tasks without applying permanent changes to the system:
```bash
ansible-playbook -i inventory.ini.example playbook.yml --check
```

### C. Executing Web Server Playbook (Experiment 11)
```bash
ansible-playbook -i inventory.ini playbook.yml
```

### D. Executing Docker Container Playbook (Experiment 12)
```bash
ansible-playbook -i inventory.ini deploy-docker.yml
```

---

## 5. Idempotence Explained (For Lab Viva)

A core principle of Ansible demonstrated in these playbooks is **idempotence**:
- If you run `ansible-playbook playbook.yml` once, tasks perform the required installations and configurations (**Status: changed**).
- If you run the exact same command a second time immediately afterwards, Ansible inspects the current state of the server, sees that packages are already installed and files already match, and makes zero modifications (**Status: ok**, 0 changed).
- Handlers (such as restarting Nginx or CareSync) are only notified and triggered when template files or configurations actually change, avoiding unnecessary service disruptions!
