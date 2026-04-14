import sqlite3
import os
from pathlib import Path
from config import DB_NAME

# Lazy initialization
conn = None
cursor = None


def get_connection():
    """Lazily initialize database connection"""
    global conn, cursor
    if conn is None:
        # Ensure database directory exists
        db_path = Path(DB_NAME)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
    return conn, cursor


def init_db():
    conn, cursor = get_connection()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS time_entries (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        weekday TEXT NOT NULL,
        start_time TEXT,
        end_time TEXT,
        break_start_time TEXT,
        break_end_time TEXT,
        total_hours REAL,
        remark TEXT
    )
    """)

    # Add break columns if they don't exist (for existing databases)
    try:
        cursor.execute(
            "ALTER TABLE time_entries ADD COLUMN break_start_time TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute(
            "ALTER TABLE time_entries ADD COLUMN break_end_time TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS work_schedule (
        id INTEGER PRIMARY KEY,
        weekday TEXT UNIQUE,
        expected_hours REAL
    )
    """)

    conn.commit()
