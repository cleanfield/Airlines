
from schiphol_api import SchipholAPIClient
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

try:
    print("Initializing client...")
    client = SchipholAPIClient()
    print("Fetching airlines (all pages)...")
    
    all_airlines = []
    page = 0
    max_pages = 50 # Avoid infinite loops
    
    while page < max_pages:
        print(f"Fetching page {page}...")
        try:
            data = client.get_airlines(page=page)
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
        if not data or 'airlines' not in data:
            print("No airlines key or empty data")
            break
            
        airlines = data['airlines']
        if not airlines:
            print("Empty airlines list, finished.")
            break
            
        print(f"  Found {len(airlines)} airlines on page {page}")
        all_airlines.extend(airlines)
        
        # Check link header or size? API usually returns 'airlines' list.
        # If list is smaller than page size (usually 20?), we are done?
        # But we can just try next page until empty.
        
        page += 1
        time.sleep(0.5)
    
    print(f"Total airlines found: {len(all_airlines)}")
    
    with open('airlines_raw.json', 'w') as f:
        json.dump(all_airlines, f, indent=2)
    
    if all_airlines:
        mapping = {}
        for airline in all_airlines:
             name = airline.get('publicName') or airline.get('name', 'Unknown')
             
             if airline.get('iata'):
                 mapping[str(airline['iata'])] = name
             if airline.get('nvls'):
                 mapping[str(airline['nvls'])] = name
             if airline.get('icao'):
                 mapping[str(airline['icao'])] = name
        
        with open('airline_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2)
        print(f"Saved mapping with {len(mapping)} entries to airline_mapping.json")

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
