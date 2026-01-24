"""
Simple MariaDB Connection Test
Tests database connectivity using the database module
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("MARIADB CONNECTION TEST")
print("=" * 80)

# Check environment variables
print("\nChecking environment variables...")
print(f"MARIA_SERVER: {os.getenv('MARIA_SERVER')}")
print(f"MARIA_DB: {os.getenv('MARIA_DB')}")
print(f"MARIA_USER: {os.getenv('MARIA_USER')}")
print(f"MARIA_PASSWORD: {'***' if os.getenv('MARIA_PASSWORD') else 'NOT SET'}")
print(f"MARIA_ID_ED25519: {os.getenv('MARIA_ID_ED25519')}")

# Test database connection
print("\nAttempting database connection...")
try:
    from database import DatabaseManager
    
    with DatabaseManager() as db:
        print("\n[SUCCESS] Database connection established!")
        
        # Create tables
        print("\nCreating/verifying tables...")
        db.create_tables()
        print("[SUCCESS] Tables created/verified!")
        
        # Test query
        print("\nTesting database query...")
        with db.connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            result = cursor.fetchone()
            print(f"[SUCCESS] Connected to database: {result}")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\nTables in database:")
            for table in tables:
                print(f"  - {list(table.values())[0]}")
        
        print("\n" + "=" * 80)
        print("[SUCCESS] All database tests passed!")
        print("=" * 80)
        
except Exception as e:
    print(f"\n[ERROR] Database test failed: {e}")
    print("=" * 80)
    import traceback
    traceback.print_exc()
