import urllib.request
import urllib.parse
import http.cookiejar
import json
import time
import os

base_url = "http://localhost:8080"
job_name = "CareSync-Pipeline-CD"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def get_crumb():
    req = urllib.request.Request(f"{base_url}/crumbIssuer/api/json")
    with opener.open(req) as resp:
        data = json.loads(resp.read().decode())
        return data['crumbRequestField'], data['crumb']

with open(r"c:\Users\lenovo\OneDrive\Desktop\Devops cat2\Jenkinsfile", "r", encoding="utf-8") as f:
    jenkinsfile_text = f.read()

escaped_script = (jenkinsfile_text
    .replace("&", "&amp;")
    .replace("<", "&lt;")
    .replace(">", "&gt;")
    .replace('"', "&quot;"))

pipeline_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <actions/>
  <description>Experiment 5: Continuous Delivery / Pipeline as Code for CareSync Hospital Management System. 9-Stage Declarative Pipeline: Checkout, Environment Verification, Dependency Installation, Code Validation, Automated Pytest Suite, JUnit Report Publication, Docker Build, Deployment, and Health Verification.</description>
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

print("Updating CareSync-Pipeline-CD configuration...")
crumb_field, crumb_value = get_crumb()
req = urllib.request.Request(f"{base_url}/job/{job_name}/config.xml", data=pipeline_xml.encode('utf-8'))
req.add_header(crumb_field, crumb_value)
req.add_header("Content-Type", "application/xml")
with opener.open(req) as resp:
    print("Updated Pipeline config:", resp.status)

# Trigger build #2
build_req = urllib.request.Request(f"{base_url}/job/{job_name}/build")
build_req.add_header(crumb_field, crumb_value)
build_req.data = b""
with opener.open(build_req) as resp:
    print("Triggered build #2:", resp.status)

print("Waiting for build to finish...")
for _ in range(60):
    time.sleep(2)
    try:
        status_req = urllib.request.Request(f"{base_url}/job/{job_name}/api/json")
        with opener.open(status_req) as resp:
            data = json.loads(resp.read().decode())
            last_build = data.get("lastBuild")
            if last_build and last_build["number"] >= 2:
                num = last_build["number"]
                log_req = urllib.request.Request(f"{base_url}/job/{job_name}/{num}/consoleText")
                with opener.open(log_req) as lresp:
                    log_text = lresp.read().decode('utf-8', errors='ignore')
                    if "Finished:" in log_text:
                        print(f"Build #{num} complete! Tail log:")
                        lines = log_text.strip().splitlines()
                        tail = lines[-35:] if len(lines) > 35 else lines
                        print("\n".join(tail))
                        break
    except Exception as e:
        pass
