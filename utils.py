from datetime import datetime
import calendar


def calculate_hours(start, end):
    fmt = "%H:%M"
    s = datetime.strptime(start, fmt)
    e = datetime.strptime(end, fmt)
    return round((e - s).total_seconds() / 3600, 2)


def calculate_hours_with_break(start, end, break_start=None, break_end=None):
    """Calculate working hours with break deduction"""
    total_hours = calculate_hours(start, end)

    if break_start and break_end and break_start != break_end:
        break_hours = calculate_hours(break_start, break_end)
        return round(total_hours - break_hours, 2)

    return total_hours


def validate_date(date_str):
    """Validate date string format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            f"Invalid date format: {date_str}. Expected YYYY-MM-DD")


def get_weekday(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")


def validate_time_order(start, end, break_start=None, break_end=None):
    """Validate that start < end and break_start <= break_end if provided (equal means no break)"""
    fmt = "%H:%M"
    start_time = datetime.strptime(start, fmt)
    end_time = datetime.strptime(end, fmt)

    if start_time >= end_time:
        raise ValueError("Start time must be before end time")

    if break_start and break_end:
        break_start_time = datetime.strptime(break_start, fmt)
        break_end_time = datetime.strptime(break_end, fmt)
        if break_start_time > break_end_time:
            raise ValueError(
                "Break start time must not be after break end time")
        if break_start_time < start_time or break_end_time > end_time:
            raise ValueError("Break times must be within work hours")


def count_weekday_in_month(year, month, weekday_name):
    idx = list(calendar.day_name).index(weekday_name)
    count = 0

    for d in range(1, 32):
        try:
            if datetime(year, month, d).weekday() == idx:
                count += 1
        except:
            break

    return count
