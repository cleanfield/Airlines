"""
Simple Database Connection Test
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("DATABASE CONNECTION TEST")
print("=" * 80)
print()

# Check credentials
print("Checking environment variables...")
server = os.getenv('MARIA_SERVER')
db_name = os.getenv('MARIA_DB')
db_user = os.getenv('MARIA_DB_USER')
ssh_user = os.getenv('MARIA_SSH_USER')

print(f"Server: {server}")
print(f"Database: {db_name}")
print(f"DB User: {db_user}")
print(f"SSH User: {ssh_user}")
print()

# Test connection
print("Testing database connection...")
print()

try:
    from database import DatabaseManager
    
    with DatabaseManager() as db:
        print("[SUCCESS] Database connection established!")
        print()
        
        # Create tables
        print("Creating/verifying tables...")
        db.create_tables()
        print("[SUCCESS] Tables verified")
        print()
        
        # Check data
        cursor = db.connection.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM flights")
        flight_count = cursor.fetchone()['count']
        print(f"Flights in database: {flight_count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM airline_statistics")
        stats_count = cursor.fetchone()['count']
        print(f"Airline statistics: {stats_count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM data_collection_log")
        log_count = cursor.fetchone()['count']
        print(f"Collection log entries: {log_count}")
        
        cursor.close()
        print()
        print("[SUCCESS] Database is working correctly!")
        
except Exception as e:
    print("[FAILED] Database connection failed")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)

# Check Apex
print()
print("CHECKING APEX...")
print()

try:
    import requests
    apex_url = f"http://{server}/ords/"
    print(f"Apex URL: {apex_url}")
    
    response = requests.get(apex_url, timeout=5)
    print(f"HTTP Status: {response.status_code}")
    
    if response.status_code == 200:
        print("[SUCCESS] Apex is accessible")
    else:
        print("[WARNING] Apex responded but may not be fully configured")
        
except requests.exceptions.Timeout:
    print("[FAILED] Connection timeout")
except requests.exceptions.ConnectionError:
    print("[FAILED] Connection refused - Apex may not be running")
except ImportError:
    print("[INFO] requests library not installed - skipping Apex check")
except Exception as e:
    print(f"[ERROR] {e}")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
