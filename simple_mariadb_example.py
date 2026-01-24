"""
Simple MariaDB Connection Example
Demonstrates basic PyMySQL usage without SSH tunneling
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_simple():
    """Simple direct connection to MariaDB (no SSH tunnel)"""
    print("=" * 60)
    print("Simple MariaDB Connection Example")
    print("=" * 60)
    
    # Connection parameters
    config = {
        'host': os.getenv('MARIA_SERVER', 'localhost'),
        'user': os.getenv('MARIA_USER', 'root'),
        'password': os.getenv('MARIA_PASSWORD', ''),
        'database': os.getenv('MARIA_DB', 'test'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    print(f"\nConnecting to MariaDB...")
    print(f"  Host: {config['host']}")
    print(f"  User: {config['user']}")
    print(f"  Database: {config['database']}")
    
    try:
        # Establish connection
        connection = pymysql.connect(**config)
        print("\n✓ Connected successfully!")
        
        # Create a cursor
        with connection.cursor() as cursor:
            # Example 1: Get server version
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
            print(f"\n  MariaDB Version: {result['version']}")
            
            # Example 2: Get current database
            cursor.execute("SELECT DATABASE() as current_db")
            result = cursor.fetchone()
            print(f"  Current Database: {result['current_db']}")
            
            # Example 3: Show tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n  Tables in database ({len(tables)}):")
            for table in tables:
                table_name = list(table.values())[0]
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                print(f"    - {table_name}: {count} rows")
        
        # Close connection
        connection.close()
        print("\n✓ Connection closed")
        
    except pymysql.Error as e:
        print(f"\n✗ Error: {e}")
        print("\nNote: If you need SSH tunneling, use the database.py module")
        print("which handles SSH tunnel setup automatically.")


def connect_with_context_manager():
    """Example using context manager for automatic cleanup"""
    print("\n" + "=" * 60)
    print("Context Manager Example")
    print("=" * 60)
    
    config = {
        'host': os.getenv('MARIA_SERVER', 'localhost'),
        'user': os.getenv('MARIA_USER', 'root'),
        'password': os.getenv('MARIA_PASSWORD', ''),
        'database': os.getenv('MARIA_DB', 'test'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        # Connection automatically closes when exiting the 'with' block
        with pymysql.connect(**config) as connection:
            with connection.cursor() as cursor:
                # Execute query
                cursor.execute("""
                    SELECT 
                        'PyMySQL' as library,
                        'MariaDB' as database,
                        VERSION() as version
                """)
                result = cursor.fetchone()
                
                print("\n✓ Query executed successfully:")
                for key, value in result.items():
                    print(f"    {key}: {value}")
                    
    except pymysql.Error as e:
        print(f"\n✗ Error: {e}")


def create_sample_table():
    """Example: Create a sample table"""
    print("\n" + "=" * 60)
    print("Create Table Example")
    print("=" * 60)
    
    config = {
        'host': os.getenv('MARIA_SERVER', 'localhost'),
        'user': os.getenv('MARIA_USER', 'root'),
        'password': os.getenv('MARIA_PASSWORD', ''),
        'database': os.getenv('MARIA_DB', 'test'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        with pymysql.connect(**config) as connection:
            with connection.cursor() as cursor:
                # Create table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sample_flights (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        flight_number VARCHAR(20) NOT NULL,
                        airline VARCHAR(50),
                        departure_time DATETIME,
                        arrival_time DATETIME,
                        status VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
                print("\n✓ Table 'sample_flights' created/verified")
                
                # Insert sample data
                cursor.execute("""
                    INSERT INTO sample_flights 
                    (flight_number, airline, departure_time, arrival_time, status)
                    VALUES 
                    ('KL1234', 'KLM', '2026-01-23 10:00:00', '2026-01-23 12:30:00', 'On Time')
                    ON DUPLICATE KEY UPDATE status=VALUES(status)
                """)
                
                connection.commit()
                print(f"✓ Inserted {cursor.rowcount} row(s)")
                
                # Query the data
                cursor.execute("SELECT * FROM sample_flights LIMIT 5")
                results = cursor.fetchall()
                
                print(f"\n  Sample data ({len(results)} rows):")
                for row in results:
                    print(f"    {row['flight_number']} - {row['airline']} - {row['status']}")
                    
    except pymysql.Error as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "PyMySQL Examples" + " " * 27 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Run examples
    connect_simple()
    connect_with_context_manager()
    create_sample_table()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nFor SSH tunnel support, use the DatabaseManager class")
    print("from database.py which handles secure remote connections.")
    print("=" * 60 + "\n")
