# CareSync — Jenkins Freestyle Job & Declarative Pipeline Guide

This guide covers CI/CD automation, Freestyle configuration, Declarative Pipeline execution, and JUnit test reporting for **23IT723 DevOps Laboratory Experiments 4, 5, and 10**.

---

## 1. Prerequisites & Jenkins Installation

### Starting Jenkins on Windows:
1. **Option A: Native Windows Service / WAR file**:
   ```powershell
   # If using jenkins.war with Java 17/21:
   java -jar jenkins.war --httpPort=8080
   ```
2. **Option B: Running Jenkins in Docker**:
   ```bash
   docker run -d -p 8085:8080 -p 50000:50000 --name jenkins-lab -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
   ```
3. Open `http://localhost:8080` (or `http://localhost:8085`) in your web browser.
4. Retrieve the initial admin password and install the **Suggested Plugins**.

### Required Jenkins Plugins:
- **Git plugin**: Connects Jenkins to GitHub repositories.
- **Pipeline**: Supports Declarative and Scripted Pipelines (`Jenkinsfile`).
- **JUnit Plugin**: Parses `reports/junit.xml` and renders test health trend graphs.
- **GitHub Integration Plugin**: Handles GitHub webhooks.

---

## 2. Setting Up Jenkins Freestyle Job (Experiment 4)

### Step 1: Create Job
1. On Jenkins Dashboard, click **New Item**.
2. Enter item name: `CareSync-Freestyle-CI`.
3. Select **Freestyle project** and click **OK**.

### Step 2: Source Code Management (SCM)
1. Select the **Git** radio button.
2. **Repository URL**: `https://github.com/<your-github-username>/caresync-devops.git`.
3. **Credentials**: If public, leave as `none`. If private, click **Add -> Jenkins**, select **Username with password** (or GitHub Personal Access Token / PAT), and select it.
4. **Branch Specifier**: `*/main` or `*/develop`.

### Step 3: Build Triggers
- Check **GitHub hook trigger for GITScm polling** (for webhooks).
- Or check **Poll SCM** with schedule `H/5 * * * *` (polls every 5 minutes if no webhook is reachable).

### Step 4: Build Steps (Execute Tests)
Click **Add build step**:
- On **Windows**: Choose **Execute Windows batch command**:
  ```bat
  cd /d "%WORKSPACE%"
  if not exist ".venv" ( python -m venv .venv )
  call .venv\Scripts\activate.bat
  pip install -r requirements.txt
  if not exist "reports" ( mkdir reports )
  pytest -v --junitxml=reports/junit.xml
  ```
- On **Linux / Mac**: Choose **Execute shell**:
  ```bash
  python3 -m venv .venv
  . .venv/bin/activate
  pip install -r requirements.txt
  mkdir -p reports
  pytest -v --junitxml=reports/junit.xml
  ```

### Step 5: Post-build Actions (Publish Reports - Experiment 10)
1. Click **Add post-build action** -> **Publish JUnit test result report**.
2. Set **Test report XMLs**: `reports/junit.xml`.
3. Check **Retain long standard output/error**.
4. Click **Save**.

### Step 6: Test & Verify
1. Click **Build Now**.
2. Click the build number (e.g. `#1`) -> **Console Output**.
3. Verify test execution finishes with exit code `0`.
4. Click **Test Result** in the sidebar to view the interactive test suite breakdown showing all 30 passing tests!

---

## 3. Setting Up Jenkins Declarative Pipeline (Experiment 5)

The repository includes a ready-to-use **`Jenkinsfile`** defining a 9-stage pipeline:
1. **Checkout**: Pulls Git repository.
2. **Environment Verification**: Inspects Python, Git, and Docker.
3. **Dependency Installation**: Sets up virtual environment and installs pinned packages.
4. **Application Validation**: Runs syntax check (`py_compile`).
5. **Automated Tests**: Runs Pytest and creates `reports/junit.xml`.
6. **Test Report Publication**: Publishes JUnit XML directly to Jenkins UI.
7. **Docker Image Build**: Builds `caresync-app:latest` if Docker is active.
8. **Deployment**: Deploys application conditionally when on `main` or `develop`.
9. **Health Verification**: Invokes `/health` and `/health/ready` to verify deployment integrity.

### Configuring the Pipeline Job in Jenkins:
1. Jenkins Dashboard -> **New Item**.
2. Name: `CareSync-Pipeline-CD` -> Select **Pipeline** -> **OK**.
3. Scroll to **Pipeline** section:
   - **Definition**: Select **Pipeline script from SCM**.
   - **SCM**: Select **Git**.
   - **Repository URL**: `https://github.com/<your-username>/caresync-devops.git`.
   - **Branches to build**: `*/main`.
   - **Script Path**: `Jenkinsfile`.
4. Click **Save**.
5. Click **Build Now** to execute the complete pipeline!

---

## 4. Continuous Testing & Failure Demonstration (Experiment 10)

During viva evaluation, the examiner may ask: *"What happens if an automated test fails in CI/CD?"*

### Demonstrating Failure Handling:
1. Intentionally introduce an assertion failure in `tests/test_app.py`:
   ```python
   def test_intentional_failure():
       assert 1 == 2  # Fails!
   ```
2. Commit and push:
   ```bash
   git commit -am "test: demonstrate pipeline failure"
   git push origin develop
   ```
3. Jenkins runs the pipeline:
   - **Stage 5 (Automated Tests)**: Detects the assertion error and exits with non-zero code.
   - **Stage 6 (Report Publication)**: Records the failed test in `reports/junit.xml`.
   - **Stages 7, 8, 9 (Build & Deploy)**: **SKIPPED / ABORTED!**
   - **Build Status**: Marked **FAILED (RED)**.
4. Revert the failure and push again:
   ```bash
   git revert HEAD --no-edit
   git push origin develop
   ```
   The build turns **GREEN**, and deployment succeeds.
