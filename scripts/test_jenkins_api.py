import urllib.request
import json

base_url = "http://localhost:8080"

# Check crumb
try:
    req = urllib.request.Request(f"{base_url}/crumbIssuer/api/json")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("CRUMB:", data)
except Exception as e:
    print("Crumb not required or error:", e)

# Check info
try:
    req = urllib.request.Request(f"{base_url}/api/json")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print("Jenkins Mode:", data.get("mode"))
        print("Jobs currently:", [j['name'] for j in data.get("jobs", [])])
except Exception as e:
    print("API error:", e)
