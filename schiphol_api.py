"""
Schiphol Airport API Client
Handles all interactions with the Schiphol Flight API v4
"""
import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config


class SchipholAPIClient:
    """Client for interacting with Schiphol Flight API"""
    
    def __init__(self):
        self.base_url = config.SCHIPHOL_CONFIG['base_url']
        self.app_id = config.SCHIPHOL_CONFIG['app_id']
        self.app_key = config.SCHIPHOL_CONFIG['app_key']
        self.resource_version = config.SCHIPHOL_CONFIG['resource_version']
        
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for API requests"""
        return {
            'Accept': 'application/json',
            'app_id': self.app_id,
            'app_key': self.app_key,
            'ResourceVersion': self.resource_version
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Schiphol API
        
        Args:
            endpoint: API endpoint (e.g., '/flights')
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {}
    
    def get_flights(self, 
                   schedule_date: Optional[str] = None,
                   flight_direction: Optional[str] = None,
                   page: int = 0,
                   sort: str = '+scheduleTime',
                   include_delays: bool = True) -> Dict:
        """
        Get flight information
        
        Args:
            schedule_date: Date in YYYY-MM-DD format
            flight_direction: 'A' for arrivals, 'D' for departures
            page: Page number for pagination
            sort: Sort order (e.g., '+scheduleTime', '-scheduleTime')
            include_delays: Whether to include delay information
            
        Returns:
            Flight data dictionary
        """
        params = {
            'page': page,
            'sort': sort,
            'includedelays': str(include_delays).lower()
        }
        
        if schedule_date:
            params['scheduleDate'] = schedule_date
        if flight_direction:
            params['flightDirection'] = flight_direction
            
        return self._make_request('/flights', params)
    
    def get_all_flights(self,
                       schedule_date: Optional[str] = None,
                       flight_direction: Optional[str] = None,
                       max_pages: Optional[int] = None) -> List[Dict]:
        """
        Get all flights across multiple pages
        
        Args:
            schedule_date: Date in YYYY-MM-DD format
            flight_direction: 'A' for arrivals, 'D' for departures
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of all flight records
        """
        all_flights = []
        page = 0
        max_pages = max_pages or config.COLLECTION_SETTINGS['max_pages']
        
        while page < max_pages:
            print(f"Fetching page {page}...")
            data = self.get_flights(
                schedule_date=schedule_date,
                flight_direction=flight_direction,
                page=page
            )
            
            if not data or 'flights' not in data:
                break
                
            flights = data.get('flights', [])
            if not flights:
                break
                
            all_flights.extend(flights)
            
            # Check if there are more pages
            # The API returns a link header, but we can also check if we got a full page
            if len(flights) < config.COLLECTION_SETTINGS['page_size']:
                break
                
            page += 1
            time.sleep(config.COLLECTION_SETTINGS['delay_between_requests'])
        
        print(f"Total flights collected: {len(all_flights)}")
        return all_flights
    
    def get_flights_by_date_range(self,
                                 start_date: str,
                                 end_date: str,
                                 flight_direction: Optional[str] = None) -> List[Dict]:
        """
        Get flights for a date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            flight_direction: 'A' for arrivals, 'D' for departures
            
        Returns:
            List of all flight records in the date range
        """
        all_flights = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end_date_obj:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"\nCollecting flights for {date_str}...")
            
            flights = self.get_all_flights(
                schedule_date=date_str,
                flight_direction=flight_direction
            )
            all_flights.extend(flights)
            
            current_date += timedelta(days=1)
        
        return all_flights
    
    def get_destinations(self) -> Dict:
        """Get list of destinations"""
        return self._make_request('/destinations')
    
    def get_airlines(self) -> Dict:
        """Get list of airlines"""
        return self._make_request('/airlines')
    
    def get_aircraft_types(self) -> Dict:
        """Get list of aircraft types"""
        return self._make_request('/aircrafttypes')
    
    def save_flights_to_file(self, flights: List[Dict], filename: str):
        """
        Save flight data to JSON file
        
        Args:
            flights: List of flight records
            filename: Output filename
        """
        filepath = f"{config.RAW_DATA_DIR}/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(flights, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(flights)} flights to {filepath}")


if __name__ == "__main__":
    # Example usage
    client = SchipholAPIClient()
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    print("=== Schiphol API Client Test ===\n")
    
    # Get departures for today
    print("Fetching departures for today...")
    departures = client.get_all_flights(
        schedule_date=today,
        flight_direction='D',
        max_pages=2
    )
    
    if departures:
        print(f"\nSample departure flight:")
        print(json.dumps(departures[0], indent=2))
        
        # Save to file
        filename = f"departures_{today}.json"
        client.save_flights_to_file(departures, filename)
    
    # Get arrivals for today
    print("\n\nFetching arrivals for today...")
    arrivals = client.get_all_flights(
        schedule_date=today,
        flight_direction='A',
        max_pages=2
    )
    
    if arrivals:
        print(f"\nSample arrival flight:")
        print(json.dumps(arrivals[0], indent=2))
        
        # Save to file
        filename = f"arrivals_{today}.json"
        client.save_flights_to_file(arrivals, filename)
