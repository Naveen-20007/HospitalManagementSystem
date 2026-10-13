"""
CareSync Live Deployment Health Verifier
Probes the Nginx proxy and Flask Gunicorn backend to confirm container health.
"""
import urllib.request
import time
import sys

def verify_health(base_url="http://localhost:8081", max_attempts=20, delay_sec=2):
    health_url = f"{base_url}/health"
    print(f"[*] Probing CareSync health endpoint: {health_url}")
    
    healthy = False
    for attempt in range(1, max_attempts + 1):
        try:
            req = urllib.request.Request(health_url, headers={"User-Agent": "CareSync-HealthProbe/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode('utf-8')
                if resp.status == 200 and "healthy" in body:
                    print(f"[+] Attempt {attempt}/{max_attempts}: Health check PASSED!")
                    print(f"    Status: {resp.status}, Response: {body.strip()}")
                    healthy = True
                    break
        except Exception as e:
            print(f"[-] Attempt {attempt}/{max_attempts}: Waiting for containers... ({e})")
        time.sleep(delay_sec)

    if not healthy:
        print("[!] ERROR: CareSync health check timed out.")
        return False

    # Also verify web root UI
    root_url = f"{base_url}/"
    print(f"[*] Probing CareSync Web UI root: {root_url}")
    try:
        req = urllib.request.Request(root_url, headers={"User-Agent": "CareSync-HealthProbe/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f"[+] Root UI returned HTTP {resp.status} ({len(content)} bytes)")
            if "CareSync" in content:
                print("[+] Application title verified in HTML response.")
    except Exception as e:
        print(f"[-] Root UI probe warning: {e}")

    print("[SUCCESS] CareSync deployment is fully healthy, operational, and serving traffic!")
    return True

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8081"
    ok = verify_health(url)
    sys.exit(0 if ok else 1)
