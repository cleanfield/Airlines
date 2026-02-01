
from schiphol_api import SchipholAPIClient
import json
import time

def fetch_destinations():
    client = SchipholAPIClient()
    all_destinations = {}
    
    page = 0
    max_pages = 50
    while page < max_pages:
        print(f"Fetching page {page}...")
        response = client._make_request('/destinations', params={'page': page})
        
        if not response or 'destinations' not in response:
            break
            
        destinations = response.get('destinations', [])
        if not destinations:
            break
            
        print(f"Found {len(destinations)} destinations on page {page}")
        
        for dest in destinations:
            iata = dest.get('iata')
            # Extract English name if available, otherwise generic publicName
            name = dest.get('publicName', {}).get('english')
            
            if iata and name:
                all_destinations[iata] = name
        
        # Check for next link or if empty
        if len(destinations) < 20: # Assuming page size is 20
             break
             
        page += 1
        time.sleep(0.2)
        
    print(f"Total mapped destinations: {len(all_destinations)}")
    
    with open('destination_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(all_destinations, f, indent=2)

if __name__ == "__main__":
    fetch_destinations()
