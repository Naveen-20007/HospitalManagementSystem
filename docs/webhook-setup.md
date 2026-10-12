# CareSync — GitHub Webhook & Jenkins Automation Guide

This guide covers automated push-triggered continuous integration for **23IT723 DevOps Laboratory Experiment 6**.

---

## 1. How GitHub Webhooks Work

```
Developer pushes commit to GitHub
         │
         ▼
GitHub sends HTTP POST Request with JSON payload
         │
         ▼
Jenkins Webhook Listener (/github-webhook/)
         │
         ▼
Jenkins triggers automated Freestyle or Pipeline Build
```

A **Webhook** is an automated HTTP callback triggered by an event (such as `git push`). Instead of Jenkins repeatedly polling GitHub ("Are there new commits?"), GitHub instantly notifies Jenkins the second code is pushed.

---

## 2. The Localhost Challenge on Windows & How to Solve It

> [!IMPORTANT]
> **Why `http://localhost:8080/github-webhook/` will NOT work directly on GitHub:**
> GitHub's servers run in the public cloud. They cannot resolve `localhost` on your private Windows laptop because `localhost` refers to the machine sending the request.

### Safe Development Options for College Demonstrations:

#### Option A: Secure Public Tunnel via `localtunnel` (Recommended, Free, No Signup)
In a Windows PowerShell terminal:
```powershell
npx localtunnel --port 8080
```
Output:
```
your url is: https://fancy-hospital-agent.loca.lt
```
Your Jenkins Webhook URL becomes:
`https://fancy-hospital-agent.loca.lt/github-webhook/`

#### Option B: Secure Tunnel via `ngrok`
```powershell
ngrok http 8080
```
Output:
```
Forwarding https://1a2b-3c4d.ngrok-free.app -> http://localhost:8080
```
Your Jenkins Webhook URL becomes:
`https://1a2b-3c4d.ngrok-free.app/github-webhook/`

#### Option C: Lab / Cloud Server
If Jenkins is hosted on an AWS/Azure EC2 instance or college lab server with a public IP or DNS:
`http://<server-public-ip>:8080/github-webhook/`

---

## 3. Configuring the Webhook in GitHub

1. Open your repository on GitHub: `https://github.com/<your-username>/caresync-devops`.
2. Click **Settings** (tab on the top right) -> **Webhooks** (in left sidebar).
3. Click **Add webhook**.
4. Configure the parameters:
   - **Payload URL**: `https://<your-tunnel-url>/github-webhook/` (Note the mandatory trailing slash `/`).
   - **Content type**: `application/json`.
   - **Secret**: Optional secret token (leave blank for local lab demo).
   - **Which events would you like to trigger this webhook?**:
     Select **Just the push event**.
   - Check **Active**.
5. Click **Add webhook**.

---

## 4. Enabling Webhook Trigger in Jenkins

### For Freestyle Job (`CareSync-Freestyle-CI`):
1. Go to the project configuration in Jenkins.
2. Under **Build Triggers**, check:
   `[x] GitHub hook trigger for GITScm polling`.
3. Click **Save**.

### For Pipeline Job (`CareSync-Pipeline-CD`):
1. In the Pipeline project configuration:
2. Under **Build Triggers**, check:
   `[x] GitHub hook trigger for GITScm polling`.
3. Click **Save**.

---

## 5. End-to-End Test and Verification

1. On your Windows laptop, make a minor change to CareSync:
   ```bash
   git checkout develop
   echo "# Verified Webhook Push" >> README.md
   git commit -am "test(ci): trigger automated build via github webhook"
   git push origin develop
   ```
2. Check GitHub Webhook Delivery:
   - In GitHub -> **Settings** -> **Webhooks** -> Click your webhook URL.
   - Look at the **Recent Deliveries** tab.
   - You should see a green checkmark with HTTP **200 OK**.
3. Check Jenkins Build History:
   - Return to your Jenkins project page.
   - Notice that a new build (e.g. `#2`) started automatically without clicking "Build Now"!
   - Under the build details, look at **Started by GitHub push by <username>**.
