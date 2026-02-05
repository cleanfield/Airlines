
from schiphol_api import SchipholAPIClient
import json
import time

def fetch_destinations():
    client = SchipholAPIClient()
    all_destinations = {}
    
    page = 0
    max_pages = 1000
    while page < max_pages:
        if page % 10 == 0:
            print(f"Fetching page {page}...")
        response = client._make_request('/destinations', params={'page': page})
        
        if not response or 'destinations' not in response:
            break
            
        destinations = response.get('destinations', [])
        if not destinations:
            break
            
        # print(f"Found {len(destinations)} destinations on page {page}")


        

        for dest in destinations:
            iata = dest.get('iata')
            public_name = dest.get('publicName', {})
            name = None
            if isinstance(public_name, dict):
                name = public_name.get('dutch') or public_name.get('english')
            elif isinstance(public_name, str):
                name = public_name
            
            country = dest.get('country')
            
            if iata and name:
                all_destinations[iata] = {
                    'name': name,
                    'country': country
                }
        
        # Check for next link or if empty
        if len(destinations) < 20: # Assuming page size is 20
             break
             
        page += 1
        time.sleep(0.1)
        
    print(f"Total mapped destinations: {len(all_destinations)}")
    
    with open('destination_details.json', 'w', encoding='utf-8') as f:
        json.dump(all_destinations, f, indent=2)


if __name__ == "__main__":
    fetch_destinations()
