import urllib.request
import urllib.parse
import http.cookiejar
import json

base_url = "http://localhost:8080"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# 1. Fetch Crumb with cookie
req = urllib.request.Request(f"{base_url}/crumbIssuer/api/json")
with opener.open(req) as resp:
    crumb_data = json.loads(resp.read().decode())
    crumb_field = crumb_data['crumbRequestField']
    crumb_value = crumb_data['crumb']
    print(f"Got Crumb: {crumb_field} = {crumb_value[:10]}...")

# 2. Check cookies stored
for cookie in cj:
    print(f"Cookie: {cookie.name} = {cookie.value}")

freestyle_xml = """<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description>CareSync Automated CI Test</description>
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
      <command>echo Hello CareSync CI from Jenkins</command>
    </hudson.tasks.BatchFile>
  </builders>
  <publishers/>
  <buildWrappers/>
</project>
"""

create_url = f"{base_url}/createItem?name=CareSync-Test"
create_req = urllib.request.Request(create_url, data=freestyle_xml.encode('utf-8'))
create_req.add_header(crumb_field, crumb_value)
create_req.add_header("Content-Type", "application/xml")

try:
    with opener.open(create_req) as resp:
        print("Create Job Status:", resp.status)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode('utf-8', errors='ignore'))
except Exception as e:
    print("Error:", e)
