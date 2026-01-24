"""
View Data Collection Log
Queries the database log to show collection history and recommend next collection timeframe
"""
from database import DatabaseManager
from datetime import datetime, timedelta
import pandas as pd

def view_collection_log():
    """View the data collection log and provide recommendations"""
    
    print("=" * 80)
    print("DATA COLLECTION LOG")
    print("=" * 80)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        with DatabaseManager() as db:
            # Get recent collection log entries
            log_df = db.get_collection_log(limit=50)
            
            if log_df.empty:
                print("⚠️  No collection log entries found in database.")
                print("\nThis could mean:")
                print("  1. The log table was just created")
                print("  2. No data has been collected yet with logging enabled")
                print("\nTo start collecting data with logging:")
                print("  python main.py collect --days-back 7")
                print("\n" + "=" * 80)
                return
            
            # Display summary statistics
            print("COLLECTION SUMMARY:")
            print("-" * 80)
            total_collections = len(log_df)
            successful = len(log_df[log_df['status'] == 'success'])
            failed = len(log_df[log_df['status'] == 'failed'])
            total_records = log_df['records_collected'].sum()
            
            print(f"Total Operations: {total_collections}")
            print(f"  ✓ Successful: {successful}")
            if failed > 0:
                print(f"  ✗ Failed: {failed}")
            print(f"Total Records Collected: {total_records:,}")
            print()
            
            # Show recent entries
            print("RECENT COLLECTION ACTIVITIES (Last 20):")
            print("-" * 80)
            print(f"{'Date/Time':<20} {'Operation':<10} {'Type':<10} {'Date Range':<25} {'Records':<10} {'Status'}")
            print("-" * 80)
            
            for _, row in log_df.head(20).iterrows():
                collection_time = row['collection_date'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['collection_date']) else 'Unknown'
                operation = row['operation_type']
                flight_type = 'Departures' if row['flight_direction'] == 'D' else 'Arrivals'
                date_range = f"{row['date_range_start']} to {row['date_range_end']}"
                records = row['records_collected'] if pd.notna(row['records_collected']) else 0
                status = row['status']
                status_icon = '✓' if status == 'success' else '✗'
                
                print(f"{collection_time:<20} {operation:<10} {flight_type:<10} {date_range:<25} {records:<10} {status_icon} {status}")
            
            print()
            
            # Analyze coverage
            print("DATE COVERAGE ANALYSIS:")
            print("-" * 80)
            
            # Get unique date ranges collected
            collect_ops = log_df[log_df['operation_type'] == 'collect']
            
            if not collect_ops.empty:
                earliest_start = collect_ops['date_range_start'].min()
                latest_end = collect_ops['date_range_end'].max()
                
                print(f"Earliest data collected: {earliest_start}")
                print(f"Latest data collected: {latest_end}")
                
                # Check how current the data is
                if pd.notna(latest_end):
                    latest_date = pd.to_datetime(latest_end)
                    today = pd.Timestamp.now()
                    days_behind = (today - latest_date).days
                    
                    print(f"Current date: {today.strftime('%Y-%m-%d')}")
                    print(f"Days behind: {days_behind}")
                    print()
                    
                    # Recommendations
                    print("=" * 80)
                    print("RECOMMENDATIONS FOR NEXT COLLECTION:")
                    print("=" * 80)
                    
                    if days_behind > 2:
                        print(f"\n⚠️  Data is {days_behind} days behind!")
                        print(f"\nRecommended action:")
                        print(f"  Collect data from {latest_end} to today")
                        print(f"\n  Command:")
                        print(f"  python main.py collect --days-back {days_behind}")
                        
                    elif days_behind == 1:
                        print(f"\n✓ Data is 1 day behind")
                        print(f"\nRecommended action:")
                        print(f"  Collect yesterday's data")
                        print(f"\n  Command:")
                        print(f"  python main.py collect --days-back 1")
                        
                    elif days_behind == 0:
                        print(f"\n✓ Data is up to date!")
                        print(f"\nNext collection:")
                        print(f"  Wait until tomorrow to collect today's complete data")
                        print(f"  Or collect partial data for today:")
                        print(f"\n  Command:")
                        print(f"  python main.py collect --days-back 0")
                    
                    else:
                        print(f"\n⚠️  Latest collection date is in the future?")
                        print(f"  This might indicate scheduled/future flight data")
                    
                    # Check for gaps
                    print(f"\n\nCHECKING FOR DATE GAPS...")
                    print("-" * 80)
                    
                    # Query database for actual flight data gaps
                    cursor = db.connection.cursor()
                    cursor.execute("""
                        SELECT DISTINCT schedule_date 
                        FROM flights 
                        ORDER BY schedule_date
                    """)
                    flight_dates = [row['schedule_date'] for row in cursor.fetchall()]
                    cursor.close()
                    
                    if flight_dates:
                        # Find gaps
                        flight_dates_set = set(pd.to_datetime(flight_dates))
                        date_range = pd.date_range(
                            start=min(flight_dates_set),
                            end=max(flight_dates_set),
                            freq='D'
                        )
                        
                        gaps = [d for d in date_range if d not in flight_dates_set]
                        
                        if gaps:
                            print(f"Found {len(gaps)} date gap(s) in flight data:")
                            for gap in gaps[:10]:
                                print(f"  - {gap.strftime('%Y-%m-%d')}")
                            if len(gaps) > 10:
                                print(f"  ... and {len(gaps) - 10} more")
                            
                            print(f"\nTo fill gaps, collect data for specific dates:")
                            if gaps:
                                first_gap = gaps[0].strftime('%Y-%m-%d')
                                print(f"  python main.py collect --days-back <days> --days-forward 0")
                        else:
                            print("✓ No gaps found in collected data!")
                    else:
                        print("No flight data found in database yet.")
            else:
                print("No collection operations logged yet.")
            
            print("\n" + "=" * 80)
            
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 80)

if __name__ == "__main__":
    view_collection_log()
