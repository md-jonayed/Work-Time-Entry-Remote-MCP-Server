from fastmcp import FastMCP
import asyncio
import json
from pathlib import Path
import os

from db import init_db, get_connection, register_user, user_exists
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

mcp = FastMCP(name="IKIM Work Time Server")

# Config file for storing user preferences
PROJECT_DIR = Path(__file__).parent.absolute()
CONFIG_FILE = os.getenv('CONFIG_PATH', str(PROJECT_DIR / "config_user.json"))

# Ensure we're in the correct working directory
os.chdir(PROJECT_DIR)


async def has_schedule(user_id: str):
    """Return True if a work schedule blueprint exists for user."""
    schedule = await get_schedule(user_id)
    return len(schedule) > 0


# Security: All tools now require user_id parameter for data isolation


@mcp.tool
async def register_user_tool(user_id: str):
    """Register a new user for time tracking"""
    exists = await user_exists(user_id)
    if exists:
        return {"status": "already_exists", "user_id": user_id, "message": f"User '{user_id}' already exists"}

    result = await register_user(user_id)
    return {"status": "success", "user_id": user_id, "message": f"User '{user_id}' registered successfully"}


@mcp.tool
async def add_time_entry(user_id: str, date: str, start: str, end: str, remark: str = "", break_start: str | None = None, break_end: str | None = None):
    """Add a work entry with optional break time - USER DATA IS ISOLATED"""
    if not await has_schedule(user_id):
        raise ValueError(
            "Please define a work schedule before logging time entries. Use 'set_work_schedule' to configure your weekly schedule.")
    return await add_entry(user_id, date, start, end, remark, break_start, break_end)


@mcp.tool
async def set_work_schedule(user_id: str, day: str, hours: float):
    """Set weekly schedule for the user"""
    await set_schedule(user_id, day, hours)
    return {"user_id": user_id, "day": day, "hours": hours, "message": f"Schedule set: {day} - {hours} hours"}


@mcp.tool
async def get_work_schedule(user_id: str):
    """View work schedule for the user"""
    schedule = await get_schedule(user_id)
    return {"user_id": user_id, "schedule": schedule}


@mcp.tool
async def get_time_entries(user_id: str, month: int, year: int):
    """Get time entries for a specific user and month - DATA IS ISOLATED BY USER"""
    return await _get_time_entries(user_id, month, year)


@mcp.tool
async def get_time_entry(user_id: str, entry_id: int):
    """Get a single time entry by ID - DATA IS ISOLATED BY USER"""
    return await _get_time_entry(user_id, entry_id)


@mcp.tool
async def update_time_entry(user_id: str, entry_id: int, date: str | None = None, start: str | None = None, end: str | None = None, remark: str | None = None, break_start: str | None = None, break_end: str | None = None):
    """Update a saved time entry with optional break time - DATA IS ISOLATED BY USER"""
    return await _update_time_entry(user_id, entry_id, date=date, start=start, end=end, remark=remark, break_start=break_start, break_end=break_end)


@mcp.tool
async def delete_time_entry(user_id: str, entry_id: int):
    """Delete a saved time entry - DATA IS ISOLATED BY USER"""
    return await _delete_time_entry(user_id, entry_id)


@mcp.tool
async def get_month_summary(user_id: str, month: int, year: int):
    """Get monthly summary with worked vs expected hours - DATA IS ISOLATED BY USER"""
    return await month_summary(user_id, month, year)


@mcp.tool
async def export_month_excel(user_id: str, month: int, year: int):
    """Export IKIM-style Excel timesheet for user - DATA IS ISOLATED BY USER"""
    return await export_excel(user_id, month, year)


if __name__ == "__main__":
    # FastMCP automatically detects the transport (stdio for MCP, sse for standalone)
    mcp.run(transport="http", host="0.0.0.0", port=8000)
