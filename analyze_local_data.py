"""
Analyze Local Flight Data Files
Determines collection timeframes from local JSON files when database is not available
"""
import os
import json
from datetime import datetime, timedelta
import config

def analyze_local_files():
    """Analyze local flight data files to determine collection history"""
    
    print("=" * 80)
    print("LOCAL FLIGHT DATA ANALYSIS")
    print("=" * 80)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    raw_dir = config.RAW_DATA_DIR
    
    # Get all JSON files
    files = [f for f in os.listdir(raw_dir) if f.endswith('.json') and not f.startswith('.')]
    
    if not files:
        print("⚠️  No flight data files found!")
        print(f"\nSearched in: {raw_dir}")
        print("\nTo start collecting data:")
        print("  python main.py collect --days-back 7")
        print("\n" + "=" * 80)
        return
    
    print(f"Found {len(files)} data file(s) in {raw_dir}\n")
    
    # Parse file information
    file_info = []
    for filename in files:
        parts = filename.replace('.json', '').split('_')
        if len(parts) >= 4:
            flight_type = parts[0]  # 'arrivals' or 'departures'
            start_date = parts[1]
            end_date = parts[3]
            
            filepath = os.path.join(raw_dir, filename)
            file_size = os.path.getsize(filepath)
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            # Count records in file
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    record_count = len(data) if isinstance(data, list) else 0
            except:
                record_count = 0
            
            file_info.append({
                'filename': filename,
                'type': flight_type,
                'start_date': start_date,
                'end_date': end_date,
                'records': record_count,
                'size_kb': file_size / 1024,
                'modified': file_modified
            })
    
    # Sort by start date
    file_info.sort(key=lambda x: x['start_date'], reverse=True)
    
    # Display file information
    print("COLLECTED DATA FILES:")
    print("-" * 80)
    print(f"{'Filename':<45} {'Type':<11} {'Records':<10} {'Size (KB)':<12} {'Modified'}")
    print("-" * 80)
    
    for info in file_info:
        print(f"{info['filename']:<45} {info['type'].capitalize():<11} {info['records']:<10} {info['size_kb']:<12.1f} {info['modified'].strftime('%Y-%m-%d %H:%M')}")
    
    print()
    
    # Analyze date coverage
    print("DATE COVERAGE:")
    print("-" * 80)
    
    all_dates = set()
    for info in file_info:
        all_dates.add(info['start_date'])
        all_dates.add(info['end_date'])
    
    if all_dates:
        sorted_dates = sorted(all_dates)
        earliest = sorted_dates[0]
        latest = sorted_dates[-1]
        
        print(f"Earliest data: {earliest}")
        print(f"Latest data: {latest}")
        
        # Calculate days behind
        latest_date = datetime.strptime(latest, '%Y-%m-%d')
        today = datetime.now()
        days_behind = (today - latest_date).days
        
        print(f"Current date: {today.strftime('%Y-%m-%d')}")
        print(f"Days behind: {days_behind}")
        print()
        
        # Statistics
        total_records = sum(info['records'] for info in file_info)
        departures_count = sum(info['records'] for info in file_info if info['type'] == 'departures')
        arrivals_count = sum(info['records'] for info in file_info if info['type'] == 'arrivals')
        
        print("SUMMARY:")
        print("-" * 80)
        print(f"Total records: {total_records:,}")
        print(f"  Departures: {departures_count:,}")
        print(f"  Arrivals: {arrivals_count:,}")
        print()
        
        # Recommendations
        print("=" * 80)
        print("RECOMMENDATIONS FOR NEXT COLLECTION:")
        print("=" * 80)
        
        if days_behind > 2:
            print(f"\n⚠️  Data is {days_behind} days behind current date!")
            print(f"\nRecommended action:")
            print(f"  Collect data from {latest} to today")
            print(f"\n  Command:")
            print(f"  python main.py collect --days-back {days_behind}")
            print(f"\n  Then process the data:")
            next_date = (latest_date + timedelta(days=1)).strftime('%Y-%m-%d')
            today_str = today.strftime('%Y-%m-%d')
            print(f"  python main.py process departures {next_date}_to_{today_str}")
            print(f"  python main.py process arrivals {next_date}_to_{today_str}")
            
        elif days_behind == 1:
            print(f"\n✓ Data is 1 day behind")
            print(f"\nRecommended action:")
            print(f"  Collect yesterday's data")
            print(f"\n  Command:")
            print(f"  python main.py collect --days-back 1")
            yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
            print(f"\n  Then process:")
            print(f"  python main.py process departures {yesterday}_to_{yesterday}")
            print(f"  python main.py process arrivals {yesterday}_to_{yesterday}")
            
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
        
        # Check for date gaps
        print(f"\n\nCHECKING FOR DATE GAPS...")
        print("-" * 80)
        
        # Get all unique date ranges
        date_ranges = set()
        for info in file_info:
            start = datetime.strptime(info['start_date'], '%Y-%m-%d')
            end = datetime.strptime(info['end_date'], '%Y-%m-%d')
            current = start
            while current <= end:
                date_ranges.add(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
        
        # Find gaps
        if date_ranges:
            all_dates_in_range = set()
            min_date = datetime.strptime(min(date_ranges), '%Y-%m-%d')
            max_date = datetime.strptime(max(date_ranges), '%Y-%m-%d')
            current = min_date
            while current <= max_date:
                all_dates_in_range.add(current.strftime('%Y-%m-%d'))
                current += timedelta(days=1)
            
            gaps = sorted(all_dates_in_range - date_ranges)
            
            if gaps:
                print(f"Found {len(gaps)} date gap(s):")
                for gap in gaps[:10]:
                    print(f"  - {gap}")
                if len(gaps) > 10:
                    print(f"  ... and {len(gaps) - 10} more")
                
                print(f"\nTo fill gaps, collect data for specific dates")
            else:
                print("✓ No gaps found in date coverage!")
    
    print("\n" + "=" * 80)
    print("\nNOTE: This analysis is based on local files only.")
    print("For complete logging with database tracking, use:")
    print("  python view_collection_log.py")
    print("=" * 80)

if __name__ == "__main__":
    analyze_local_files()
