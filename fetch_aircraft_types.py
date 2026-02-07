
from schiphol_api import SchipholAPIClient
from database import DatabaseManager
import json
import time

def fetch_all_aircraft_types():
    # optimized to use session/connection
    db = DatabaseManager()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # 1. Create table
    print("Creating aircraft_types table if not exists...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aircraft_types (
            iata_sub VARCHAR(10) PRIMARY KEY,
            iata_main VARCHAR(10),
            long_description VARCHAR(255),
            short_description VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
    """)
    conn.commit()
    
    client = SchipholAPIClient()
    print("Fetching all aircraft types from Schiphol API...")
    
    all_types = []
    page = 0
    max_pages = 50 
    
    while page < max_pages:
        print(f"Fetching page {page}...")
        try:
            response = client._make_request('/aircrafttypes', params={'page': page})
            
            if not response or 'aircraftTypes' not in response:
                break
                
            types = response['aircraftTypes']
            if not types:
                break
                
            all_types.extend(types)
            print(f"Fetched {len(types)} types. Total: {len(all_types)}")
            
            # Insert into DB immediately
            for item in types:
                cursor.execute("""
                    INSERT INTO aircraft_types (iata_sub, iata_main, long_description, short_description)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        iata_main = VALUES(iata_main),
                        long_description = VALUES(long_description),
                        short_description = VALUES(short_description)
                """, (
                    item.get('iataSub', ''),
                    item.get('iataMain', ''),
                    item.get('longDescription', ''),
                    item.get('shortDescription', '')
                ))
            conn.commit()
            
            if len(types) < 20: 
                break
                
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
            
    cursor.close()
    conn.close()
    
    # Save raw data as backup
    with open('aircraft_types.json', 'w', encoding='utf-8') as f:
        json.dump(all_types, f, indent=2)
    print(f"Saved {len(all_types)} aircraft types to database and aircraft_types.json")

    # Mapping file creation (still useful for quick lookup if needed, but DB is primary now)
    mapping = {}
    for item in all_types:
        if 'iataSub' in item:
            mapping[item['iataSub']] = item['longDescription']
        
    with open('aircraft_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2)
    print(f"Created mapping with {len(mapping)} entries in aircraft_mapping.json")

if __name__ == "__main__":
    fetch_all_aircraft_types()
