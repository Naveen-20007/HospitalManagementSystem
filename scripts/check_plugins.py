import urllib.request
import json

base_url = "http://localhost:8080"
req = urllib.request.Request(f"{base_url}/pluginManager/api/json?depth=1")
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        plugins = [p['shortName'] for p in data.get('plugins', []) if p.get('active')]
        print(f"Total active plugins: {len(plugins)}")
        for target in ['git', 'workflow-job', 'workflow-aggregator', 'junit', 'pipeline-model-definition']:
            print(f"Plugin '{target}': {'INSTALLED' if target in plugins else 'NOT installed'}")
        if len(plugins) < 20:
            print("All active plugins:", plugins)
except Exception as e:
    print("Error querying plugins:", e)
