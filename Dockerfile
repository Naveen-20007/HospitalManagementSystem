# ==============================================================================
# CareSync Production Dockerfile
# Multi-stage/lightweight Debian Slim base, non-root user, persistent volume support
# ==============================================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    DATABASE_PATH=/app/data/caresync.db

WORKDIR /app

# Install runtime utilities (curl for container healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user and group for security
RUN groupadd -r caresync && useradd -r -g caresync -d /app -s /sbin/nologin caresync

# Create data directory for persistent SQLite storage
RUN mkdir -p /app/data && chown -R caresync:caresync /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ app/
COPY scripts/ scripts/
COPY app.py .
COPY docker/docker-entrypoint.sh /app/docker-entrypoint.sh

# Grant execution permissions and assign directory ownership
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh && \
    chmod +x /app/docker-entrypoint.sh && \
    chown -R caresync:caresync /app

# Switch to non-root user
USER caresync

# Expose internal application port
EXPOSE 5000

# Docker Healthcheck probe against the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Define entrypoint and default start command using Gunicorn WSGI
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "app:create_app()"]
