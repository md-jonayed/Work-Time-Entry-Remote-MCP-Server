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

        # Enable foreign keys
        await conn.execute("PRAGMA foreign_keys = ON")

        # Create users table for user management and isolation
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
        """)

        # Initialize time_entries schema with user_id for data isolation
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            weekday TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            break_start_time TEXT,
            break_end_time TEXT,
            total_hours REAL,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, date)
        )
        """)

        # Add user_id column to existing time_entries if it doesn't exist
        try:
            await conn.execute(
                "ALTER TABLE time_entries ADD COLUMN user_id TEXT NOT NULL DEFAULT 'default_user'")
        except aiosqlite.OperationalError:
            pass  # Column already exists

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

        # Add timestamp columns if they don't exist
        try:
            await conn.execute(
                "ALTER TABLE time_entries ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except aiosqlite.OperationalError:
            pass  # Column already exists

        try:
            await conn.execute(
                "ALTER TABLE time_entries ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except aiosqlite.OperationalError:
            pass  # Column already exists

        # Initialize work_schedule schema with user_id for personalized schedules
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS work_schedule (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            weekday TEXT NOT NULL,
            expected_hours REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE(user_id, weekday)
        )
        """)

        # Add user_id column to existing work_schedule if it doesn't exist
        try:
            await conn.execute(
                "ALTER TABLE work_schedule ADD COLUMN user_id TEXT NOT NULL DEFAULT 'default_user'")
        except aiosqlite.OperationalError:
            pass  # Column already exists

        # Add created_at column to work_schedule if it doesn't exist
        try:
            await conn.execute(
                "ALTER TABLE work_schedule ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except aiosqlite.OperationalError:
            pass  # Column already exists

        await conn.commit()

    return conn


async def init_db():
    """Legacy function, now handled in get_connection"""
    pass


async def register_user(user_id: str, metadata: str = ""):
    """Register a new user"""
    conn = await get_connection()
    try:
        await conn.execute(
            "INSERT INTO users (user_id, metadata) VALUES (?, ?)",
            (user_id, metadata)
        )
        await conn.commit()
        return {"user_id": user_id, "status": "created"}
    except aiosqlite.IntegrityError:
        return {"user_id": user_id, "status": "already_exists"}


async def user_exists(user_id: str):
    """Check if user exists"""
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    return await cursor.fetchone() is not None
