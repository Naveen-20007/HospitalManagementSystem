#!/bin/sh
set -e

# CareSync Docker Container Entrypoint
echo "[CareSync Container] Initializing runtime environment..."

# Ensure persistent data directory exists
mkdir -p /app/data

# If database file does not exist, run schema initialization and demo seeds
if [ ! -f "${DATABASE_PATH:-/app/data/caresync.db}" ]; then
    echo "[CareSync Container] No database found at ${DATABASE_PATH:-/app/data/caresync.db}. Initializing and seeding demo data..."
    python scripts/seed_data.py
    if [ -f /app/caresync.db ] && [ ! -f "${DATABASE_PATH:-/app/data/caresync.db}" ]; then
        cp /app/caresync.db "${DATABASE_PATH:-/app/data/caresync.db}"
    fi
else
    echo "[CareSync Container] Existing database found at ${DATABASE_PATH:-/app/data/caresync.db}."
fi

echo "[CareSync Container] Starting application server..."
exec "$@"
