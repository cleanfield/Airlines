# MariaDB Connection Guide

This guide explains how to connect to MariaDB using Python in the Airlines project.

## Overview

The project uses **PyMySQL** to connect to a MariaDB database through an **SSH tunnel** for secure remote access.

## Environment Variables

Configure these variables in your `.env` file:

```env
# SSH Connection (for secure tunnel)
MARIA_SERVER=<server_ip>          # SSH server hostname/IP
MARIA_SSH_USER=flights               # SSH username
MARIA_ID_ED25519="C:\Projects\Airlines\id_ed25519"  # SSH private key path
MARIA_ID_ED25519_PUB="C:\Projects\Airlines\id_ed25519.pub"  # SSH public key

# Database Connection
MARIA_DB=flights                     # Database name
MARIA_DB_USER=flights                # Database username
MARIA_DB_PASSWORD=<password>         # Database password
```

## Connection Architecture

```
Your App (Python)
    ↓
SSH Tunnel (sshtunnel library)
    ↓ (encrypted connection via port 22)
SSH Server (<server_ip>)
    ↓ (local connection to 127.0.0.1:3306)
MariaDB Server
```

## Using the DatabaseManager Class

### Method 1: Context Manager (Recommended)

The context manager automatically handles connection setup and cleanup:

```python
from database import DatabaseManager

# Automatic connection and cleanup
with DatabaseManager() as db:
    # Connection is established here
    
    # Execute queries
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM flights LIMIT 10")
        results = cursor.fetchall()
        
        for row in results:
            print(row)
    
    # Connection automatically closes when exiting the 'with' block
```

### Method 2: Manual Connection

For more control over connection lifecycle:

```python
from database import DatabaseManager

db = DatabaseManager()

try:
    # Manually establish connection
    db.connect()
    
    # Do your work
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM flights")
        result = cursor.fetchone()
        print(f"Total flights: {result['count']}")
        
finally:
    # Always disconnect
    db.disconnect()
```

## Common Operations

### 1. Create Tables

```python
with DatabaseManager() as db:
    db.create_tables()
    print("Tables created successfully!")
```

### 2. Insert Flight Data

```python
import pandas as pd
from database import DatabaseManager

# Prepare flight data
flight_data = pd.DataFrame([{
    'flight_id': 123456,
    'flight_number': 'KL1234',
    'airline_code': 'KL',
    'flight_direction': 'D',
    'schedule_date': '2026-01-23',
    'schedule_time': '10:30:00',
    'actual_time': '2026-01-23 10:35:00',
    'estimated_time': '2026-01-23 10:35:00',
    'delay_minutes': 5.0,
    'on_time': True,
    'flight_status': 'DEP',
    'destinations': 'AMS',
    'aircraft_type': 'B737',
    'terminal': '3',
    'gate': 'D5',
    'baggage_claim': None
}])

# Save to database
with DatabaseManager() as db:
    rows_affected = db.save_flights(flight_data)
    print(f"Saved {rows_affected} flights")
```

### 3. Query Flight Data

```python
with DatabaseManager() as db:
    # Get flights for a specific date range
    df = db.get_flights(
        start_date='2026-01-20',
        end_date='2026-01-23',
        airline_code='KL'  # Optional filter
    )
    
    print(f"Retrieved {len(df)} flights")
    print(df.head())
```

### 4. Save Airline Statistics

```python
import pandas as pd

stats_data = pd.DataFrame([{
    'airline_code': 'KL',
    'total_flights': 100,
    'on_time_flights': 85,
    'avg_delay_minutes': 5.2,
    'median_delay_minutes': 3.0,
    'std_delay_minutes': 8.5,
    'min_delay_minutes': -10.0,
    'max_delay_minutes': 45.0,
    'on_time_percentage': 85.0,
    'reliability_score': 84.48
}])

with DatabaseManager() as db:
    rows_affected = db.save_airline_statistics(
        df=stats_data,
        date_range_start='2026-01-01',
        date_range_end='2026-01-23',
        flight_direction='D'
    )
    print(f"Saved {rows_affected} statistics records")
```

### 5. Get Airline Statistics

```python
with DatabaseManager() as db:
    stats_df = db.get_airline_statistics(
        start_date='2026-01-01',
        end_date='2026-01-23'
    )
    
    print("Top 10 Airlines by Reliability:")
    print(stats_df.head(10))
```

### 6. Custom Queries

```python
with DatabaseManager() as db:
    with db.connection.cursor() as cursor:
        # Execute custom SQL
        cursor.execute("""
            SELECT 
                airline_code,
                COUNT(*) as total_flights,
                AVG(delay_minutes) as avg_delay
            FROM flights
            WHERE schedule_date >= '2026-01-01'
            GROUP BY airline_code
            ORDER BY avg_delay ASC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        for row in results:
            print(f"{row['airline_code']}: {row['total_flights']} flights, "
                  f"avg delay: {row['avg_delay']:.2f} min")
```

## Database Schema

### Flights Table

```sql
CREATE TABLE flights (
    id BIGINT PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL,
    airline_code VARCHAR(10),
    flight_direction CHAR(1),
    schedule_date DATE,
    schedule_time TIME,
    actual_time DATETIME,
    estimated_time DATETIME,
    delay_minutes DECIMAL(10, 2),
    on_time BOOLEAN,
    flight_status VARCHAR(20),
    destinations VARCHAR(255),
    aircraft_type VARCHAR(10),
    terminal VARCHAR(10),
    gate VARCHAR(10),
    baggage_claim VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_airline_code (airline_code),
    INDEX idx_schedule_date (schedule_date),
    INDEX idx_flight_direction (flight_direction)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Airline Statistics Table

```sql
CREATE TABLE airline_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    airline_code VARCHAR(10) NOT NULL,
    date_range_start DATE NOT NULL,
    date_range_end DATE NOT NULL,
    flight_direction CHAR(1),
    total_flights INT,
    on_time_flights INT,
    avg_delay_minutes DECIMAL(10, 2),
    median_delay_minutes DECIMAL(10, 2),
    std_delay_minutes DECIMAL(10, 2),
    min_delay_minutes DECIMAL(10, 2),
    max_delay_minutes DECIMAL(10, 2),
    on_time_percentage DECIMAL(5, 2),
    reliability_score DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_airline_stats (airline_code, date_range_start, date_range_end, flight_direction),
    INDEX idx_airline_code (airline_code),
    INDEX idx_date_range (date_range_start, date_range_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## Testing the Connection

Run the test script to verify your connection:

```bash
python database.py
```

Expected output:

```
=== Database Connection Test ===

Establishing SSH tunnel to <server_ip>...
Loading SSH key from: C:\Projects\Airlines\id_ed25519
✓ Loaded Ed25519 key
SSH tunnel established on local port XXXXX
Connecting to MariaDB database 'flights'...
Database connection established successfully!

Creating tables...
Database tables created/verified successfully

Database test completed successfully!
```

## Troubleshooting

### Issue: "No module named 'pymysql'"

**Solution:** Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Issue: "SSH key not found"

**Solution:** Verify the SSH key path in `.env` file

```bash
# Check if file exists
dir "C:\Projects\Airlines\id_ed25519"
```

### Issue: "Connection timeout"

**Solution:**

- Check if SSH server is accessible
- Verify firewall settings
- Ensure SSH port 22 is open

### Issue: "Authentication failed"

**Solution:**

- Verify `MARIA_SSH_USER` is correct
- Ensure SSH key has proper permissions
- Check if public key is added to server's `~/.ssh/authorized_keys`

### Issue: "Database access denied"

**Solution:**

- Verify `MARIA_DB_USER` and `MARIA_DB_PASSWORD`
- Ensure database user has proper permissions
- Check if database exists

## Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use SSH keys** - More secure than passwords
3. **Limit database permissions** - Grant only necessary privileges
4. **Use strong passwords** - For database accounts
5. **Keep dependencies updated** - Regularly update PyMySQL and other libraries

## Performance Tips

1. **Use connection pooling** for high-traffic applications
2. **Close connections** when done (automatically handled by context manager)
3. **Use batch inserts** for multiple records
4. **Create appropriate indexes** on frequently queried columns
5. **Use prepared statements** to prevent SQL injection

## Additional Resources

- [PyMySQL Documentation](https://pymysql.readthedocs.io/)
- [MariaDB Documentation](https://mariadb.com/kb/en/documentation/)
- [SSH Tunnel Documentation](https://sshtunnel.readthedocs.io/)

## Example Scripts

See these files for complete examples:

- `database.py` - Main DatabaseManager class
- `mariadb_connection_example.py` - Comprehensive examples
- `simple_mariadb_example.py` - Basic PyMySQL usage
