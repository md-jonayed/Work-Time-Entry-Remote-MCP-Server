# WorkTime Entry MCP Remote Server

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)
[![Security](https://img.shields.io/badge/Security-User%20Isolated-brightgreen.svg)]()

A comprehensive **Model Context Protocol (MCP)** server for professional work time tracking, designed to integrate seamlessly with AI assistants and automation tools. Track work hours, manage schedules, calculate overtime, and generate detailed Excel reports with enterprise-grade validation, error handling, and **user data isolation**.

## ⚠️ Security & Data Isolation

**This version includes critical security enhancements:**

- ✅ **User Data Isolation**: Every tool now requires a `user_id` parameter. Users can only access their own data.
- ✅ **User Registration**: All users must be registered via `register_user_tool()` before using other features.
- ✅ **Database Constraints**: Foreign key relationships and UNIQUE constraints enforce data integrity.
- ✅ **SQL Injection Protection**: All queries use parameterized statements (no string concatenation).
- ✅ **Timestamps**: All entries include `created_at` and `updated_at` timestamps for audit trails.

> **Important**: The previous version had a critical flaw where any user could access all users' data due to missing user_id fields. This has been completely fixed.

## 🌟 Key Features

### 📊 Time Tracking

- **User-Isolated Data**: Each user's data is completely isolated - users can only view/modify their own entries
- **Precise Time Entry**: Record work hours with start/end times and optional break periods
- **Smart Break Handling**: Equal break start/end times indicate "no break" for easy updates
- **Flexible Scheduling**: Define a weekly schedule as the primary work blueprint
- **Expected Hours from Schedule**: Expected monthly hours are calculated only from scheduled weekdays
- **Monthly Summaries**: Comprehensive reports with worked hours, expected hours, and overtime

### 📈 Reporting & Export

- **User-Specific Excel Export**: Generate professional IKIM-style Excel timesheets (user data only)
- **Data Integrity**: Automatic handling of missing days and data validation
- **Entry IDs**: All entries include unique IDs for easy updates and deletions
- **Customizable Reports**: Export specific months with detailed breakdowns
- **Audit Trail**: Timestamps on all operations for compliance

### 🔧 Enterprise Features

- **Robust Validation**: Comprehensive input validation with clear error messages
- **Database Persistence**: SQLite-based storage with automatic schema management and foreign keys
- **Data Isolation**: Per-user configuration with UNIQUE constraints preventing data leakage
- **Flexible Work Hours**: Configure weekly work hours and work days per user for accurate calculations
- **Asynchronous Operations**: Built with async/await for high-performance concurrent database operations using aiosqlite
- **Thread Safety**: Optimized for MCP's single-threaded execution model

### 🤖 **MCP Integration**

- **AI Assistant Ready**: Full MCP protocol compliance for seamless AI integration
- **Tool-Based API**: 12 specialized tools for comprehensive time tracking operations
- **Type Safety**: Full type hints and structured data exchange
- **Error Handling**: Graceful error handling with detailed error responses

## 🏗️ Architecture

```
WorkTime Entry MCP Server
├── main.py          # MCP server setup and tool definitions
├── services.py      # Business logic and data operations with user isolation
├── db.py           # Database connection and schema with user support
├── utils.py        # Utility functions and validation
├── excel_export.py # Excel report generation (user-specific)
└── config.py       # Configuration management
```

### Database Schema

- **`users`**: User registration and metadata
- **`time_entries`**: Work time records with user_id isolation and timestamps
- **`work_schedule`**: Per-user weekly schedule configuration
- **Automatic Migrations**: Schema updates handled transparently
- **Foreign Keys**: Enforced referential integrity with CASCADE delete

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
# Set database path for persistent storage (optional, defaults to /tmp/work_time.db)
export DB_PATH=/path/to/your/database.db

# Set config file path for user preferences (optional, defaults to project directory)
export CONFIG_PATH=/path/to/config_user.json
```

## ☁️ Cloud Deployment

### FastMCP Cloud

This server is designed to work with FastMCP cloud deployments. For persistent data storage in cloud environments:

1. **Set Database Path**: Configure the `DB_PATH` environment variable to a writable location:

   ```bash
   export DB_PATH=/persistent/storage/work_time.db
   ```

2. **Volume Mounting**: If deploying in containers, mount a persistent volume to the database path.

3. **Default Behavior**: If `DB_PATH` is not set, the server uses `/tmp/work_time.db` which provides temporary storage that may be lost on container restarts.

### Data Persistence

- **Local Development**: Database is stored in the project directory
- **Cloud Deployment**: Use environment variables to configure persistent storage paths
- **Backup**: Regularly backup your database file for data safety

## 📚 API Reference

### User Management

#### `register_user_tool(user_id)`

Register a new user for time tracking.

> **IMPORTANT**: All users must be registered before using other tools. Each MCP client/user should have a unique `user_id`.

**Parameters:**

- `user_id` (str): Unique identifier for the user (email, username, etc.)

**Returns:** Registration confirmation

**Example:**

```python
register_user_tool("alice@company.com")
register_user_tool("bob@company.com")
```

### Time Entry Management

#### `add_time_entry(user_id, date, start, end, remark?, break_start?, break_end?)`

Add a new work time entry for a specific user.

> Requires a defined work schedule via `set_work_schedule()` before logging entries.

**Parameters:**

- `user_id` (str): User identifier (must be registered)
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
add_time_entry("alice@company.com", "2024-01-15", "09:00", "17:00", "Project development")

# Add entry with break
add_time_entry("alice@company.com", "2024-01-15", "09:00", "17:00", "Meetings", "12:00", "13:00")
```

**Data Isolation:** Alice can only access her own entries, not Bob's.

#### `get_time_entries(user_id, month, year)`

Retrieve all time entries for a specific user and month.

**Parameters:**

- `user_id` (str): User identifier
- `month` (int): Month number (1-12)
- `year` (int): Year (e.g., 2024)

**Returns:** List of user's time entries for that month

**Data Isolation:** Only returns entries belonging to the specified `user_id`.

#### `get_time_entry(user_id, entry_id)`

Get a specific time entry by ID.

**Parameters:**

- `user_id` (str): User identifier
- `entry_id` (int): Unique entry identifier

**Returns:** Complete entry details or error if not found or not owned by user

**Data Isolation:** Returns error if the entry doesn't belong to `user_id`.

#### `update_time_entry(user_id, entry_id, date?, start?, end?, remark?, break_start?, break_end?)`

Update an existing time entry.

**Parameters:**

- `user_id` (str): User identifier
- `entry_id` (int): Entry to update
- Other parameters: Same as add_time_entry, all optional

**Returns:** Updated entry details

**Data Isolation:** Can only update entries owned by `user_id`.

#### `delete_time_entry(user_id, entry_id)`

Remove a time entry.

**Parameters:**

- `user_id` (str): User identifier
- `entry_id` (int): Entry to delete

**Returns:** Deletion confirmation

**Data Isolation:** Can only delete own entries.

### Schedule Management

#### `set_work_schedule(user_id, day, hours)`

Set expected working hours for a specific weekday for a user.

**Parameters:**

- `user_id` (str): User identifier
- `day` (str): Day name (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
- `hours` (float): Expected hours for that day

**Example:**

```python
set_work_schedule("alice@company.com", "Monday", 8.0)
set_work_schedule("alice@company.com", "Friday", 6.0)
```

**Data Isolation:** Each user has their own schedule.

#### `get_work_schedule(user_id)`

Retrieve the work schedule for a specific user.

**Parameters:**

- `user_id` (str): User identifier

**Returns:** List of day-hours pairs for that user

**Data Isolation:** Only returns the user's schedule.

### Reporting & Export

#### `get_month_summary(user_id, month, year)`

Get a comprehensive monthly summary with worked vs expected hours.

**Parameters:**

- `user_id` (str): User identifier
- `month` (int): Month number (1-12)
- `year` (int): Year

**Returns:** Summary with:

- `worked_hours`: Total hours logged
- `expected_hours`: Total hours from schedule
- `overtime`: Positive if over expected, negative if under
- `worked_days`: Number of days with entries
- `expected_days`: Number of days in schedule for the month
- `entries`: Detailed list of entries

**Example Response:**

```json
{
  "user_id": "alice@company.com",
  "month": 1,
  "year": 2024,
  "worked_hours": 165.5,
  "expected_hours": 160.0,
  "overtime": 5.5,
  "worked_days": 22,
  "expected_days": 22,
  "entries": [...]
}
```

**Data Isolation:** Only returns the user's data.

#### `export_month_excel(user_id, month, year)`

Export a user's timesheet to professional IKIM-style Excel.

**Parameters:**

- `user_id` (str): User identifier
- `month` (int): Month number
- `year` (int): Year

**Returns:** File path with user data extracted to Excel

**Example:**

```python
export_month_excel("alice@company.com", 1, 2024)
# Generates: /tmp/timesheet_alice@company.com_2024-01.xlsx
```

**Data Isolation:** Excel file contains only the specified user's data.

## 🔐 Security Best Practices

1. **User Identification**: Ensure your MCP client/AI system correctly identifies the current user and passes the `user_id` consistently.

2. **Unique User IDs**: Use globally unique identifiers (emails, UUIDs) for `user_id` to prevent collisions.

3. **Database Backup**: Implement regular database backups outside of temporary storage directories.

4. **Access Control**: If deploying as a service, implement authentication to ensure only authorized clients can connect.

5. **Audit Logs**: Enable timestamp tracking (built-in) to monitor who modified which entries and when.

## 📝 Migration Guide (from v1.0)

If you're upgrading from the previous version without user isolation:

### Database Migration

The system automatically handles schema migration:

1. A `users` table is created
2. `user_id` columns are added to existing tables
3. Existing data is assigned to a `default_user`

### Code Changes

All function calls now require `user_id` as the first parameter:

**Before (❌ insecure):**

```python
add_time_entry("2024-01-15", "09:00", "17:00")
get_time_entries(1, 2024)
```

**After (✅ secure):**

```python
add_time_entry("alice@company.com", "2024-01-15", "09:00", "17:00")
get_time_entries("alice@company.com", 1, 2024)
```

First, register all users:

```python
register_user_tool("alice@company.com")
register_user_tool("bob@company.com")
```

## 🐛 Fixes in This Version

- ✅ **Critical**: Added user_id to all database operations for data isolation
- ✅ **Critical**: Removed cross-user data access vulnerability
- ✅ **Critical**: Updated all tools to require user_id parameter
- ✅ **Enhancement**: Added user management and registration
- ✅ **Enhancement**: Added audit timestamps to all entries
- ✅ **Enhancement**: Implemented database foreign keys and constraints
- ✅ **Bug Fix**: Implemented missing `month_summary()` function
- ✅ **Bug Fix**: Added missing `asyncio` import
- ✅ **Enhancement**: Improved Excel export with user information
- ✅ **Enhancement**: Added per-user schedule isolation

## 📞 Support

For issues, questions, or security concerns, please report them appropriately.

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
