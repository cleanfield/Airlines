"""
Database and Apex Verification Script
Tests database connection and checks Apex availability
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("DATABASE AND APEX VERIFICATION")
print("=" * 80)
print()

# Check environment variables
print("1. CHECKING ENVIRONMENT VARIABLES")
print("-" * 80)

required_vars = [
    'MARIA_SERVER',
    'MARIA_SSH_USER',
    'MARIA_DB',
    'MARIA_DB_USER',
    'MARIA_DB_PASSWORD',
    'MARIA_ID_ED25519'
]

all_present = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if 'PASSWORD' in var or 'PASSPHRASE' in var:
            display_value = '***' + value[-3:] if len(value) > 3 else '***'
        elif 'KEY' in var:
            display_value = value[:20] + '...' if len(value) > 20 else value
        else:
            display_value = value
        print(f"  ✓ {var}: {display_value}")
    else:
        print(f"  ✗ {var}: NOT SET")
        all_present = False

print()

if not all_present:
    print("⚠️  Some required environment variables are missing!")
    print("   Please check your .env file.")
    print()
else:
    print("✓ All required environment variables are set")
    print()

# Check SSH key file
print("2. CHECKING SSH KEY FILE")
print("-" * 80)

ssh_key_path = os.getenv('MARIA_ID_ED25519', '').strip('"')
print(f"  SSH Key Path: {ssh_key_path}")

if os.path.exists(ssh_key_path):
    print(f"  ✓ SSH key file exists")
    file_size = os.path.getsize(ssh_key_path)
    print(f"  File size: {file_size} bytes")
else:
    print(f"  ✗ SSH key file NOT FOUND")
    print(f"  Note: The path might be a WSL path. Checking Windows equivalent...")
    
    # Try to convert WSL path to Windows path
    if ssh_key_path.startswith('/mnt/'):
        windows_path = ssh_key_path.replace('/mnt/c/', 'C:\\').replace('/', '\\')
        print(f"  Windows path: {windows_path}")
        if os.path.exists(windows_path):
            print(f"  ✓ Found at Windows path!")
        else:
            print(f"  ✗ Not found at Windows path either")

print()

# Test database connection
print("3. TESTING DATABASE CONNECTION")
print("-" * 80)

try:
    from database import DatabaseManager
    
    print("  Attempting to connect to database...")
    print(f"  Server: {os.getenv('MARIA_SERVER')}")
    print(f"  Database: {os.getenv('MARIA_DB')}")
    print(f"  User: {os.getenv('MARIA_SSH_USER')}")
    print()
    
    with DatabaseManager() as db:
        print("  ✓ Database connection established!")
        print()
        
        # Create/verify tables
        print("  Creating/verifying tables...")
        db.create_tables()
        print("  ✓ Tables created/verified successfully")
        print()
        
        # Check existing data
        print("  Checking existing data...")
        cursor = db.connection.cursor()
        
        # Check flights table
        cursor.execute("SELECT COUNT(*) as count FROM flights")
        flight_count = cursor.fetchone()['count']
        print(f"  Flights in database: {flight_count:,}")
        
        # Check airline_statistics table
        cursor.execute("SELECT COUNT(*) as count FROM airline_statistics")
        stats_count = cursor.fetchone()['count']
        print(f"  Airline statistics records: {stats_count:,}")
        
        # Check data_collection_log table
        cursor.execute("SELECT COUNT(*) as count FROM data_collection_log")
        log_count = cursor.fetchone()['count']
        print(f"  Collection log entries: {log_count:,}")
        
        cursor.close()
        print()
        print("  ✓ DATABASE CONNECTION SUCCESSFUL!")
        
except Exception as e:
    print(f"  ✗ Database connection FAILED")
    print(f"  Error: {e}")
    print()
    import traceback
    traceback.print_exc()

print()

# Check Apex availability
print("4. CHECKING APEX AVAILABILITY")
print("-" * 80)

try:
    import requests
    
    # Try to access Apex
    apex_url = f"http://{os.getenv('MARIA_SERVER')}/ords/"
    print(f"  Checking Apex at: {apex_url}")
    
    try:
        response = requests.get(apex_url, timeout=5)
        if response.status_code == 200:
            print(f"  ✓ Apex is accessible (HTTP {response.status_code})")
        else:
            print(f"  ⚠️  Apex responded with HTTP {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"  ✗ Connection timeout - Apex may not be running")
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection refused - Apex may not be configured")
    except Exception as e:
        print(f"  ✗ Error accessing Apex: {e}")
    
except ImportError:
    print("  ⚠️  'requests' library not installed")
    print("  Install with: pip install requests")

print()
print("=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
