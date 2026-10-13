import urllib.request
import http.cookiejar
import json
import time

base_url = "http://localhost:8080"
job_name = "CareSync-Test"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Get crumb
req = urllib.request.Request(f"{base_url}/crumbIssuer/api/json")
with opener.open(req) as resp:
    crumb_data = json.loads(resp.read().decode())
    crumb_field = crumb_data['crumbRequestField']
    crumb_value = crumb_data['crumb']

freestyle_xml = """<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description>CareSync Test Python &amp; Pytest</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
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
set PATH=C:\\Users\\lenovo\\AppData\\Local\\Programs\\Python\\Python313;C:\\Users\\lenovo\\AppData\\Local\\Programs\\Python\\Python313\\Scripts;%PATH%
python --version
cd /d "c:\\Users\\lenovo\\OneDrive\\Desktop\\Devops cat2"
call .\\.venv\\Scripts\\activate.bat
python -m pytest tests/test_health.py -v
      </command>
    </hudson.tasks.BatchFile>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>
"""

# Update job config
config_req = urllib.request.Request(f"{base_url}/job/{job_name}/config.xml", data=freestyle_xml.encode('utf-8'))
config_req.add_header(crumb_field, crumb_value)
config_req.add_header("Content-Type", "application/xml")
with opener.open(config_req) as resp:
    print("Updated config:", resp.status)

# Trigger build #3
build_req = urllib.request.Request(f"{base_url}/job/{job_name}/build")
build_req.add_header(crumb_field, crumb_value)
build_req.data = b""
with opener.open(build_req) as resp:
    print("Triggered build #3:", resp.status)

# Wait for build 3
time.sleep(3)
for _ in range(15):
    time.sleep(2)
    try:
        log_req = urllib.request.Request(f"{base_url}/job/{job_name}/3/consoleText")
        with opener.open(log_req) as lresp:
            log_text = lresp.read().decode('utf-8', errors='ignore')
            if "Finished:" in log_text:
                print(f"Log #3:\n{log_text}")
                break
    except Exception as e:
        pass
