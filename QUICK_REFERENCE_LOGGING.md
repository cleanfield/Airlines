# Quick Reference: Data Collection Logging

## What Was Implemented

✅ **Database Logging Table** (`data_collection_log`)

- Tracks all collection and processing operations
- Records timestamps, date ranges, record counts, execution times, and status
- Automatically logs every `collect`, `process`, and `analyze` operation

✅ **Enhanced Main Application** (`main.py`)

- `collect_data()` now logs collection activities with timing and error tracking
- `process_data()` now logs processing activities with success/failure status
- All operations automatically create log entries in the database

✅ **Log Viewer Script** (`view_collection_log.py`)

- Displays collection history from database
- Shows date coverage analysis
- Detects gaps in collected data
- Provides specific recommendations for next collection

✅ **Local File Analyzer** (`analyze_local_data.py`)

- Analyzes local JSON files when database is unavailable
- Shows file sizes, record counts, and date ranges
- Provides recommendations based on local data

✅ **Documentation**

- `COLLECTION_LOG_GUIDE.md` - Complete guide to the logging system
- `COLLECTION_STATUS.md` - Current status and recommendations

## How to Use

### Check What Data You Have

**Option 1: Using the database log (recommended)**

```bash
python view_collection_log.py
```

**Option 2: Using local files**

```bash
python analyze_local_data.py
```

**Option 3: Check the summary**

```bash
# Open COLLECTION_STATUS.md
```

### Current Status

Based on your local files:

- **Latest data**: 2026-01-23
- **Current date**: 2026-01-24
- **Status**: 1 day behind

### Recommended Next Action

```bash
# Collect yesterday's data
python main.py collect --days-back 1

# This will automatically:
# 1. Collect flight data for 2026-01-23
# 2. Log the collection to the database
# 3. Save raw data to JSON files
```

Then process it:

```bash
python main.py process departures 2026-01-23_to_2026-01-23
python main.py process arrivals 2026-01-23_to_2026-01-23
```

Or do everything in one command:

```bash
python main.py analyze --days-back 1
```

## Key Files Created/Modified

### New Files

- `view_collection_log.py` - View database collection log
- `analyze_local_data.py` - Analyze local data files
- `check_collection_log.py` - Original diagnostic script
- `COLLECTION_LOG_GUIDE.md` - Complete documentation
- `COLLECTION_STATUS.md` - Current status summary
- `QUICK_REFERENCE_LOGGING.md` - This file

### Modified Files

- `database.py` - Added `data_collection_log` table and logging methods
- `main.py` - Enhanced `collect_data()` and `process_data()` with logging

## Database Schema

```sql
CREATE TABLE data_collection_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    operation_type VARCHAR(20) NOT NULL,  -- 'collect', 'process', 'analyze'
    flight_direction CHAR(1),              -- 'D' or 'A'
    date_range_start DATE NOT NULL,
    date_range_end DATE NOT NULL,
    records_collected INT DEFAULT 0,
    records_processed INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'success',  -- 'success', 'partial', 'failed'
    error_message TEXT,
    execution_time_seconds DECIMAL(10, 2),
    api_pages_fetched INT,
    notes TEXT
);
```

## Programmatic Access

```python
from database import DatabaseManager

# View collection log
with DatabaseManager() as db:
    log_df = db.get_collection_log(limit=50)
    print(log_df)

# Log a custom operation
with DatabaseManager() as db:
    db.log_collection(
        operation_type='collect',
        flight_direction='D',
        date_range_start='2026-01-23',
        date_range_end='2026-01-23',
        records_collected=795,
        status='success',
        execution_time=45.2
    )
```

## Benefits

1. **Historical Tracking**: See all past collection activities
2. **Gap Detection**: Automatically identify missing dates
3. **Performance Monitoring**: Track execution times and success rates
4. **Smart Recommendations**: Get specific commands for next collection
5. **Error Tracking**: Log and review failed operations
6. **Audit Trail**: Complete record of all data operations

## Next Steps

1. **Collect current data**:

   ```bash
   python main.py collect --days-back 1
   ```

2. **View the log** (once database is accessible):

   ```bash
   python view_collection_log.py
   ```

3. **Set up daily automation** (optional):
   - Schedule daily collection at a specific time
   - Automatically process and generate reports

---

**Summary**: The logging system is now fully integrated. Every data collection and processing operation will be automatically logged to the database, giving you complete visibility into your data pipeline.
