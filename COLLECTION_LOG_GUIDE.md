# Data Collection Logging System

## Overview

The Airline Reliability Tracker now includes a comprehensive logging system that tracks all data collection and processing activities in the database. This allows you to:

- View historical collection activities
- Identify gaps in collected data
- Determine optimal timeframes for next collection
- Track success/failure rates
- Monitor performance metrics

## Database Table: `data_collection_log`

The system automatically logs all operations to the `data_collection_log` table with the following information:

| Column | Description |
|--------|-------------|
| `id` | Auto-increment primary key |
| `collection_date` | Timestamp when the operation was performed |
| `operation_type` | Type of operation: 'collect', 'process', or 'analyze' |
| `flight_direction` | 'D' for departures, 'A' for arrivals |
| `date_range_start` | Start date of the data range (YYYY-MM-DD) |
| `date_range_end` | End date of the data range (YYYY-MM-DD) |
| `records_collected` | Number of records collected from API |
| `records_processed` | Number of records processed |
| `status` | Operation status: 'success', 'partial', or 'failed' |
| `error_message` | Error message if operation failed |
| `execution_time_seconds` | Time taken to complete the operation |
| `api_pages_fetched` | Number of API pages fetched (if applicable) |
| `notes` | Additional notes about the operation |

## Viewing the Collection Log

### Command Line Script

Run the log viewer script to see collection history and get recommendations:

```bash
python view_collection_log.py
```

This will display:

- **Collection Summary**: Total operations, success/failure counts, total records
- **Recent Activities**: Last 20 collection/processing operations
- **Date Coverage Analysis**: Earliest and latest data collected
- **Recommendations**: Suggested next collection timeframe
- **Gap Analysis**: Missing dates in the collected data

### Example Output

```
================================================================================
DATA COLLECTION LOG
================================================================================
Current time: 2026-01-24 09:00:00

COLLECTION SUMMARY:
--------------------------------------------------------------------------------
Total Operations: 12
  ✓ Successful: 11
  ✗ Failed: 1
Total Records Collected: 15,234

RECENT COLLECTION ACTIVITIES (Last 20):
--------------------------------------------------------------------------------
Date/Time            Operation  Type       Date Range                Records    Status
--------------------------------------------------------------------------------
2026-01-23 21:16     collect    Departures 2026-01-23 to 2026-01-23  795        ✓ success
2026-01-23 21:15     collect    Arrivals   2026-01-23 to 2026-01-23  239        ✓ success
2026-01-22 15:30     process    Departures 2026-01-22 to 2026-01-22  727        ✓ success

DATE COVERAGE ANALYSIS:
--------------------------------------------------------------------------------
Earliest data collected: 2026-01-15
Latest data collected: 2026-01-23
Current date: 2026-01-24
Days behind: 1

================================================================================
RECOMMENDATIONS FOR NEXT COLLECTION:
================================================================================

✓ Data is 1 day behind

Recommended action:
  Collect yesterday's data

  Command:
  python main.py collect --days-back 1
```

## Programmatic Access

You can also query the log programmatically in your Python scripts:

```python
from database import DatabaseManager

with DatabaseManager() as db:
    # Get all collection logs
    log_df = db.get_collection_log(limit=100)
    
    # Filter by date range
    log_df = db.get_collection_log(
        start_date='2026-01-01',
        end_date='2026-01-31'
    )
    
    # Filter by operation type
    log_df = db.get_collection_log(
        operation_type='collect',
        limit=50
    )
```

## Automatic Logging

The logging system is integrated into the main application:

### Data Collection (`main.py collect`)

When you run:

```bash
python main.py collect --days-back 7
```

The system automatically logs:

- Date range collected
- Number of records retrieved
- Execution time
- Success/failure status
- Any errors encountered

### Data Processing (`main.py process`)

When you run:

```bash
python main.py process departures 2026-01-15_to_2026-01-22
```

The system automatically logs:

- Date range processed
- Number of records processed
- Execution time
- Database save status
- Any errors encountered

## Determining Next Collection Timeframe

### Method 1: Use the Log Viewer (Recommended)

```bash
python view_collection_log.py
```

The script will analyze your collection history and provide specific recommendations.

### Method 2: Query the Database Directly

```python
from database import DatabaseManager

with DatabaseManager() as db:
    # Get the latest collection date
    log_df = db.get_collection_log(operation_type='collect', limit=1)
    
    if not log_df.empty:
        latest_end = log_df.iloc[0]['date_range_end']
        print(f"Latest data collected up to: {latest_end}")
        print(f"Next collection should start from: {latest_end + 1 day}")
```

### Method 3: Check Flight Data Directly

```python
from database import DatabaseManager

with DatabaseManager() as db:
    cursor = db.connection.cursor()
    cursor.execute("""
        SELECT MAX(schedule_date) as latest_date
        FROM flights
    """)
    result = cursor.fetchone()
    print(f"Latest flight data: {result['latest_date']}")
```

## Best Practices

1. **Regular Collections**: Run daily collections to keep data current

   ```bash
   python main.py collect --days-back 1
   ```

2. **Check Logs Before Collecting**: Always check the log to avoid duplicate collections

   ```bash
   python view_collection_log.py
   ```

3. **Monitor for Failures**: Review failed operations in the log and retry if needed

4. **Fill Gaps**: If gaps are detected, collect data for specific date ranges

   ```bash
   python main.py collect --days-back 5 --days-forward 0
   ```

5. **Process After Collection**: Always process collected data

   ```bash
   python main.py process departures 2026-01-23_to_2026-01-23
   python main.py process arrivals 2026-01-23_to_2026-01-23
   ```

## Troubleshooting

### Log Table Doesn't Exist

If you get an error about the log table not existing, create it:

```bash
python -c "from database import DatabaseManager; db = DatabaseManager(); db.connect(); db.create_tables(); db.disconnect()"
```

Or simply run any collection/processing command, which will create tables automatically.

### No Log Entries

If the log is empty, it means:

1. The log table was just created
2. No data has been collected with the new logging system

Start collecting data to populate the log:

```bash
python main.py collect --days-back 7
```

### Database Connection Issues

If you can't connect to the database, check:

1. Your `.env` file has correct credentials
2. SSH tunnel can be established
3. MariaDB server is running

Test the connection:

```bash
python main.py db-test
```

## Summary

The logging system provides complete visibility into your data collection pipeline:

- ✅ **Automatic**: Logs every collection and processing operation
- ✅ **Comprehensive**: Tracks timing, record counts, and errors
- ✅ **Actionable**: Provides specific recommendations for next steps
- ✅ **Queryable**: Easy to access via scripts or programmatically
- ✅ **Persistent**: Stored in the database for historical analysis

Use `python view_collection_log.py` to get started!
