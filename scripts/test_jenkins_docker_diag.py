import urllib.request
import urllib.parse
import http.cookiejar
import json
import time

base_url = "http://localhost:8080"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def get_crumb():
    req = urllib.request.Request(f"{base_url}/crumbIssuer/api/json")
    with opener.open(req) as resp:
        data = json.loads(resp.read().decode())
        return data['crumbRequestField'], data['crumb']

def create_or_update_job(name, xml_content):
    crumb_field, crumb_value = get_crumb()
    check_req = urllib.request.Request(f"{base_url}/job/{name}/api/json")
    exists = False
    try:
        with opener.open(check_req):
            exists = True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            exists = False
        else:
            raise

    if exists:
        print(f"Job '{name}' exists, updating configuration...")
        post_url = f"{base_url}/job/{name}/config.xml"
    else:
        print(f"Creating new job '{name}'...")
        post_url = f"{base_url}/createItem?name={urllib.parse.quote(name)}"

    req = urllib.request.Request(post_url, data=xml_content.encode('utf-8'))
    req.add_header(crumb_field, crumb_value)
    req.add_header("Content-Type", "application/xml")
    with opener.open(req) as resp:
        print(f"Job '{name}' configured successfully (Status {resp.status})")

def trigger_and_wait(name):
    crumb_field, crumb_value = get_crumb()
    build_req = urllib.request.Request(f"{base_url}/job/{name}/build")
    build_req.add_header(crumb_field, crumb_value)
    build_req.data = b""
    with opener.open(build_req) as resp:
        print(f"Build queued for '{name}' (Status {resp.status})")

    print(f"Waiting for '{name}' build to complete...")
    for _ in range(45):
        time.sleep(2)
        try:
            status_req = urllib.request.Request(f"{base_url}/job/{name}/api/json")
            with opener.open(status_req) as resp:
                data = json.loads(resp.read().decode())
                last_build = data.get("lastBuild")
                if last_build:
                    build_num = last_build["number"]
                    log_req = urllib.request.Request(f"{base_url}/job/{name}/{build_num}/consoleText")
                    with opener.open(log_req) as lresp:
                        log_text = lresp.read().decode('utf-8', errors='ignore')
                        if "Finished:" in log_text:
                            print(f"\n==========================================")
                            print(f" Build #{build_num} finished for '{name}'")
                            print(f"==========================================")
                            print(log_text)
                            return "Finished: SUCCESS" in log_text, build_num
        except Exception as e:
            pass
    return False, None

diag_pipeline_xml = """<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <actions/>
  <description>Phase 5: Jenkins to Docker Diagnostic Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>
pipeline {
    agent any
    environment {
        PATH = "C:\\\\Users\\\\lenovo\\\\AppData\\\\Local\\\\Programs\\\\DockerDesktop\\\\resources\\\\bin;C:\\\\Users\\\\lenovo\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python313;C:\\\\Users\\\\lenovo\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python313\\\\Scripts;C:\\\\Program Files\\\\Git\\\\cmd;C:\\\\Program Files\\\\Java\\\\jdk-21\\\\bin;${env.PATH}"
    }
    stages {
        stage('Tool Verification') {
            steps {
                bat '''
                    @echo on
                    echo --- [1] OS and User ---
                    ver
                    echo Current User: %USERNAME%
                    echo --- [2] Java ---
                    java -version
                    echo --- [3] Git ---
                    git --version
                    echo --- [4] Python ---
                    python --version
                    echo --- [5] Docker CLI ---
                    docker --version
                    echo --- [6] Docker Compose ---
                    docker compose version
                    echo --- [7] Docker Daemon Connectivity ---
                    docker info
                '''
            }
        }
        stage('Test Image Build and Run') {
            steps {
                bat '''
                    @echo on
                    echo --- [8] Building Harmless Test Image ---
                    echo FROM alpine:latest > Dockerfile.diag
                    echo CMD ["echo", "JENKINS_DOCKER_VERIFIED_SUCCESSFULLY"] >> Dockerfile.diag
                    docker build -f Dockerfile.diag -t jenkins-docker-test:diag .
                    echo --- [9] Running Test Container ---
                    docker run --rm jenkins-docker-test:diag
                    echo --- [10] Cleanup ---
                    docker rmi jenkins-docker-test:diag
                    if exist Dockerfile.diag del Dockerfile.diag
                    echo --- SUCCESS: Jenkins to Docker Connection Fully Verified! ---
                '''
            }
        }
    }
}
    </script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
"""

if __name__ == "__main__":
    job_name = "Jenkins-Docker-Diagnostic"
    create_or_update_job(job_name, diag_pipeline_xml)
    success, bnum = trigger_and_wait(job_name)
    print(f"\nDiagnostic Result: success={success}, build={bnum}")
