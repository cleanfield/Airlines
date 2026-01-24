"""
Check Flight Data Collection Log
Queries the database to determine what timeframes have been collected
"""
from database import DatabaseManager
import pandas as pd
from datetime import datetime

def check_collection_history():
    """Check what flight data has been collected and stored in the database"""
    
    print("=" * 80)
    print("FLIGHT DATA COLLECTION HISTORY")
    print("=" * 80)
    print(f"\nCurrent time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        with DatabaseManager() as db:
            # Query to get date ranges from flights table
            query_flights = """
                SELECT 
                    MIN(schedule_date) as earliest_date,
                    MAX(schedule_date) as latest_date,
                    COUNT(*) as total_flights,
                    COUNT(DISTINCT schedule_date) as days_covered,
                    SUM(CASE WHEN flight_direction = 'D' THEN 1 ELSE 0 END) as departures,
                    SUM(CASE WHEN flight_direction = 'A' THEN 1 ELSE 0 END) as arrivals
                FROM flights
            """
            
            cursor = db.connection.cursor()
            cursor.execute(query_flights)
            result = cursor.fetchone()
            
            if result and result[0]:
                earliest, latest, total, days, departures, arrivals = result
                
                print("FLIGHTS TABLE SUMMARY:")
                print("-" * 80)
                print(f"  Date Range: {earliest} to {latest}")
                print(f"  Days Covered: {days}")
                print(f"  Total Flights: {total:,}")
                print(f"    - Departures: {departures:,}")
                print(f"    - Arrivals: {arrivals:,}")
                print()
            else:
                print("No flight data found in database.")
                print()
            
            # Query to get airline statistics date ranges
            query_stats = """
                SELECT 
                    date_range_start,
                    date_range_end,
                    flight_direction,
                    COUNT(*) as airlines_count,
                    created_at
                FROM airline_statistics
                GROUP BY date_range_start, date_range_end, flight_direction, created_at
                ORDER BY created_at DESC
            """
            
            cursor.execute(query_stats)
            stats_results = cursor.fetchall()
            
            if stats_results:
                print("AIRLINE STATISTICS PROCESSING HISTORY:")
                print("-" * 80)
                print(f"{'Start Date':<12} {'End Date':<12} {'Type':<10} {'Airlines':<10} {'Processed At'}")
                print("-" * 80)
                
                for row in stats_results:
                    start, end, direction, count, created = row
                    flight_type = "Departures" if direction == 'D' else "Arrivals"
                    created_str = created.strftime('%Y-%m-%d %H:%M') if created else 'Unknown'
                    print(f"{start:<12} {end:<12} {flight_type:<10} {count:<10} {created_str}")
                print()
            else:
                print("No airline statistics found in database.")
                print()
            
            # Query to get daily breakdown
            query_daily = """
                SELECT 
                    schedule_date,
                    flight_direction,
                    COUNT(*) as flight_count,
                    COUNT(DISTINCT airline_code) as airlines
                FROM flights
                GROUP BY schedule_date, flight_direction
                ORDER BY schedule_date DESC, flight_direction
                LIMIT 30
            """
            
            cursor.execute(query_daily)
            daily_results = cursor.fetchall()
            
            if daily_results:
                print("DAILY FLIGHT DATA (Last 30 entries):")
                print("-" * 80)
                print(f"{'Date':<12} {'Type':<10} {'Flights':<10} {'Airlines'}")
                print("-" * 80)
                
                for row in daily_results:
                    date, direction, flights, airlines = row
                    flight_type = "Departures" if direction == 'D' else "Arrivals"
                    print(f"{date:<12} {flight_type:<10} {flights:<10} {airlines}")
                print()
            
            cursor.close()
            
            # Recommendations
            print("=" * 80)
            print("RECOMMENDATIONS FOR NEXT DATA COLLECTION:")
            print("=" * 80)
            
            if result and result[0]:
                from datetime import datetime, timedelta
                latest_date = datetime.strptime(str(latest), '%Y-%m-%d')
                today = datetime.now()
                days_behind = (today - latest_date).days
                
                if days_behind > 1:
                    print(f"\n⚠️  Data is {days_behind} days behind current date!")
                    print(f"   Latest data: {latest}")
                    print(f"   Current date: {today.strftime('%Y-%m-%d')}")
                    print(f"\n   Suggested collection command:")
                    print(f"   python main.py collect --days-back {days_behind}")
                elif days_behind == 1:
                    print(f"\n✓ Data is 1 day behind. Consider collecting yesterday's data:")
                    print(f"   python main.py collect --days-back 1")
                else:
                    print(f"\n✓ Data is up to date!")
                    print(f"   Latest data: {latest}")
                    
                # Check for gaps
                query_gaps = """
                    WITH RECURSIVE date_range AS (
                        SELECT MIN(schedule_date) as date FROM flights
                        UNION ALL
                        SELECT DATE_ADD(date, INTERVAL 1 DAY)
                        FROM date_range
                        WHERE date < (SELECT MAX(schedule_date) FROM flights)
                    )
                    SELECT dr.date
                    FROM date_range dr
                    LEFT JOIN (
                        SELECT DISTINCT schedule_date 
                        FROM flights
                    ) f ON dr.date = f.schedule_date
                    WHERE f.schedule_date IS NULL
                    ORDER BY dr.date
                """
                
                cursor = db.connection.cursor()
                cursor.execute(query_gaps)
                gaps = cursor.fetchall()
                cursor.close()
                
                if gaps:
                    print(f"\n⚠️  Found {len(gaps)} date gap(s) in collected data:")
                    for gap in gaps[:10]:  # Show first 10 gaps
                        print(f"   - {gap[0]}")
                    if len(gaps) > 10:
                        print(f"   ... and {len(gaps) - 10} more")
            else:
                print("\n⚠️  No data in database yet!")
                print("   Start collecting data with:")
                print("   python main.py collect --days-back 7")
            
            print("\n" + "=" * 80)
            
    except Exception as e:
        print(f"\n❌ Error accessing database: {e}")
        print("\nTrying to check local files instead...")
        print()
        
        # Fallback: check local files
        import os
        import config
        
        raw_files = os.listdir(config.RAW_DATA_DIR)
        flight_files = [f for f in raw_files if f.endswith('.json') and not f.startswith('.')]
        
        if flight_files:
            print("LOCAL RAW DATA FILES:")
            print("-" * 80)
            for file in sorted(flight_files):
                print(f"  {file}")
            print()
            
            # Extract date ranges
            dates = set()
            for file in flight_files:
                parts = file.replace('.json', '').split('_')
                if len(parts) >= 4:
                    dates.add(parts[1])  # start date
                    dates.add(parts[3])  # end date
            
            if dates:
                sorted_dates = sorted(dates)
                print(f"Date range in files: {sorted_dates[0]} to {sorted_dates[-1]}")
                print()
        else:
            print("No local data files found either.")
            print()

if __name__ == "__main__":
    check_collection_history()
