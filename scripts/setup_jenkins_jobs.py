import urllib.request
import urllib.parse
import http.cookiejar
import json
import time
import os

base_url = "http://localhost:8080"
repo_path = r"c:\Users\lenovo\OneDrive\Desktop\Devops cat2"
repo_url = "file:///" + repo_path.replace("\\", "/")

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def get_crumb():
    req = urllib.request.Request(f"{base_url}/crumbIssuer/api/json")
    with opener.open(req) as resp:
        data = json.loads(resp.read().decode())
        return data['crumbRequestField'], data['crumb']

def create_or_update_job(name, xml_content):
    crumb_field, crumb_value = get_crumb()
    # Check if job exists
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

    # Wait for queue and build start
    print(f"Waiting for '{name}' build to start and complete...")
    build_num = None
    for _ in range(40):
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
                            # Print summary
                            lines = log_text.strip().splitlines()
                            tail = lines[-35:] if len(lines) > 35 else lines
                            print("\n".join(tail))
                            return True, build_num
        except Exception as e:
            pass
    return False, None

# 1. FREESTYLE JOB XML (Exp 4)
freestyle_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Experiment 4: Continuous Integration with Jenkins (Freestyle Project) for CareSync Hospital Management System. Automated build, dependency installation, 30 Pytest test execution, and JUnit XML test report publishing.</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <customWorkspace>{repo_path}</customWorkspace>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.BatchFile>
      <command>
set PATH=C:\\Users\\lenovo\\AppData\\Local\\Programs\\Python\\Python313;C:\\Users\\lenovo\\AppData\\Local\\Programs\\Python\\Python313\\Scripts;C:\\Program Files\\Git\\cmd;%PATH%
call .\\.venv\\Scripts\\activate.bat
if not exist "reports" ( mkdir reports )
python -m pytest -v --junitxml=reports/junit.xml
      </command>
    </hudson.tasks.BatchFile>
  </builders>
  <publishers>
    <hudson.tasks.junit.JUnitResultArchiver plugin="junit">
      <testResults>reports/junit.xml</testResults>
      <keepLongStdio>true</keepLongStdio>
      <healthScaleFactor>1.0</healthScaleFactor>
      <allowEmptyResults>false</allowEmptyResults>
    </hudson.tasks.junit.JUnitResultArchiver>
  </publishers>
  <buildWrappers/>
</project>
"""

# 2. Read Jenkinsfile for Pipeline Job (Exp 5)
with open(os.path.join(repo_path, "Jenkinsfile"), "r", encoding="utf-8") as f:
    jenkinsfile_content = f.read()

# For pipeline script without git server, adjust stage 1 to not fail if no git remote credentials
escaped_script = jenkinsfile_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

pipeline_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <actions/>
  <description>Experiment 5: Continuous Delivery / Pipeline as Code for CareSync Hospital Management System. 9-Stage Declarative Pipeline: Checkout, Environment Verification, Dependency Installation, Code Validation, Automated Pytest Suite, JUnit Report Publication, Docker Build, Deployment, and Health Verification.</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>{repo_url}</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
"""

if __name__ == "__main__":
    print("--- Setting up CareSync-Freestyle-CI ---")
    create_or_update_job("CareSync-Freestyle-CI", freestyle_xml)
    ok, num = trigger_and_wait("CareSync-Freestyle-CI")
    print(f"CareSync-Freestyle-CI finished: {ok}, Build #{num}")

    print("\n--- Setting up CareSync-Pipeline-CD ---")
    create_or_update_job("CareSync-Pipeline-CD", pipeline_xml)
    ok2, num2 = trigger_and_wait("CareSync-Pipeline-CD")
    print(f"CareSync-Pipeline-CD finished: {ok2}, Build #{num2}")
