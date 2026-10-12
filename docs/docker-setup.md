# CareSync — Docker & Docker Compose Deployment Guide

This guide covers Containerization, multi-stage images, port mapping, volume persistence, and container lifecycle for **23IT723 DevOps Laboratory Experiments 7, 8, 9, and 12**.

---

## 1. Container Lifecycle Commands (Experiment 7)

Every command demonstrated in the DevOps laboratory:

| Operation | Command | Explanation |
| :--- | :--- | :--- |
| **Pull Image** | `docker pull python:3.11-slim` | Downloads base image from Docker Hub registry |
| **List Images** | `docker images` | Displays cached local images, tags, IDs, and virtual sizes |
| **Build Image** | `docker build -t caresync:1.0 .` | Builds custom image according to instructions in `Dockerfile` |
| **Run Container** | `docker run -d -p 5000:5000 --name caresync-test caresync:1.0` | Starts detached container with host-to-container port mapping |
| **List Active** | `docker ps` | Shows currently running containers, ports, and status |
| **List All** | `docker ps -a` | Shows all containers including stopped or exited ones |
| **View Logs** | `docker logs -f caresync-test` | Streams stdout/stderr application logs |
| **Inspect** | `docker inspect caresync-test` | Displays JSON configuration, IP address, mounts, and health state |
| **Execute Inside** | `docker exec -it caresync-test sh` | Opens interactive terminal session inside the container |
| **Stop** | `docker stop caresync-test` | Sends `SIGTERM` followed by `SIGKILL` to cleanly stop container |
| **Start** | `docker start caresync-test` | Re-runs a previously stopped container |
| **Restart** | `docker restart caresync-test` | Stops and immediately restarts container |
| **Remove Container** | `docker rm caresync-test` | Deletes stopped container instance |
| **Remove Image** | `docker rmi caresync:1.0` | Deletes image from local storage |

---

## 2. Port Mapping Explained (Host vs Container)

```
Browser Request: http://localhost:8080
       │
       ▼ (Host Port 8080 mapped to Nginx Container Port 80)
┌──────────────────────────────────────────────┐
│  Nginx Reverse Proxy Container (Port 80)     │
│  File: nginx/default.conf                    │
└──────────────────────┬───────────────────────┘
                       │ (Internal Docker Bridge Network: caresync-net)
                       ▼ (Proxy Pass to caresync-app:5000)
┌──────────────────────────────────────────────┐
│  CareSync Flask Application Container        │
│  Gunicorn WSGI listening on Port 5000        │
└──────────────────────────────────────────────┘
```

When you specify `-p 8080:80`:
- **`8080` (Left)**: The port exposed on your Windows laptop (host).
- **`80` (Right)**: The internal port on which Nginx listens inside its container.

---

## 3. Persistent Volumes for SQLite Database

Without persistent volumes, any changes saved to `caresync.db` would be wiped when the container is deleted (`docker rm`).

In `compose.yaml`:
```yaml
volumes:
  - caresync_data:/app/data
```
The named volume `caresync_persistent_db` maps to `/app/data` inside the container. SQLite writes to `/app/data/caresync.db`. When the container stops, restarts, or is rebuilt, all appointments, patients, and queue tokens remain safe in the Docker volume on the host drive.

---

## 4. Operating System Image Comparison (Experiment 8)

Compare Debian Slim against Alpine Linux:

### Build Debian Slim Image:
```bash
docker build -t caresync:debian -f Dockerfile .
```

### Build Alpine Linux Image:
```bash
docker build -t caresync:alpine -f docker/Dockerfile.alpine .
```

### Compare Size and Properties:
```bash
docker images | grep caresync
```

| Metric | Debian Slim (`python:3.11-slim`) | Alpine Linux (`python:3.11-alpine`) |
| :--- | :--- | :--- |
| **Package Manager** | `apt-get` | `apk` |
| **C Library** | `glibc` | `musl libc` |
| **Base Size** | ~140 MB | ~50 MB |
| **Compatibility** | Universal Python wheels support | May require compiling C extensions |
| **Production Choice** | Standard for robust Flask deployments | Extreme lightweight edge deployments |

---

## 5. Docker Compose Orchestration (Experiment 9)

### Start Full Stack (App + Nginx + Persistent Volume):
```bash
docker compose up -d --build
```

### Verify Service Health:
```bash
docker compose ps
```
Both `caresync-app` and `caresync-nginx` will show `Up (healthy)`.

### View Live Combined Logs:
```bash
docker compose logs -f
```

### Access Application:
Open your browser at:
`http://localhost:8080`

### Verify Persistence:
1. Book an appointment through the browser at `http://localhost:8080`.
2. Stop and recreate the containers:
   ```bash
   docker compose down
   docker compose up -d
   ```
3. Refresh `http://localhost:8080` — your appointment is still intact!

### Teardown:
```bash
docker compose down
```
To remove the persistent volume as well during a complete reset:
```bash
docker compose down -v
```
