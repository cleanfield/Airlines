# MariaDB Quick Reference

## Quick Start

```python
from database import DatabaseManager

# Connect and query
with DatabaseManager() as db:
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM flights LIMIT 5")
        results = cursor.fetchall()
        print(results)
```

## Common Patterns

### Get Flight Count

```python
with DatabaseManager() as db:
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM flights")
        print(cursor.fetchone()['count'])
```

### Get Flights by Date

```python
with DatabaseManager() as db:
    df = db.get_flights(start_date='2026-01-23', end_date='2026-01-23')
    print(df)
```

### Get Flights by Airline

```python
with DatabaseManager() as db:
    df = db.get_flights(airline_code='KL')
    print(df)
```

### Insert Flight Data

```python
import pandas as pd

df = pd.DataFrame([{
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
    db.save_flights(df)
```

### Get Top Airlines

```python
with DatabaseManager() as db:
    with db.connection.cursor() as cursor:
        cursor.execute("""
            SELECT airline_code, 
                   AVG(delay_minutes) as avg_delay,
                   COUNT(*) as flights
            FROM flights
            WHERE schedule_date >= '2026-01-01'
            GROUP BY airline_code
            ORDER BY avg_delay ASC
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"{row['airline_code']}: {row['avg_delay']:.1f}min ({row['flights']} flights)")
```

### Get Airline Statistics

```python
with DatabaseManager() as db:
    stats = db.get_airline_statistics(
        start_date='2026-01-01',
        end_date='2026-01-23'
    )
    print(stats.head(10))
```

## Environment Variables

```env
MARIA_SERVER=<server_ip>
MARIA_SSH_USER=flights
MARIA_ID_ED25519="C:\Projects\Airlines\id_ed25519"
MARIA_DB=flights
MARIA_DB_USER=flights
MARIA_DB_PASSWORD=<password>
```

## Test Connection

```bash
python database.py
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| ModuleNotFoundError | `python -m pip install -r requirements.txt` |
| SSH key not found | Check path in `.env` file |
| Connection timeout | Verify server is accessible |
| Authentication failed | Check SSH username and key |
| Database access denied | Verify database credentials |
