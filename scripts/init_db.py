"""
CareSync Database Initialization Script
Creates all tables, relationships, and indices.
"""
import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db, get_db_path

if __name__ == '__main__':
    path = get_db_path()
    print(f"[CareSync] Initializing database at: {path}")
    init_db(path)
    print("[CareSync] Database tables successfully created!")
