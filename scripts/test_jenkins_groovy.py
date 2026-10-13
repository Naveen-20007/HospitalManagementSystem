import urllib.request
import urllib.parse
import json

base_url = "http://localhost:8080"

# Fetch Crumb
req = urllib.request.Request(f"{base_url}/crumbIssuer/api/json")
with urllib.request.urlopen(req) as resp:
    crumb_data = json.loads(resp.read().decode())
    crumb_field = crumb_data['crumbRequestField']
    crumb_value = crumb_data['crumb']

groovy_code = """
def wherePython = "cmd.exe /c where python".execute().text
def whereGit = "cmd.exe /c where git".execute().text
def user = System.getProperty("user.name")
def home = System.getenv("JENKINS_HOME")
println "User: " + user
println "Jenkins Home: " + home
println "Where python:\\n" + wherePython
println "Where git:\\n" + whereGit
"""

post_data = urllib.parse.urlencode({'script': groovy_code}).encode('utf-8')
post_req = urllib.request.Request(f"{base_url}/scriptText", data=post_data)
post_req.add_header(crumb_field, crumb_value)
post_req.add_header("Content-Type", "application/x-www-form-urlencoded")

try:
    with urllib.request.urlopen(post_req) as resp:
        print("Groovy Script Output:")
        print(resp.read().decode('utf-8'))
except Exception as e:
    print("Script Console Error:", e)
