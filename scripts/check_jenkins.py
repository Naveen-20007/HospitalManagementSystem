import urllib.request
import re

url = "http://localhost:8080/"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        title = re.search(r'<title>(.*?)</title>', html)
        print("PAGE TITLE:", title.group(1) if title else "None")
        print("Has 'New Item':", "newjob" in html.lower() or "new item" in html.lower())
        print("Has 'log in' / 'sign in':", "log in" in html.lower() or "sign in" in html.lower())
        print("URL after redirects:", resp.geturl())
except Exception as e:
    print("Error:", e)
