from db import get_connection
from utils import calculate_hours_with_break, get_weekday, count_weekday_in_month, validate_time_order, validate_date
from datetime import datetime


async def add_entry(date, start, end, remark="", break_start=None, break_end=None):
    # Validate inputs
    validate_date(date)
    validate_time_order(start, end, break_start, break_end)

    conn = await get_connection()
    weekday = get_weekday(date)

    # Sick leave auto-handling
    if remark.lower() == "sick leave":
        cursor = await conn.execute(
            "SELECT expected_hours FROM work_schedule WHERE weekday=?", (weekday,))
        row = await cursor.fetchone()
        hours = row[0] if row else 0
    else:
        hours = calculate_hours_with_break(start, end, break_start, break_end)

    await conn.execute("""
        INSERT INTO time_entries (date, weekday, start_time, end_time, break_start_time, break_end_time, total_hours, remark)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, weekday, start, end, break_start, break_end, hours, remark))

    entry_id = conn.last_insert_rowid()
    try:
        await conn.commit()
    except Exception as e:
        if "readonly" in str(e).lower():
            raise ValueError(
                "Database is read-only. Please configure a writable database path using the DB_PATH environment variable for persistent storage.")
        raise

    return {"id": entry_id, "date": date, "weekday": weekday, "hours": hours}


async def get_time_entries(month, year):
    conn = await get_connection()
    prefix = f"{year}-{month:02d}"
    cursor = await conn.execute(
        "SELECT id, date, weekday, start_time, end_time, break_start_time, break_end_time, total_hours, remark FROM time_entries WHERE date LIKE ? ORDER BY date",
        (f"{prefix}%",)
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


async def get_time_entry(entry_id):
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT id, date, weekday, start_time, end_time, break_start_time, break_end_time, total_hours, remark FROM time_entries WHERE id = ?",
        (entry_id,)
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


async def update_time_entry(entry_id, date=None, start=None, end=None, remark=None, break_start=None, break_end=None):
    conn = await get_connection()
    cursor = await conn.execute(
        "SELECT date, start_time, end_time, break_start_time, break_end_time, remark FROM time_entries WHERE id = ?", (entry_id,))
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
            "SELECT expected_hours FROM work_schedule WHERE weekday=?", (
                weekday,)
        )
        row = await cursor.fetchone()
        hours = row[0] if row else 0
    else:
        hours = calculate_hours_with_break(start, end, break_start, break_end)

    await conn.execute(
        "UPDATE time_entries SET date=?, weekday=?, start_time=?, end_time=?, break_start_time=?, break_end_time=?, total_hours=?, remark=? WHERE id = ?",
        (date, weekday, start, end, break_start, break_end, hours, remark, entry_id)
    )
    try:
        await conn.commit()
    except Exception as e:
        if "readonly" in str(e).lower():
            raise ValueError(
                "Database is read-only. Please configure a writable database path using the DB_PATH environment variable for persistent storage.")
        raise
    return await get_time_entry(entry_id)


async def delete_time_entry(entry_id):
    # get_time_entry will return error dict if entry doesn't exist
    existing_entry = await get_time_entry(entry_id)
    if "error" in existing_entry:
        return existing_entry

    conn = await get_connection()
    cursor = await conn.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
    deleted = cursor.rowcount
    try:
        await conn.commit()
    except Exception as e:
        if "readonly" in str(e).lower():
            raise ValueError(
                "Database is read-only. Please configure a writable database path using the DB_PATH environment variable for persistent storage.")
        raise
    return {"deleted": deleted, "id": entry_id}


async def set_schedule(day, hours):
    conn = await get_connection()
    await conn.execute("""
        INSERT OR REPLACE INTO work_schedule (weekday, expected_hours)
        VALUES (?, ?)
    """, (day, hours))

    try:
        await conn.commit()
    except Exception as e:
        if "readonly" in str(e).lower():
            raise ValueError(
                "Database is read-only. Please configure a writable database path using the DB_PATH environment variable for persistent storage.")
        raise


async def get_schedule():
    conn = await get_connection()
    cursor = await conn.execute("SELECT weekday, expected_hours FROM work_schedule")
    rows = await cursor.fetchall()
    return [{"day": d, "hours": h} for d, h in rows]


async def month_summary(month, year):
    conn = await get_connection()
    prefix = f"{year}-{month:02d}"

    # Get all entries for the month
    cursor = await conn.execute(
        "SELECT id, date, weekday, start_time, end_time, break_start_time, break_end_time, total_hours, remark FROM time_entries WHERE date LIKE ? ORDER BY date",
        (f"{prefix}%",)
    )
    entries = await cursor.fetchall()

    # Calculate totals
    worked = sum(entry[7] for entry in entries) if entries else 0

    # Get work schedule - ONLY calculate expected hours for scheduled days
    cursor = await conn.execute("SELECT weekday, expected_hours FROM work_schedule")
    schedule_rows = await cursor.fetchall()
    schedule = dict(schedule_rows)

    # Calculate expected hours based ONLY on scheduled days
    # If no schedule is set, expected_hours = 0
    expected = 0
    for weekday, daily_hours in schedule.items():
        day_count = count_weekday_in_month(year, month, weekday)
        expected += day_count * daily_hours

    # Format detailed entries
    detailed_entries = [
        {
            "id": entry[0],
            "date": entry[1],
            "day": entry[2],
            "start_time": entry[3],
            "end_time": entry[4],
            "break_start_time": entry[5],
            "break_end_time": entry[6],
            "hours": round(entry[7], 2),
            "remark": entry[8]
        }
        for entry in entries
    ]

    return {
        "month": month,
        "year": year,
        "entries": detailed_entries,
        "summary": {
            "total_worked_hours": round(worked, 2),
            "expected_hours": round(expected, 2),
            "overtime": round(worked - expected, 2),
            "entry_count": len(entries)
        }
    }
