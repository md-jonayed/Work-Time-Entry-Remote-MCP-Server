# WorkTime Entry MCP Remote Server

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

A comprehensive **Model Context Protocol (MCP)** server for professional work time tracking, designed to integrate seamlessly with AI assistants and automation tools. Track work hours, manage schedules, calculate overtime, and generate detailed Excel reports with enterprise-grade validation and error handling.

## 🌟 Key Features

### 📊 Time Tracking

- **Precise Time Entry**: Record work hours with start/end times and optional break periods
- **Smart Break Handling**: Equal break start/end times indicate "no break" for easy updates
- **Flexible Scheduling**: Define a weekly schedule as the primary work blueprint
- **Schedule-First Workflow**: Time entries require a defined schedule or fallback default weekly hours before logging
- **Expected Hours from Schedule**: Expected monthly hours are calculated only from scheduled weekdays
- **Monthly Summaries**: Comprehensive reports with worked hours, expected hours, and overtime

### 📈 Reporting & Export

- **Excel Export**: Generate professional IKIM-style Excel timesheets
- **Data Integrity**: Automatic handling of missing days and data validation
- **Entry IDs**: All entries include unique IDs for easy updates and deletions
- **Customizable Reports**: Export specific months with detailed breakdowns

### 🔧 Enterprise Features

- **Robust Validation**: Comprehensive input validation with clear error messages
- **Database Persistence**: SQLite-based storage with automatic schema management
- **Configuration Management**: JSON-based user preferences and environment variable support
- **Flexible Work Hours**: Configure weekly work hours and work days for accurate calculations
- **Thread Safety**: Optimized for MCP's single-threaded execution model

### 🤖 **MCP Integration**

- **AI Assistant Ready**: Full MCP protocol compliance for seamless AI integration
- **Tool-Based API**: 11 specialized tools for comprehensive time tracking operations
- **Type Safety**: Full type hints and structured data exchange
- **Error Handling**: Graceful error handling with detailed error responses

## 🏗️ Architecture

```
WorkTime Entry MCP Server
├── main.py          # MCP server setup and tool definitions
├── services.py      # Business logic and data operations
├── db.py           # Database connection and schema management
├── utils.py        # Utility functions and validation
├── excel_export.py # Excel report generation
├── config.py       # Configuration management
└── config_user.json # User preferences storage
```

### Database Schema

- **`time_entries`**: Work time records with break tracking
- **`work_schedule`**: Weekly schedule configuration
- **Automatic Migrations**: Schema updates handled transparently

## 📋 Prerequisites

- **Python**: 3.13 or higher
- **Dependencies**: Listed in `requirements.txt` or `pyproject.toml`
- **MCP Client**: Compatible MCP client (Claude Desktop, VS Code extensions, etc.)

## 🚀 Installation

### Option 1: Using pip (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd worktime-entry-mcp-remote-server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using uv (Modern Python Package Manager)

```bash
# Install uv if not already installed
pip install uv

# Clone and install
git clone <repository-url>
cd worktime-entry-mcp-remote-server
uv sync
```

### Option 3: Development Installation

```bash
# For development with editable install
pip install -e .
```

## ⚙️ Configuration

### Environment Variables

```bash
# Set default weekly hours (optional)
export DEFAULT_WEEKLY_HOURS=9.0
```

### User Preferences

The server automatically creates `config_user.json` for storing user preferences:

```json
{
  "default_weekly_hours": 40.0,
  "work_days_per_week": 5
}
```

**Configuration Options:**

- `default_weekly_hours`: Total work hours per week used as a fallback only when no work schedule is defined.
- `work_days_per_week`: Number of work days per week (default: 5). Used to infer daily default hours when no schedule blueprint exists.

The system calculates default daily hours as: `default_weekly_hours / work_days_per_week` when using fallback scheduling.

When a work schedule is defined, the schedule total becomes authoritative and `get_default_weekly_hours()` returns the combined weekly scheduled hours.

## 🎯 Usage

### Starting the Server

```bash
# Activate virtual environment
source .venv/bin/activate

# Start MCP server
python main.py
```

### MCP Client Integration

Configure your MCP client (e.g., Claude Desktop) to connect to this server:

```json
{
  "mcpServers": {
    "worktime": {
      "command": "python",
      "args": ["/path/to/worktime-entry-mcp-remote-server/main.py"]
    }
  }
}
```

## 📚 API Reference

### Time Entry Management

#### `add_time_entry(date, start, end, remark?, break_start?, break_end?)`

Add a new work time entry.

> Requires a defined work schedule via `set_work_schedule()` or fallback default weekly hours via `set_default_weekly_hours()` before logging entries.

**Parameters:**

- `date` (str): Date in YYYY-MM-DD format
- `start` (str): Start time in HH:MM format
- `end` (str): End time in HH:MM format
- `remark` (str, optional): Work description or notes
- `break_start` (str, optional): Break start time in HH:MM format
- `break_end` (str, optional): Break end time in HH:MM format

**Returns:** Entry details with ID and calculated hours

**Example:**

```python
# Add a regular work day
add_time_entry("2024-01-15", "09:00", "17:00", "Project development")

# Add entry with break
add_time_entry("2024-01-15", "09:00", "17:00", "Meetings", "12:00", "13:00")
```

#### `get_time_entries(month, year)`

Retrieve all time entries for a specific month.

**Parameters:**

- `month` (int): Month number (1-12)
- `year` (int): Year (e.g., 2024)

**Returns:** List of time entries with full details

#### `get_time_entry(entry_id)`

Get a specific time entry by ID.

**Parameters:**

- `entry_id` (int): Unique entry identifier

**Returns:** Complete entry details or null if not found

#### `update_time_entry(entry_id, date?, start?, end?, remark?, break_start?, break_end?)`

Update an existing time entry.

**Parameters:**

- `entry_id` (int): Entry to update
- Other parameters: Same as add_time_entry, all optional

**Returns:** Updated entry details

#### `delete_time_entry(entry_id)`

Remove a time entry.

**Parameters:**

- `entry_id` (int): Entry to delete

**Returns:** Deletion confirmation with affected row count

### Schedule Management

#### `set_work_schedule(day, hours)`

Set expected working hours for a specific weekday.

**Parameters:**

- `day` (str): Day name (Monday, Tuesday, etc.)
- `hours` (float): Expected hours for that day

**Example:**

```python
set_work_schedule("Monday", 8.0)
set_work_schedule("Friday", 6.0)
```

#### `get_work_schedule()`

Retrieve the current work schedule.

**Returns:** List of day-hours pairs

### Configuration

#### `set_default_weekly_hours(hours)`

Set the default weekly hours for new schedule entries.

**Parameters:**

- `hours` (float): Default hours value

#### `get_default_weekly_hours()`

Get the current default weekly hours setting.

**Returns:** Current default hours value

#### `set_work_days_per_week(days)`

Set the number of work days per week for calculating daily defaults.

**Parameters:**

- `days` (int): Number of work days per week (1-7)

**Example:**

```python
set_work_days_per_week(5)  # Monday to Friday
```

#### `get_work_days_per_week()`

Get the current number of work days per week setting.

**Returns:** Current work days per week value

### Reporting

#### `get_month_summary(month, year)`

Generate a comprehensive monthly summary with expected hours based on your work schedule.

**How Expected Hours is Calculated:**

Expected hours is calculated ONLY from days you have scheduled in `set_work_schedule()`. For example:

- If you set: Tuesday = 4.5 hours, Thursday = 4.5 hours
- And April 2026 has 4 Tuesdays and 5 Thursdays
- Then: Expected hours = (4 × 4.5) + (5 × 4.5) = 40.5 hours

Days without a schedule are NOT counted in expected hours.

**Parameters:**

- `month` (int): Month number (1-12)
- `year` (int): Year (e.g., 2024)

**Returns:**

```json
{
  "month": 4,
  "year": 2026,
  "entries": [
    {
      "id": 1,
      "date": "2026-04-02",
      "day": "Thursday",
      "start_time": "10:00",
      "end_time": "14:30",
      "hours": 4.5,
      "remark": "IKIM work"
    }
  ],
  "summary": {
    "total_worked_hours": 4.5,
    "expected_hours": 40.5,
    "overtime": -36.0,
    "entry_count": 1
  }
}
```

**Example Calculation:**

```
Weekly schedule: Tuesday 4.5hrs + Thursday 4.5hrs = 9 hours/week
April 2026: 4 Tuesdays × 4.5 + 5 Thursdays × 4.5 = 40.5 expected hours
If you worked 4.5 hours: overtime = 4.5 - 40.5 = -36 hours (36 hours short)
```

#### `export_month_excel(month, year)`

Export monthly timesheet to Excel format.

**Parameters:**

- `month` (int): Month to export
- `year` (int): Year to export

**Returns:** File path to generated Excel file

## 📊 Excel Export Format

The exported Excel file (`timesheet.xlsx`) contains:

| Date       | Weekday | Start | End   | Break Start | Break End | Hours | Remark       |
| ---------- | ------- | ----- | ----- | ----------- | --------- | ----- | ------------ |
| 2024-01-01 | Monday  | 09:00 | 17:00 | 12:00       | 13:00     | 8.0   | Project work |
| 2024-01-02 | Tuesday | 09:00 | 17:00 |             |           | 8.0   | Meetings     |
| ...        | ...     | ...   | ...   | ...         | ...       | ...   | ...          |

**Features:**

- Automatic calculation of working hours with break deduction
- Missing days marked as "MISSED"
- Professional formatting suitable for IKIM timesheets
- Summary totals at the bottom

## ✅ Data Validation

### Input Validation Rules

- **Date Format**: Must be YYYY-MM-DD (e.g., "2024-01-15")
- **Time Format**: Must be HH:MM (24-hour format, e.g., "09:00", "17:30")
- **Time Order**: Start time must be before end time
- **Break Validation**:
  - Break start must not be after break end (equal times allowed for "no break")
  - Break times must be within work hours
  - Equal break start/end times are treated as no break
- **Required Fields**: Date, start time, and end time are mandatory

### Error Messages

The server provides clear, actionable error messages:

```
ValueError: Invalid date format: 2024/01/15. Expected YYYY-MM-DD
ValueError: Start time must be before end time
ValueError: Break times must be within work hours
```

## 🔧 Troubleshooting

### Common Issues

**1. Import Errors**

```bash
ModuleNotFoundError: No module named 'fastmcp'
```

**Solution:** Install dependencies

```bash
pip install -r requirements.txt
```

**2. Database Errors**

```bash
sqlite3.OperationalError: no such table
```

**Solution:** Database initializes automatically on first run. Check file permissions.

**3. MCP Connection Issues**

- Ensure the server path is correct in your MCP client configuration
- Verify Python environment activation
- Check that the server starts without errors

**4. Excel Export Issues**

- Ensure `openpyxl` is installed
- Check write permissions in the working directory
- Verify the generated file path

### Debug Mode

Enable verbose logging by setting environment variables:

```bash
export PYTHONPATH=/path/to/project:$PYTHONPATH
python -c "import logging; logging.basicConfig(level=logging.DEBUG); import main"
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python -c "
from services import *
# Test validation
try:
    add_entry('invalid', '09:00', '17:00')
except ValueError as e:
    print('Validation working:', e)

# Test normal operation
entry = add_entry('2024-01-01', '09:00', '17:00', 'Test')
print('Entry added:', entry)
"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest

# Format code
black .
isort .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) for MCP protocol support
- Excel export powered by [openpyxl](https://openpyxl.readthedocs.io/)
- SQLite for reliable data persistence

## 📞 Support

For issues, questions, or contributions:

1. Check the [Issues](../../issues) page
2. Review the troubleshooting section above
3. Create a new issue with detailed information

---

**Happy time tracking! ⏰**
