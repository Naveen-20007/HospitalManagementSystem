"""
CareSync Database Reset Script
Safely clears existing development database and re-runs init and seed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db_path
from scripts.seed_data import seed_database

if __name__ == '__main__':
    path = get_db_path()
    if os.path.exists(path):
        print(f"[CareSync] Removing old database at: {path}")
        os.remove(path)
    print("[CareSync] Re-seeding clean database...")
    seed_database()
    print("[CareSync] Reset complete!")
