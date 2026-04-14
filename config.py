import os
from pathlib import Path

# Use absolute path for database to avoid working directory issues
PROJECT_DIR = Path(__file__).parent.absolute()
DB_NAME = str(PROJECT_DIR / "work_time.db")

# Make DEFAULT_WEEKLY_HOURS configurable via environment variable
DEFAULT_WEEKLY_HOURS = float(os.getenv("DEFAULT_WEEKLY_HOURS", "9"))

# Ensure database directory exists
db_dir = Path(DB_NAME).parent
if db_dir != Path("."):
    db_dir.mkdir(parents=True, exist_ok=True)
