
import json
import os
import sys
from database import DatabaseManager

def setup_destination_tables():
    print("Setting up destination tables...")
    
    # Load JSON data
    json_path = 'destinations_full.json'
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        destinations = json.load(f)
    
    print(f"Loaded {len(destinations)} destinations from JSON")

    db = DatabaseManager()
    conn = db.get_connection()
    
    try:
        with conn.cursor() as cursor:
            # 1. Create Tables
            print("Creating tables...")
            
            # Continents
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS continents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Countries
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    continent_id INT,
                    code VARCHAR(10),
                    FOREIGN KEY (continent_id) REFERENCES continents(id),
                    UNIQUE KEY unique_country (name, continent_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Airports (replacing or creating new)
            # Check if old table exists strictly to warn or migrate? 
            # We'll just Create IF NOT EXISTS but with correct schema.
            # If 'airports' exists with different schema, this might fail or just not add columns.
            # Let's drop the old airports table to be sure we have the right structure.
            # WARNING: This deletes existing data. User asked to "create tables... and use those".
            cursor.execute("DROP TABLE IF EXISTS airports")
            
            cursor.execute("""
                CREATE TABLE airports (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    iata_code VARCHAR(10) UNIQUE,
                    name VARCHAR(255),
                    city VARCHAR(255),
                    country_id INT,
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    destinations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (country_id) REFERENCES countries(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            conn.commit()
            print("Tables created.")
            
            # 2. Populate Data
            print("Populating data...")
            
            # Track IDs to avoid repeated selects
            continent_map = {} # name -> id
            country_map = {} # (name, continent_id) -> id
            
            # Pre-load existing continents/countries if any (though we just created/cleared table?)
            # Just incase we run this twice without drop
            cursor.execute("SELECT id, name FROM continents")
            for r in cursor.fetchall():
                continent_map[r['name']] = r['id']
                
            cursor.execute("SELECT id, name, continent_id FROM countries")
            for r in cursor.fetchall():
                country_map[(r['name'], r['continent_id'])] = r['id']

            stats = {'continents': 0, 'countries': 0, 'airports': 0}
            
            for item in destinations:
                cont_name = item.get('continent') or 'Unknown'
                country_name = item.get('country') or 'Unknown'
                airport_code = item.get('code')
                airport_name = item.get('name') or 'Unknown'
                
                if not airport_code: 
                    continue
                
                # Continent
                if cont_name not in continent_map:
                    # Try insert ignoring duplicates
                    cursor.execute("INSERT IGNORE INTO continents (name) VALUES (%s)", (cont_name,))
                    if cursor.rowcount > 0:
                         continent_map[cont_name] = cursor.lastrowid
                    else:
                         # It existed but wasn't in map? Or case sensitivity. Fetch it.
                         cursor.execute("SELECT id FROM continents WHERE name = %s", (cont_name,))
                         res = cursor.fetchone()
                         if res:
                             continent_map[cont_name] = res['id']
                
                cont_id = continent_map.get(cont_name)
                if not cont_id:
                     # Should not happen if logic above is correct
                     continue

                # Country
                country_key = (country_name, cont_id)
                # Check normalized or exact? Let's rely on DB UNIQUE constraint and INSERT IGNORE
                
                # Check if we have it in memory
                if country_key not in country_map:
                    cursor.execute("INSERT IGNORE INTO countries (name, continent_id) VALUES (%s, %s)", (country_name, cont_id))
                    if cursor.rowcount > 0:
                        country_map[country_key] = cursor.lastrowid
                    else:
                        cursor.execute("SELECT id FROM countries WHERE name = %s AND continent_id = %s", (country_name, cont_id))
                        res = cursor.fetchone()
                        if res:
                            country_map[country_key] = res['id']
                
                country_id = country_map.get(country_key)
                if not country_id:
                    continue
                
                # Airport
                cursor.execute("""
                    INSERT INTO airports (iata_code, name, country_id) 
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE name = VALUES(name), country_id = VALUES(country_id)
                """, (airport_code, airport_name, country_id))
                stats['airports'] += 1
                
            conn.commit()
            print(f"Population complete. Stats: {stats}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()

if __name__ == "__main__":
    setup_destination_tables()
