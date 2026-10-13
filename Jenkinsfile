pipeline {
    agent {
        node {
            label 'built-in'
            customWorkspace 'c:\\Users\\lenovo\\OneDrive\\Desktop\\Devops cat2'
        }
    }

    environment {
        APP_NAME     = 'caresync'
        IMAGE_NAME   = 'caresync-app'
        IMAGE_TAG    = "${BUILD_NUMBER}"
        REPORTS_DIR  = 'reports'
        HOST_PORT    = '8081'
        HEALTH_URL   = 'http://localhost:8081/health'
        APP_URL      = 'http://localhost:8081/'
        PATH         = "C:\\Users\\lenovo\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin;C:\\Users\\lenovo\\AppData\\Local\\Programs\\Python\\Python313;C:\\Users\\lenovo\\AppData\\Local\\Programs\\Python\\Python313\\Scripts;C:\\Program Files\\Git\\cmd;C:\\Program Files\\Java\\jdk-21\\bin;${env.PATH}"
    }

    options {
        timeout(time: 25, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timestamps()
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {
        // ====================================================================
        // STAGE 1: Source Code Checkout & VCS Information
        // ====================================================================
        stage('1. Checkout') {
            steps {
                echo "=========================================================="
                echo "[CareSync CI/CD] Stage 1: Checkout Source Code"
                echo "=========================================================="
                script {
                    try {
                        checkout scm
                    } catch (Exception e) {
                        echo "Operating in local workspace: ${e.message}"
                    }
                    bat 'git log -1 --oneline || ver'
                    echo "Build Number : ${BUILD_NUMBER}"
                    echo "Branch       : ${env.GIT_BRANCH ?: 'main'}"
                }
            }
        }

        // ====================================================================
        // STAGE 2: Validate Project Structure & Syntax
        // ====================================================================
        stage('2. Validate Structure') {
            steps {
                echo "=========================================================="
                echo "[CareSync CI/CD] Stage 2: Validating Project Structure"
                echo "=========================================================="
                bat '''
                    @echo on
                    echo Checking core project components...
                    if not exist "app" ( echo Missing app directory & exit /b 1 )
                    if not exist "tests" ( echo Missing tests directory & exit /b 1 )
                    if not exist "Dockerfile" ( echo Missing Dockerfile & exit /b 1 )
                    if not exist "compose.yaml" ( echo Missing compose.yaml & exit /b 1 )
                    if not exist "requirements.txt" ( echo Missing requirements.txt & exit /b 1 )
                    echo Project directory structure verified.
                    
                    echo Checking Python syntax compilation...
                    python -m py_compile app.py app/__init__.py app/models.py app/db.py
                    echo Syntax validation successful.
                '''
            }
        }

        // ====================================================================
        // STAGE 3: Python Virtual Environment & Dependencies
        // ====================================================================
        stage('3. Prepare Dependencies') {
            steps {
                echo "=========================================================="
                echo "[CareSync CI/CD] Stage 3: Preparing Python Dependencies"
                echo "=========================================================="
                bat '''
                    @echo on
                    if not exist ".venv" (
                        echo Creating virtual environment...
                        python -m venv .venv
                    )
                    call .venv\\Scripts\\activate.bat
                    pip install --no-warn-script-location -r requirements.txt
                    python --version
                    pytest --version
                '''
            }
        }

        // ====================================================================
        // STAGE 4: Automated Testing Suite (Pytest)
        // ====================================================================
        stage('4. Run Automated Tests') {
            steps {
                echo "=========================================================="
                echo "[CareSync CI/CD] Stage 4: Executing Pytest Test Suite"
                echo "=========================================================="
                bat '''
                    @echo on
                    call .venv\\Scripts\\activate.bat
                    if not exist "reports" ( mkdir reports )
                    python -m pytest -v --junitxml=reports/junit.xml
                '''
            }
            post {
                always {
                    echo "=========================================================="
                    echo "[CareSync CI/CD] Publishing JUnit XML Test Results"
                    echo "=========================================================="
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        // ====================================================================
        // STAGE 5: Docker Container Image Build
        // ====================================================================
        stage('5. Build Docker Image') {
            steps {
                echo "=========================================================="
                echo "[CareSync CI/CD] Stage 5: Building Docker Image: ${IMAGE_NAME}:${IMAGE_TAG}"
                echo "=========================================================="
                bat """
                    @echo on
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                    docker images | findstr ${IMAGE_NAME}
                """
            }
        }

        // ====================================================================
        // STAGE 6: Automated Deployment via Docker Compose
        // ====================================================================
        stage('6. Deploy via Docker Compose') {
            steps {
                echo "=========================================================="
                echo "[CareSync CI/CD] Stage 6: Deploying Application Stack"
                echo "=========================================================="
                bat '''
                    @echo on
                    docker compose down --remove-orphans || ver
                    docker compose up -d
                    docker compose ps
                '''
            }
        }

        // ====================================================================
        // STAGE 7: Live Health & Readiness Verification
        // ====================================================================
        stage('7. Health Verification') {
            steps {
                echo "=========================================================="
                echo "[CareSync CI/CD] Stage 7: Verifying Live Application Health"
                echo "=========================================================="
                bat '''
                    @echo on
                    echo Waiting for containers to become healthy and verifying live endpoints...
                    python scripts/verify_health.py http://localhost:8081
                    echo Automatically launching CareSync website in browser...
                    powershell -NoProfile -Command "Start-Process 'http://localhost:8081'" || ver
                '''
            }
        }
    }

    // ========================================================================
    // Post-Build Pipeline Notifications & Artifact Archiving
    // ========================================================================
    post {
        always {
            archiveArtifacts artifacts: 'reports/**/*.xml', allowEmptyArchive: true
            echo "=========================================================="
            echo "[CareSync CI/CD] Pipeline run finished for build #${BUILD_NUMBER}"
            echo "=========================================================="
        }
        success {
            echo "=========================================================="
            echo "PIPELINE RESULT: SUCCESS"
            echo "CareSync Hospital System deployed and verified successfully!"
            echo "Access application at: http://localhost:8081"
            echo "Health status at      : http://localhost:8081/health"
            echo "=========================================================="
        }
        failure {
            echo "=========================================================="
            echo "PIPELINE RESULT: FAILED"
            echo "Capturing diagnostic container logs..."
            echo "=========================================================="
            bat 'docker compose logs --tail 50 || ver'
        }
    }
}
