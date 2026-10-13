import urllib.request
import json

base_url = "http://localhost:8080"

for job in ["CareSync-Freestyle-CI", "CareSync-Pipeline-CD"]:
    try:
        req = urllib.request.Request(f"{base_url}/job/{job}/api/json")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            builds = [b["number"] for b in data.get("builds", [])]
            last_build = data.get("lastBuild")
            last_successful = data.get("lastSuccessfulBuild")
            print(f"Job: {job}")
            print(f"  Builds: {builds}")
            print(f"  Last Build: {last_build['number'] if last_build else 'None'}")
            print(f"  Last Successful: {last_successful['number'] if last_successful else 'None'}")
            
            if last_build:
                num = last_build["number"]
                log_req = urllib.request.Request(f"{base_url}/job/{job}/{num}/consoleText")
                with urllib.request.urlopen(log_req) as lresp:
                    log = lresp.read().decode('utf-8', errors='ignore')
                    print(f"  Last 10 lines of Build #{num} log:")
                    for line in log.strip().splitlines()[-10:]:
                        print(f"    {line}")
    except Exception as e:
        print(f"Error checking {job}: {e}")
