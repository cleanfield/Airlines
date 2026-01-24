"""
Practical MariaDB Connection Test
This script tests your MariaDB connection and performs basic operations
"""

from database import DatabaseManager
import sys

def test_connection():
    """Test 1: Basic connection"""
    print("\n" + "="*60)
    print("TEST 1: Basic Connection")
    print("="*60)
    
    try:
        with DatabaseManager() as db:
            print("✓ Successfully connected to MariaDB!")
            print(f"  Database: {db.db_name}")
            print(f"  SSH Host: {db.ssh_host}")
            return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_database_info():
    """Test 2: Get database information"""
    print("\n" + "="*60)
    print("TEST 2: Database Information")
    print("="*60)
    
    try:
        with DatabaseManager() as db:
            with db.connection.cursor() as cursor:
                # Get version
                cursor.execute("SELECT VERSION() as version")
                version = cursor.fetchone()['version']
                print(f"✓ MariaDB Version: {version}")
                
                # Get current database
                cursor.execute("SELECT DATABASE() as db")
                current_db = cursor.fetchone()['db']
                print(f"✓ Current Database: {current_db}")
                
                # Get current user
                cursor.execute("SELECT USER() as user")
                user = cursor.fetchone()['user']
                print(f"✓ Connected as: {user}")
                
                return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_tables():
    """Test 3: Check tables"""
    print("\n" + "="*60)
    print("TEST 3: Database Tables")
    print("="*60)
    
    try:
        with DatabaseManager() as db:
            # Create tables if they don't exist
            db.create_tables()
            
            with db.connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if tables:
                    print(f"✓ Found {len(tables)} table(s):")
                    for table in tables:
                        table_name = list(table.values())[0]
                        
                        # Get row count
                        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                        count = cursor.fetchone()['count']
                        
                        print(f"  • {table_name}: {count:,} rows")
                else:
                    print("  No tables found (this is normal for a new database)")
                
                return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_query():
    """Test 4: Execute a query"""
    print("\n" + "="*60)
    print("TEST 4: Query Execution")
    print("="*60)
    
    try:
        with DatabaseManager() as db:
            with db.connection.cursor() as cursor:
                # Try to get some flights
                cursor.execute("SELECT COUNT(*) as count FROM flights")
                count = cursor.fetchone()['count']
                
                print(f"✓ Query executed successfully")
                print(f"  Total flights in database: {count:,}")
                
                if count > 0:
                    # Get sample flight
                    cursor.execute("""
                        SELECT flight_number, airline_code, schedule_date, 
                               delay_minutes, on_time
                        FROM flights 
                        ORDER BY schedule_date DESC 
                        LIMIT 5
                    """)
                    flights = cursor.fetchall()
                    
                    print(f"\n  Recent flights:")
                    for flight in flights:
                        status = "✓ On-time" if flight['on_time'] else "✗ Delayed"
                        delay = flight['delay_minutes'] or 0
                        print(f"    {flight['flight_number']} ({flight['airline_code']}) "
                              f"- {flight['schedule_date']} - {status} ({delay:+.0f} min)")
                else:
                    print("  No flights in database yet")
                
                return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_statistics():
    """Test 5: Check airline statistics"""
    print("\n" + "="*60)
    print("TEST 5: Airline Statistics")
    print("="*60)
    
    try:
        with DatabaseManager() as db:
            with db.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM airline_statistics")
                count = cursor.fetchone()['count']
                
                print(f"✓ Statistics table accessible")
                print(f"  Total statistics records: {count:,}")
                
                if count > 0:
                    # Get top airlines
                    cursor.execute("""
                        SELECT airline_code, total_flights, on_time_percentage, 
                               reliability_score
                        FROM airline_statistics 
                        ORDER BY reliability_score DESC 
                        LIMIT 5
                    """)
                    stats = cursor.fetchall()
                    
                    print(f"\n  Top airlines by reliability:")
                    for i, stat in enumerate(stats, 1):
                        print(f"    {i}. {stat['airline_code']}: "
                              f"{stat['reliability_score']:.2f} score "
                              f"({stat['on_time_percentage']:.1f}% on-time, "
                              f"{stat['total_flights']} flights)")
                else:
                    print("  No statistics calculated yet")
                
                return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "MariaDB Connection Test Suite" + " "*18 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Connection", test_connection),
        ("Database Info", test_database_info),
        ("Tables", test_tables),
        ("Query Execution", test_query),
        ("Statistics", test_statistics)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Your MariaDB connection is working perfectly!")
    elif passed > 0:
        print("\n  ⚠️  Some tests passed. Check the failures above.")
    else:
        print("\n  ❌ All tests failed. Check your connection settings in .env")
    
    print("="*60 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
