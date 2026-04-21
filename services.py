from db import get_connection, register_user, user_exists
from utils import calculate_hours_with_break, get_weekday, count_weekday_in_month, validate_time_order, validate_date
from datetime import datetime


async def ensure_user(user_id: str):
    """Ensure user exists in the database"""
    if not await user_exists(user_id):
        await register_user(user_id)


async def add_entry(user_id: str, date: str, start: str, end: str, remark: str = "", break_start: str | None = None, break_end: str | None = None):
    """Add a work entry with optional break time - now with user isolation"""
    # Validate inputs
    validate_date(date)
    validate_time_order(start, end, break_start, break_end)

    # Ensure user exists
    await ensure_user(user_id)

    conn = await get_connection()
    weekday = get_weekday(date)

    # Sick leave auto-handling
    if remark.lower() == "sick leave":
        cursor = await conn.execute(
            "SELECT expected_hours FROM work_schedule WHERE user_id = ? AND weekday = ?", (user_id, weekday))
        row = await cursor.fetchone()
        hours = row[0] if row else 0
    else:
        hours = calculate_hours_with_break(start, end, break_start, break_end)

    cursor = await conn.execute("""
        INSERT INTO time_entries (user_id, date, weekday, start_time, end_time, break_start_time, break_end_time, total_hours, remark)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, date, weekday, start, end, break_start, break_end, hours, remark))

    entry_id = cursor.lastrowid
    try:
        await conn.commit()
    except Exception as e:
        if "readonly" in str(e).lower():
            raise ValueError(
                "Database is read-only. Please configure a writable database path using the DB_PATH environment variable for persistent storage.")
        raise

    return {"id": entry_id, "user_id": user_id, "date": date, "weekday": weekday, "hours": hours}


async def get_time_entries(user_id: str, month: int, year: int):
    """Get time entries for a specific user and month - data-isolated"""
    conn = await get_connection()
    prefix = f"{year}-{month:02d}"
    cursor = await conn.execute(
        "SELECT id, date, weekday, start_time, end_time, break_start_time, break_end_time, total_hours, remark FROM time_entries WHERE user_id = ? AND date LIKE ? ORDER BY date",
        (user_id, f"{prefix}%")
    )
    rows = await cursor.fetchall()
    return [
        {
            "id": row[0],
            "date": row[1],
            "weekday": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "break_start_time": row[5],
            "break_end_time": row[6],
            "hours": round(row[7], 2),
            "remark": row[8]
        }
        for row in rows
    ]


async def get_time_entry(user_id: str, entry_id: int):
    """Get a single time entry - data-isolated to user"""
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT id, date, weekday, start_time, end_time, break_start_time, break_end_time, total_hours, remark FROM time_entries WHERE id = ? AND user_id = ?",
        (entry_id, user_id)
    )
    row = await cursor.fetchone()
    if not row:
        return {"error": f"Time entry with ID {entry_id} not found"}
    return {
        "id": row[0],
        "date": row[1],
        "weekday": row[2],
        "start_time": row[3],
        "end_time": row[4],
        "break_start_time": row[5],
        "break_end_time": row[6],
        "hours": round(row[7], 2),
        "remark": row[8]
    }


async def update_time_entry(user_id: str, entry_id: int, date: str | None = None, start: str | None = None, end: str | None = None, remark: str | None = None, break_start: str | None = None, break_end: str | None = None):
    """Update a saved time entry - data-isolated to user"""
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT date, start_time, end_time, break_start_time, break_end_time, remark FROM time_entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
    row = await cursor.fetchone()
    if not row:
        return {"error": f"Time entry with id {entry_id} not found"}

    current_date, current_start, current_end, current_break_start, current_break_end, current_remark = row
    date = date or current_date
    start = start if start is not None else current_start
    end = end if end is not None else current_end
    break_start = break_start if break_start is not None else current_break_start
    break_end = break_end if break_end is not None else current_break_end
    remark = remark if remark is not None else current_remark

    # Validate inputs
    validate_date(date)
    if start and end:
        validate_time_order(start, end, break_start, break_end)

    weekday = get_weekday(date)

    if remark and remark.lower() == "sick leave":
        cursor = await conn.execute(
            "SELECT expected_hours FROM work_schedule WHERE user_id = ? AND weekday = ?", (
                user_id, weekday)
        )
        row = await cursor.fetchone()
        hours = row[0] if row else 0
    else:
        hours = calculate_hours_with_break(start, end, break_start, break_end)

    await conn.execute(
        "UPDATE time_entries SET date=?, weekday=?, start_time=?, end_time=?, break_start_time=?, break_end_time=?, total_hours=?, remark=?, updated_at=CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?",
        (date, weekday, start, end, break_start,
         break_end, hours, remark, entry_id, user_id)
    )
    try:
        await conn.commit()
    except Exception as e:
        if "readonly" in str(e).lower():
            raise ValueError(
                "Database is read-only. Please configure a writable database path using the DB_PATH environment variable for persistent storage.")
        raise
    return await get_time_entry(user_id, entry_id)


async def delete_time_entry(user_id: str, entry_id: int):
    """Delete a saved time entry - data-isolated to user"""
    existing_entry = await get_time_entry(user_id, entry_id)
    if "error" in existing_entry:
        return existing_entry

    conn = await get_connection()
    cursor = await conn.execute("DELETE FROM time_entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
    deleted = cursor.rowcount
    try:
        await conn.commit()
    except Exception as e:
        if "readonly" in str(e).lower():
            raise ValueError(
                "Database is read-only. Please configure a writable database path using the DB_PATH environment variable for persistent storage.")
        raise
    return {"deleted": deleted, "id": entry_id}


async def set_schedule(user_id: str, day: str, hours: float):
    """Set weekly schedule for a user"""
    await ensure_user(user_id)

    conn = await get_connection()
    # Validate day
    valid_days = ["Monday", "Tuesday", "Wednesday",
                  "Thursday", "Friday", "Saturday", "Sunday"]
    if day not in valid_days:
        raise ValueError(f"Invalid day: {day}. Must be one of {valid_days}")

    if hours < 0:
        raise ValueError("Hours must be non-negative")

    await conn.execute(
        "INSERT OR REPLACE INTO work_schedule (user_id, weekday, expected_hours) VALUES (?, ?, ?)",
        (user_id, day, hours)
    )
    await conn.commit()
    return {"user_id": user_id, "day": day, "hours": hours}


async def get_schedule(user_id: str):
    """Get work schedule for a user"""
    await ensure_user(user_id)

    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT weekday, expected_hours FROM work_schedule WHERE user_id = ? ORDER BY CASE weekday WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END",
        (user_id,)
    )
    rows = await cursor.fetchall()
    return [{"day": row[0], "hours": row[1]} for row in rows]


async def month_summary(user_id: str, month: int, year: int):
    """Get monthly summary for a user with worked vs expected hours"""
    await ensure_user(user_id)

    conn = await get_connection()

    # Get all entries for the month for this user
    cursor = await conn.execute(
        "SELECT date, weekday, total_hours FROM time_entries WHERE user_id = ? AND date LIKE ? ORDER BY date",
        (user_id, f"{year}-{month:02d}%")
    )
    entries = await cursor.fetchall()

    # Get work schedule for this user
    schedule = await get_schedule(user_id)
    schedule_dict = {item["day"]: item["hours"] for item in schedule}

    # Calculate expected hours
    from utils import count_weekday_in_month
    expected_hours = 0
    for day_name, day_hours in schedule_dict.items():
        count = count_weekday_in_month(year, month, day_name)
        expected_hours += count * day_hours

    # Calculate worked hours
    worked_hours = sum(float(entry[2]) if entry[2] else 0 for entry in entries)

    # Calculate overtime
    overtime = worked_hours - expected_hours

    # Count worked days
    worked_days = len(entries)

    # Count expected days in schedule
    expected_days = 0
    import calendar
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        weekday = get_weekday(date_str)
        if weekday in schedule_dict:
            expected_days += 1

    return {
        "user_id": user_id,
        "month": month,
        "year": year,
        "worked_hours": round(worked_hours, 2),
        "expected_hours": round(expected_hours, 2),
        "overtime": round(overtime, 2),
        "worked_days": worked_days,
        "expected_days": expected_days,
        "entries": [
            {
                "date": entry[0],
                "weekday": entry[1],
                "hours": round(float(entry[2]), 2) if entry[2] else 0
            }
            for entry in entries
        ]
    }
