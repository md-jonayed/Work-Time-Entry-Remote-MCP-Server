from openpyxl import Workbook
from datetime import datetime
import calendar
import asyncio
from db import get_connection
from utils import get_weekday


async def export_excel(user_id: str, month: int, year: int, filename: str | None = None):
    """Export user-specific timesheet to Excel - DATA IS ISOLATED BY USER"""
    conn = await get_connection()

    # Generate filename if not provided
    if filename is None:
        filename = f"/tmp/timesheet_{user_id}_{year}-{month:02d}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "IKIM Timesheet"

    # Add header with user info
    ws.append(["IKIM Timesheet", f"User: {user_id}", "", ""])
    ws.append(["Month", f"{calendar.month_name[month]} {year}", "", ""])
    ws.append([])  # Empty row for spacing

    ws.append(["Date", "Weekday", "Start", "End",
              "Break Start", "Break End", "Hours", "Remark"])

    days_in_month = calendar.monthrange(year, month)[1]

    for day in range(1, days_in_month + 1):
        date = f"{year}-{month:02d}-{day:02d}"
        weekday = get_weekday(date)

        cursor = await conn.execute(
            "SELECT start_time, end_time, break_start_time, break_end_time, total_hours, remark FROM time_entries WHERE user_id = ? AND date = ?",
            (user_id, date)
        )

        row = await cursor.fetchone()

        if row:
            # Replace None with empty string for Excel
            clean_row = ["" if x is None else x for x in row]
            ws.append([date, weekday, *clean_row])
        else:
            ws.append([date, weekday, "", "", "", "", 0, "MISSED"])

    # totals
    cursor = await conn.execute(
        "SELECT SUM(total_hours) FROM time_entries WHERE user_id = ? AND date LIKE ?",
        (user_id, f"{year}-{month:02d}%")
    )
    total_row = await cursor.fetchone()
    total = total_row[0] or 0

    ws.append([])
    ws.append(["TOTAL", "", "", "", total])

    await asyncio.to_thread(wb.save, filename)

    return {"file": filename, "user_id": user_id, "month": month, "year": year}
