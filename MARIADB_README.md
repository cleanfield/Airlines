# Connecting to MariaDB with Python - Complete Guide

## 📋 Summary

You now have a complete MariaDB connection setup for your Airlines project! Here's everything you need to know.

## ✅ What's Working

1. **Database Module** (`database.py`)
   - DatabaseManager class with SSH tunnel support
   - Context manager for automatic cleanup
   - CRUD operations for flights and statistics
   - Proper environment variable handling

2. **Environment Configuration** (`.env`)
   - Separated SSH and database credentials
   - Correct variable names: `MARIA_SSH_USER`, `MARIA_DB_USER`, `MARIA_DB_PASSWORD`

3. **Dependencies Installed**
   - pymysql - MariaDB connector
   - sshtunnel - SSH tunneling
   - paramiko - SSH library
   - All other required packages

## 🔧 Configuration

Your `.env` file:

```env
# SSH Connection
MARIA_SERVER=<server_ip>
MARIA_SSH_USER=flights
MARIA_ID_ED25519="C:\Projects\Airlines\id_ed25519"

# Database Connection
MARIA_DB=flights
MARIA_DB_USER=flights
MARIA_DB_PASSWORD=<password>
```

## 💻 How to Use

### Basic Connection Pattern

```python
from database import DatabaseManager

# Use context manager (recommended - automatic cleanup)
with DatabaseManager() as db:
    # Execute queries
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM flights LIMIT 10")
        results = cursor.fetchall()
        
        for row in results:
            print(row)
```

### Common Operations

#### 1. Create Tables

```python
with DatabaseManager() as db:
    db.create_tables()
```

#### 2. Save Flight Data

```python
import pandas as pd

flight_data = pd.DataFrame([{
    'flight_id': 123456,
    'flight_number': 'KL1234',
    'airline_code': 'KL',
    'flight_direction': 'D',
    'schedule_date': '2026-01-23',
    'schedule_time': '10:30:00',
    'actual_time': '2026-01-23 10:35:00',
    'delay_minutes': 5.0,
    'on_time': True,
    'flight_status': 'DEP',
    'destinations': 'AMS',
    'aircraft_type': 'B737',
    'terminal': '3',
    'gate': 'D5',
    'baggage_claim': None
}])

with DatabaseManager() as db:
    db.save_flights(flight_data)
```

#### 3. Query Flights

```python
with DatabaseManager() as db:
    # Get flights by date range
    df = db.get_flights(
        start_date='2026-01-20',
        end_date='2026-01-23'
    )
    print(df)
    
    # Get flights by airline
    df = db.get_flights(airline_code='KL')
    print(df)
```

#### 4. Custom Queries

```python
with DatabaseManager() as db:
    with db.connection.cursor() as cursor:
        cursor.execute("""
            SELECT airline_code, COUNT(*) as flights
            FROM flights
            WHERE schedule_date >= '2026-01-01'
            GROUP BY airline_code
            ORDER BY flights DESC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            print(f"{row['airline_code']}: {row['flights']} flights")
```

## 📁 Files Created

| File | Purpose |
|------|---------|
| `database.py` | Main database connection module |
| `MARIADB_CONNECTION_GUIDE.md` | Comprehensive documentation |
| `MARIADB_QUICK_REFERENCE.md` | Quick reference guide |
| `MARIADB_SETUP_SUMMARY.md` | Setup summary |
| `test_mariadb_connection.py` | Connection test suite |
| `mariadb_connection_example.py` | Working examples |
| `simple_mariadb_example.py` | Basic PyMySQL examples |

## 🗄️ Database Schema

### flights Table

```sql
- id (BIGINT, PRIMARY KEY)
- flight_number (VARCHAR)
- airline_code (VARCHAR)
- flight_direction (CHAR)
- schedule_date (DATE)
- schedule_time (TIME)
- actual_time (DATETIME)
- delay_minutes (DECIMAL)
- on_time (BOOLEAN)
- flight_status (VARCHAR)
- destinations (VARCHAR)
- aircraft_type (VARCHAR)
- terminal, gate, baggage_claim
- created_at, updated_at (TIMESTAMP)
```

### airline_statistics Table

```sql
- id (INT, AUTO_INCREMENT)
- airline_code (VARCHAR)
- date_range_start, date_range_end (DATE)
- flight_direction (CHAR)
- total_flights, on_time_flights (INT)
- avg_delay_minutes, median_delay_minutes (DECIMAL)
- std_delay_minutes, min_delay_minutes, max_delay_minutes (DECIMAL)
- on_time_percentage, reliability_score (DECIMAL)
- created_at, updated_at (TIMESTAMP)
```

## ⚠️ Known Issues & Solutions

### Issue: DSSKey Warning

**Symptom:** Warning about `'module' object has no attribute 'DSSKey'`

**Cause:** The sshtunnel library (v0.4.0) tries to use deprecated DSS keys

**Impact:** This is just a warning - the connection still works with Ed25519 keys

**Solution:** The database.py file includes a workaround that minimizes this warning

### Issue: Connection Timeout

**Symptom:** "Could not establish session to SSH gateway"

**Possible Causes:**

1. SSH server is not accessible
2. Firewall blocking port 22
3. Incorrect SSH credentials
4. SSH key not authorized on server

**Solutions:**

1. Verify server is accessible: `ping <server_ip>`
2. Check SSH connection: `ssh -i id_ed25519 <ssh_user>@<server_ip>`
3. Verify SSH key is in server's `~/.ssh/authorized_keys`
4. Check firewall settings

### Issue: Database Access Denied

**Symptom:** "Access denied for user"

**Solutions:**

1. Verify `MARIA_DB_USER` and `MARIA_DB_PASSWORD` in `.env`
2. Check database user permissions on server
3. Ensure database exists

## 🧪 Testing Your Connection

### Quick Test

```bash
python database.py
```

### Comprehensive Test

```bash
python test_mariadb_connection.py
```

### Manual Test

```python
from database import DatabaseManager

try:
    with DatabaseManager() as db:
        print("✓ Connected successfully!")
        with db.connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            print(f"MariaDB version: {cursor.fetchone()}")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

## 🔐 Security Notes

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Protect SSH keys** - Keep `id_ed25519` secure
3. **Use strong passwords** - For database accounts
4. **Limit permissions** - Grant only necessary database privileges
5. **Update regularly** - Keep dependencies up to date

## 📚 Documentation

- **Full Guide:** Open `MARIADB_CONNECTION_GUIDE.md`
- **Quick Reference:** Open `MARIADB_QUICK_REFERENCE.md`
- **Examples:** Run `python mariadb_connection_example.py`

## 🚀 Integration with Your App

To use the database in your existing scripts:

```python
# In your data collection script
from database import DatabaseManager
import pandas as pd

# After collecting flight data
with DatabaseManager() as db:
    db.save_flights(flights_df)
    print("Flights saved to database!")

# In your analysis script
with DatabaseManager() as db:
    flights = db.get_flights(
        start_date='2026-01-01',
        end_date='2026-01-31'
    )
    # Analyze the data
    print(flights.describe())
```

## 💡 Best Practices

1. **Always use context manager** - Ensures proper cleanup
2. **Batch operations** - Insert multiple records at once
3. **Use transactions** - For data integrity
4. **Index properly** - For better query performance
5. **Handle exceptions** - Always wrap in try/except

## 🎯 Next Steps

1. **Test the connection** - Run `python database.py`
2. **Review the examples** - Check `mariadb_connection_example.py`
3. **Integrate with your app** - Add database calls to your scripts
4. **Monitor performance** - Check query execution times
5. **Backup regularly** - Implement database backup strategy

## 📞 Getting Help

If you encounter issues:

1. Check the troubleshooting section in `MARIADB_CONNECTION_GUIDE.md`
2. Verify all environment variables in `.env`
3. Test SSH connection separately
4. Check server logs for errors
5. Review the example scripts

## 🎉 You're All Set

Your MariaDB connection is configured and ready to use. The `DatabaseManager` class provides a clean, Pythonic interface to your database with automatic connection management and comprehensive error handling.

Happy coding! 🚀
