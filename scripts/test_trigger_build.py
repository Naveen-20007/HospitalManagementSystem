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

# Trigger build
build_req = urllib.request.Request(f"{base_url}/job/{job_name}/build")
build_req.add_header(crumb_field, crumb_value)
build_req.data = b""

with opener.open(build_req) as resp:
    print("Build triggered, status:", resp.status)

# Wait for build to start
print("Waiting for build to execute...")
for _ in range(10):
    time.sleep(2)
    try:
        status_req = urllib.request.Request(f"{base_url}/job/{job_name}/api/json")
        with opener.open(status_req) as resp:
            data = json.loads(resp.read().decode())
            last_build = data.get("lastBuild")
            if last_build:
                num = last_build["number"]
                log_req = urllib.request.Request(f"{base_url}/job/{job_name}/{num}/consoleText")
                with opener.open(log_req) as lresp:
                    log_text = lresp.read().decode('utf-8', errors='ignore')
                    print(f"Build #{num} finished or in progress! Log:\n{log_text}")
                break
    except Exception as e:
        print("Waiting...", e)
