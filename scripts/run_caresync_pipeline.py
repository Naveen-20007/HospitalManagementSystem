import urllib.request
import urllib.parse
import http.cookiejar
import json
import time
import os
import sys

base_url = "http://localhost:8080"
repo_path = r"c:\Users\lenovo\OneDrive\Desktop\Devops cat2"

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
        print(f"[*] Job '{name}' exists, updating configuration...")
        post_url = f"{base_url}/job/{name}/config.xml"
    else:
        print(f"[*] Creating new job '{name}'...")
        post_url = f"{base_url}/createItem?name={urllib.parse.quote(name)}"

    req = urllib.request.Request(post_url, data=xml_content.encode('utf-8'))
    req.add_header(crumb_field, crumb_value)
    req.add_header("Content-Type", "application/xml")
    with opener.open(req) as resp:
        print(f"[+] Job '{name}' configured successfully (HTTP {resp.status})")

def trigger_and_watch(name):
    crumb_field, crumb_value = get_crumb()
    build_req = urllib.request.Request(f"{base_url}/job/{name}/build")
    build_req.add_header(crumb_field, crumb_value)
    build_req.data = b""
    with opener.open(build_req) as resp:
        print(f"[+] Build queued for '{name}' (HTTP {resp.status})")

    # Determine next build number
    status_req = urllib.request.Request(f"{base_url}/job/{name}/api/json")
    with opener.open(status_req) as resp:
        data = json.loads(resp.read().decode())
        next_num = data.get("nextBuildNumber", 1)
    
    print(f"[*] Expecting Build #{next_num}. Monitoring execution...")
    
    # Wait for build to start
    build_num = next_num
    started = False
    for _ in range(30):
        time.sleep(2)
        try:
            b_req = urllib.request.Request(f"{base_url}/job/{name}/{build_num}/api/json")
            with opener.open(b_req) as resp:
                b_data = json.loads(resp.read().decode())
                started = True
                print(f"[*] Build #{build_num} has started! Tracking progress...")
                break
        except Exception:
            pass

    if not started:
        print("[-] Build took too long to start in queue.")
        return False, None

    # Stream or monitor until completion
    for _ in range(60):
        time.sleep(3)
        try:
            b_req = urllib.request.Request(f"{base_url}/job/{name}/{build_num}/api/json")
            with opener.open(b_req) as resp:
                b_data = json.loads(resp.read().decode())
                if not b_data.get("building", True):
                    result = b_data.get("result", "UNKNOWN")
                    print(f"\n=======================================================")
                    print(f"[*] Build #{build_num} COMPLETED with RESULT: {result}")
                    print(f"=======================================================\n")
                    
                    # Fetch console log
                    log_req = urllib.request.Request(f"{base_url}/job/{name}/{build_num}/consoleText")
                    with opener.open(log_req) as lresp:
                        log_text = lresp.read().decode('utf-8', errors='ignore')
                        # Print last 60 lines
                        lines = log_text.strip().splitlines()
                        print("\n".join(lines[-60:] if len(lines) > 60 else lines))
                    
                    return result == "SUCCESS", build_num
        except Exception as e:
            pass

    print("[-] Build timeout after 3 minutes.")
    return False, build_num

# Read Jenkinsfile
jenkinsfile_path = os.path.join(repo_path, "Jenkinsfile")
with open(jenkinsfile_path, "r", encoding="utf-8") as f:
    jenkinsfile_script = f.read()

# Encode script into Jenkins CpsFlowDefinition
escaped_script = (
    jenkinsfile_script
    .replace("&", "&amp;")
    .replace("<", "&lt;")
    .replace(">", "&gt;")
    .replace('"', "&quot;")
)

pipeline_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <actions/>
  <description>CareSync Complete CI/CD Pipeline (23IT723 DevOps Laboratory Project). Stages: Checkout, Validate Structure, Dependency Preparation, Automated Pytest Suite, Docker Image Build, Docker Compose Deployment, Live Health &amp; UI Verification.</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps">
    <script>{escaped_script}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
"""

if __name__ == "__main__":
    job_name = "CareSync-Complete-CICD"
    create_or_update_job(job_name, pipeline_xml)
    success, bnum = trigger_and_watch(job_name)
    print(f"\n[FINAL STATUS] Job: {job_name}, Build: #{bnum}, Success: {success}")
    if not success:
        sys.exit(1)
