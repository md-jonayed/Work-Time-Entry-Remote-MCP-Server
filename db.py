import aiosqlite
import os
from pathlib import Path
from config import DB_NAME

# Lazy initialization
conn = None


async def get_connection():
    """Lazily initialize database connection and schema"""
    global conn
    if conn is None:
        # Ensure database directory exists
        db_path = Path(DB_NAME)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = await aiosqlite.connect(DB_NAME)

        # Initialize schema
        await conn.execute("""
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
            await conn.execute(
                "ALTER TABLE time_entries ADD COLUMN break_start_time TEXT")
        except aiosqlite.OperationalError:
            pass  # Column already exists

        try:
            await conn.execute(
                "ALTER TABLE time_entries ADD COLUMN break_end_time TEXT")
        except aiosqlite.OperationalError:
            pass  # Column already exists

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS work_schedule (
            id INTEGER PRIMARY KEY,
            weekday TEXT UNIQUE,
            expected_hours REAL
        )
        """)

        await conn.commit()

    return conn


async def init_db():
    """Legacy function, now handled in get_connection"""
    pass
