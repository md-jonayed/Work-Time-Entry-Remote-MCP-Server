from openpyxl import Workbook
from datetime import datetime
import calendar
from db import get_connection
from utils import get_weekday


def export_excel(month, year, filename="timesheet.xlsx"):
    conn, cursor = get_connection()

    wb = Workbook()
    ws = wb.active
    ws.title = "IKIM Timesheet"

    ws.append(["Date", "Weekday", "Start", "End",
              "Break Start", "Break End", "Hours", "Remark"])

    days_in_month = calendar.monthrange(year, month)[1]

    for day in range(1, days_in_month + 1):
        date = f"{year}-{month:02d}-{day:02d}"
        weekday = get_weekday(date)

        cursor.execute(
            "SELECT start_time, end_time, break_start_time, break_end_time, total_hours, remark FROM time_entries WHERE date=?",
            (date,)
        )

        row = cursor.fetchone()

        if row:
            # Replace None with empty string for Excel
            clean_row = ["" if x is None else x for x in row]
            ws.append([date, weekday, *clean_row])
        else:
            ws.append([date, weekday, "", "", "", "", 0, "MISSED"])

    # totals
    cursor.execute(
        "SELECT SUM(total_hours) FROM time_entries WHERE date LIKE ?", (f"{year}-{month:02d}%",))
    total = cursor.fetchone()[0] or 0

    ws.append([])
    ws.append(["TOTAL", "", "", "", total])

    wb.save(filename)

    return {"file": filename}
