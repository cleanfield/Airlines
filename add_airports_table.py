"""
Script to create airports table in both local and remote MariaDB
"""
import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Local Docker MariaDB connection
def add_airports_to_local_db():
    """Add airports table to local Docker MariaDB"""
    print("=== Adding airports table to LOCAL MariaDB ===\n")
    
    try:
        # Connect to local MariaDB
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='nog3willy3',
            database='luchthavens_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("[OK] Connected to local MariaDB")
        
        with connection.cursor() as cursor:
            # Show existing data
            cursor.execute("SELECT * FROM luchthavens")
            airports = cursor.fetchall()
            print(f"\n[OK] Found {len(airports)} airports in local database:")
            for airport in airports:
                print(f"  - {airport['naam']} ({airport['iata_code']}) - {airport['stad']}, {airport['land']}")
        
        connection.close()
        print("\n[OK] Local database check completed\n")
        
    except Exception as e:
        print(f"[ERROR] Error with local database: {e}\n")

# Remote MariaDB connection (on droplet)
def add_airports_to_remote_db():
    """Add airports table to remote MariaDB"""
    print("=== Adding airports table to REMOTE MariaDB ===\n")
    
    try:
        from database import DatabaseManager
        
        # Use existing DatabaseManager for SSH tunnel connection
        with DatabaseManager() as db:
            print("[OK] Connected to remote MariaDB via SSH tunnel")
            
            with db.connection.cursor() as cursor:
                # Create airports table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS airports (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        naam VARCHAR(255) NOT NULL,
                        iata_code VARCHAR(3) NOT NULL UNIQUE,
                        icao_code VARCHAR(4),
                        stad VARCHAR(255) NOT NULL,
                        land VARCHAR(100) NOT NULL,
                        latitude DECIMAL(10, 6),
                        longitude DECIMAL(10, 6),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_iata_code (iata_code),
                        INDEX idx_land (land)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                print("[OK] Airports table created")
                
                # Insert airport data from local database
                cursor.execute("""
                    INSERT IGNORE INTO airports (naam, iata_code, icao_code, stad, land, latitude, longitude) VALUES
                    ('Schiphol Airport', 'AMS', 'EHAM', 'Amsterdam', 'Nederland', 52.308056, 4.764167),
                    ('London Heathrow', 'LHR', 'EGLL', 'Londen', 'Engeland', 51.470022, -0.454296),
                    ('Brussels Airport', 'BRU', 'EBBR', 'Brussel', 'België', 50.901389, 4.484444),
                    ('Charles de Gaulle', 'CDG', 'LFPG', 'Parijs', 'Frankrijk', 49.012779, 2.550000),
                    ('Frankfurt Airport', 'FRA', 'EDDF', 'Frankfurt', 'Duitsland', 50.026421, 8.543125)
                """)
                
                db.connection.commit()
                print(f"[OK] Inserted {cursor.rowcount} airports")
                
                # Show inserted data
                cursor.execute("SELECT * FROM airports ORDER BY naam")
                airports = cursor.fetchall()
                print(f"\n[OK] Total {len(airports)} airports in remote database:")
                for airport in airports:
                    print(f"  - {airport['naam']} ({airport['iata_code']}) - {airport['stad']}, {airport['land']}")
                
        print("\n[OK] Remote database setup completed\n")
        
    except Exception as e:
        print(f"[ERROR] Error with remote database: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=== Airport Tables Setup ===\n")
    add_airports_to_local_db()
    add_airports_to_remote_db()
    print("=== Setup Complete ===")
