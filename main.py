from fastmcp import FastMCP
from db import init_db, get_connection
from services import (
    add_entry,
    get_time_entries as _get_time_entries,
    get_time_entry as _get_time_entry,
    update_time_entry as _update_time_entry,
    delete_time_entry as _delete_time_entry,
    set_schedule,
    get_schedule,
    month_summary,
)
from excel_export import export_excel
import json
from pathlib import Path
import os
import asyncio

mcp = FastMCP(name="IKIM Work Time Server")

# Config file for storing user preferences
PROJECT_DIR = Path(__file__).parent.absolute()
CONFIG_FILE = os.getenv('CONFIG_PATH', str(PROJECT_DIR / "config_user.json"))

# Ensure we're in the correct working directory
os.chdir(PROJECT_DIR)


def load_default_hours():
    """Load default weekly hours from file, or None if not set."""
    if Path(CONFIG_FILE).exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get("default_weekly_hours")
        except:
            return None
    return None


def save_default_hours(hours: float):
    """Save default weekly hours to file"""
    data = {"default_weekly_hours": hours}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)


def get_schedule_total_hours():
    """Return the total weekly hours defined in the current work schedule."""
    schedule = asyncio.run(get_schedule())
    return sum(item["hours"] for item in schedule)


async def has_schedule():
    """Return True if a work schedule blueprint exists."""
    schedule = await get_schedule()
    return len(schedule) > 0


# Initialize database when the module is imported
asyncio.run(init_db())


@mcp.tool
async def add_time_entry(date: str, start: str, end: str, remark: str = "", break_start: str | None = None, break_end: str | None = None):
    """Add a work entry with optional break time"""
    if not await has_schedule() and load_default_hours() is None:
        raise ValueError(
            "Please define a work schedule or default weekly hours before logging time entries.")
    return await add_entry(date, start, end, remark, break_start, break_end)


@mcp.tool
async def set_work_schedule(day: str, hours: float):
    """Set weekly schedule"""
    await set_schedule(day, hours)
    return {"day": day, "hours": hours}


@mcp.tool
async def get_work_schedule():
    """View schedule"""
    return await get_schedule()


@mcp.tool
def set_default_weekly_hours(hours: float):
    """Set the fallback default weekly hours used when no schedule is defined."""
    save_default_hours(hours)
    return {"default_weekly_hours": hours, "message": "Default weekly hours updated"}


@mcp.tool
async def get_default_weekly_hours():
    """Get the current default weekly hours."""
    if await has_schedule():
        hours = get_schedule_total_hours()
    else:
        hours = load_default_hours()
    return {"default_weekly_hours": hours}


@mcp.tool
async def get_time_entries(month: int, year: int):
    """Get time entries for a month"""
    return await _get_time_entries(month, year)


@mcp.tool
async def get_time_entry(entry_id: int):
    """Get a single time entry by ID"""
    return await _get_time_entry(entry_id)


@mcp.tool
async def update_time_entry(entry_id: int, date: str | None = None, start: str | None = None, end: str | None = None, remark: str | None = None, break_start: str | None = None, break_end: str | None = None):
    """Update a saved time entry with optional break time"""
    return await _update_time_entry(entry_id, date=date, start=start, end=end, remark=remark, break_start=break_start, break_end=break_end)


@mcp.tool
async def delete_time_entry(entry_id: int):
    """Delete a saved time entry"""
    return await _delete_time_entry(entry_id)


@mcp.tool
async def get_month_summary(month: int, year: int):
    """Monthly summary"""
    return await month_summary(month, year)


@mcp.tool
async def export_month_excel(month: int, year: int):
    """Export IKIM-style Excel"""
    return await export_excel(month, year)


if __name__ == "__main__":
    # FastMCP automatically detects the transport (stdio for MCP, sse for standalone)
    mcp.run(transport="http", host="0.0.0.0", port=8000)
