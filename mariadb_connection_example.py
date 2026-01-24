"""
MariaDB Connection Example
Demonstrates how to connect to MariaDB using the DatabaseManager class
"""

from database import DatabaseManager
import pandas as pd

def example_basic_connection():
    """Example 1: Basic connection test"""
    print("=" * 60)
    print("Example 1: Basic Connection Test")
    print("=" * 60)
    
    try:
        # Using context manager (recommended - auto cleanup)
        with DatabaseManager() as db:
            print("✓ Successfully connected to MariaDB!")
            print(f"  Database: {db.db_name}")
            print(f"  User: {db.db_user}")
            print(f"  SSH Host: {db.ssh_host}")
            print(f"  Local Port: {db.local_bind_port}")
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")


def example_create_tables():
    """Example 2: Create database tables"""
    print("\n" + "=" * 60)
    print("Example 2: Create Tables")
    print("=" * 60)
    
    try:
        with DatabaseManager() as db:
            db.create_tables()
            print("✓ Tables created/verified successfully!")
            
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")


def example_execute_query():
    """Example 3: Execute a simple query"""
    print("\n" + "=" * 60)
    print("Example 3: Execute Simple Query")
    print("=" * 60)
    
    try:
        with DatabaseManager() as db:
            # Execute a simple query
            with db.connection.cursor() as cursor:
                cursor.execute("SELECT DATABASE() as current_db, VERSION() as version")
                result = cursor.fetchone()
                
                print(f"✓ Query executed successfully!")
                print(f"  Current Database: {result['current_db']}")
                print(f"  MariaDB Version: {result['version']}")
                
    except Exception as e:
        print(f"✗ Query failed: {e}")


def example_get_table_info():
    """Example 4: Get table information"""
    print("\n" + "=" * 60)
    print("Example 4: Get Table Information")
    print("=" * 60)
    
    try:
        with DatabaseManager() as db:
            with db.connection.cursor() as cursor:
                # Get list of tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                print(f"✓ Found {len(tables)} tables:")
                for table in tables:
                    table_name = list(table.values())[0]
                    
                    # Get row count
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                    count = cursor.fetchone()['count']
                    
                    print(f"  - {table_name}: {count} rows")
                    
    except Exception as e:
        print(f"✗ Failed to get table info: {e}")


def example_insert_sample_data():
    """Example 5: Insert sample flight data"""
    print("\n" + "=" * 60)
    print("Example 5: Insert Sample Data")
    print("=" * 60)
    
    try:
        with DatabaseManager() as db:
            # Create sample flight data
            sample_data = pd.DataFrame([{
                'flight_id': 999999,
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
            rows_affected = db.save_flights(sample_data)
            print(f"✓ Inserted/updated {rows_affected} flight record(s)")
            
    except Exception as e:
        print(f"✗ Failed to insert data: {e}")


def example_query_flights():
    """Example 6: Query flight data"""
    print("\n" + "=" * 60)
    print("Example 6: Query Flight Data")
    print("=" * 60)
    
    try:
        with DatabaseManager() as db:
            # Get flights from today
            df = db.get_flights(
                start_date='2026-01-23',
                end_date='2026-01-23'
            )
            
            if not df.empty:
                print(f"✓ Retrieved {len(df)} flight(s) from 2026-01-23:")
                print(f"\n{df[['flight_number', 'airline_code', 'schedule_time', 'delay_minutes']].head()}")
            else:
                print("  No flights found for this date")
                
    except Exception as e:
        print(f"✗ Failed to query flights: {e}")


def example_manual_connection():
    """Example 7: Manual connection (without context manager)"""
    print("\n" + "=" * 60)
    print("Example 7: Manual Connection Management")
    print("=" * 60)
    
    db = DatabaseManager()
    
    try:
        # Manually connect
        db.connect()
        print("✓ Manually connected to database")
        
        # Do some work
        with db.connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM flights")
            result = cursor.fetchone()
            print(f"  Total flights in database: {result['count']}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        
    finally:
        # Always disconnect manually
        db.disconnect()
        print("✓ Manually disconnected")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "MariaDB Connection Examples" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Run examples
    example_basic_connection()
    example_create_tables()
    example_execute_query()
    example_get_table_info()
    example_insert_sample_data()
    example_query_flights()
    example_manual_connection()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
