"""
Data Processing Module
Processes raw flight data and calculates airline reliability metrics
"""
import json
import pandas as pd
from datetime import datetime
<<<<<<< Updated upstream
from typing import List, Dict
=======
from typing import List, Dict, Optional
>>>>>>> Stashed changes
import config


class FlightDataProcessor:
    """Process flight data and calculate reliability metrics"""
    
    def __init__(self):
        self.on_time_threshold = config.RELIABILITY_SETTINGS['on_time_threshold_minutes']
        self.min_flights = config.RELIABILITY_SETTINGS['minimum_flights_for_ranking']
    
    def load_flight_data(self, filename: str) -> List[Dict]:
        """Load flight data from JSON file"""
        filepath = f"{config.RAW_DATA_DIR}/{filename}"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File not found: {filepath}")
            return []
    
    def parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    def calculate_delay_minutes(self, scheduled: Optional[str], actual: Optional[str]) -> Optional[float]:
        """
        Calculate delay in minutes between scheduled and actual time
        
        Args:
            scheduled: Scheduled time string
            actual: Actual time string
            
        Returns:
            Delay in minutes (positive for late, negative for early)
        """
        scheduled_dt = self.parse_datetime(scheduled)
        actual_dt = self.parse_datetime(actual)
        
        if not scheduled_dt or not actual_dt:
            return None
        
<<<<<<< Updated upstream
=======
        # Handle timezone mismatch: if one is naive and the other is aware,
        # make the naive one aware using the timezone from the aware one
        if scheduled_dt.tzinfo is None and actual_dt.tzinfo is not None:
            scheduled_dt = scheduled_dt.replace(tzinfo=actual_dt.tzinfo)
        elif actual_dt.tzinfo is None and scheduled_dt.tzinfo is not None:
            actual_dt = actual_dt.replace(tzinfo=scheduled_dt.tzinfo)
        
>>>>>>> Stashed changes
        delay = (actual_dt - scheduled_dt).total_seconds() / 60
        return delay
    
    def process_flights_to_dataframe(self, flights: List[Dict]) -> pd.DataFrame:
        """
        Convert flight data to pandas DataFrame with calculated metrics
        
        Args:
            flights: List of flight dictionaries
            
        Returns:
            DataFrame with processed flight data
        """
        processed_data = []
        
        for flight in flights:
            # Extract airline information
            airline_code = None
            airline_name = None
            if flight.get('prefixIATA'):
                airline_code = flight['prefixIATA']
            if flight.get('airlineCode'):
                airline_code = flight['airlineCode']
            
            # Get schedule and actual times
<<<<<<< Updated upstream
=======
            schedule_date = flight.get('scheduleDate')
>>>>>>> Stashed changes
            schedule_time = flight.get('scheduleTime')
            actual_time = flight.get('actualLandingTime') or flight.get('actualOffBlockTime')
            estimated_time = flight.get('estimatedLandingTime') or flight.get('expectedTimeOnBelt')
            
<<<<<<< Updated upstream
            # Calculate delay
            delay_minutes = self.calculate_delay_minutes(schedule_time, actual_time)
=======
            # Combine schedule_date and schedule_time for proper datetime comparison
            schedule_datetime = None
            if schedule_date and schedule_time:
                schedule_datetime = f"{schedule_date}T{schedule_time}"
            
            # Calculate delay
            delay_minutes = self.calculate_delay_minutes(schedule_datetime, actual_time)
>>>>>>> Stashed changes
            
            # Determine if flight is on time
            on_time = None
            if delay_minutes is not None:
                on_time = abs(delay_minutes) <= self.on_time_threshold
            
            # Extract route information
            route = flight.get('route', {})
            destinations = route.get('destinations', []) if isinstance(route, dict) else []
            
            processed_flight = {
                'flight_id': flight.get('id'),
                'flight_number': f"{flight.get('prefixIATA', '')}{flight.get('flightNumber', '')}",
                'airline_code': airline_code,
                'flight_direction': flight.get('flightDirection'),  # A=Arrival, D=Departure
                'schedule_date': flight.get('scheduleDate'),
                'schedule_time': schedule_time,
                'actual_time': actual_time,
                'estimated_time': estimated_time,
                'delay_minutes': delay_minutes,
                'on_time': on_time,
                'flight_status': flight.get('publicFlightState', {}).get('flightStates', [None])[0] if flight.get('publicFlightState') else None,
                'destinations': ','.join(destinations) if destinations else None,
                'aircraft_type': flight.get('aircraftType', {}).get('iataMain') if flight.get('aircraftType') else None,
                'terminal': flight.get('terminal'),
                'gate': flight.get('gate'),
                'baggage_claim': flight.get('baggageClaim', {}).get('belts', [None])[0] if flight.get('baggageClaim') else None,
            }
            
            processed_data.append(processed_flight)
        
        df = pd.DataFrame(processed_data)
        return df
    
    def calculate_airline_reliability(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate reliability metrics for each airline
        
        Args:
            df: DataFrame with processed flight data
            
        Returns:
            DataFrame with airline reliability metrics
        """
        # Filter out flights without delay information
        df_with_delays = df[df['delay_minutes'].notna()].copy()
        
        # Group by airline
        airline_stats = df_with_delays.groupby('airline_code').agg({
            'flight_id': 'count',
            'on_time': 'sum',
            'delay_minutes': ['mean', 'median', 'std', 'min', 'max']
        }).reset_index()
        
        # Flatten column names
        airline_stats.columns = [
            'airline_code',
            'total_flights',
            'on_time_flights',
            'avg_delay_minutes',
            'median_delay_minutes',
            'std_delay_minutes',
            'min_delay_minutes',
            'max_delay_minutes'
        ]
        
        # Calculate on-time percentage
        airline_stats['on_time_percentage'] = (
            airline_stats['on_time_flights'] / airline_stats['total_flights'] * 100
        )
        
        # Filter airlines with minimum number of flights
        airline_stats = airline_stats[
            airline_stats['total_flights'] >= self.min_flights
        ].copy()
        
        # Calculate reliability score (higher is better)
        # Score = on_time_percentage - (avg_delay_minutes / 10)
        airline_stats['reliability_score'] = (
            airline_stats['on_time_percentage'] - 
            (airline_stats['avg_delay_minutes'].clip(lower=0) / 10)
        )
        
        # Sort by reliability score
        airline_stats = airline_stats.sort_values('reliability_score', ascending=False)
        
        return airline_stats
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to CSV"""
        filepath = f"{config.PROCESSED_DATA_DIR}/{filename}"
        df.to_csv(filepath, index=False)
        print(f"Saved processed data to {filepath}")
    
    def generate_reliability_report(self, airline_stats: pd.DataFrame, filename: str):
        """Generate and save reliability report"""
        filepath = f"{config.REPORTS_DIR}/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("AIRLINE RELIABILITY REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Minimum flights for ranking: {self.min_flights}\n")
            f.write(f"On-time threshold: ±{self.on_time_threshold} minutes\n\n")
            
            f.write("AIRLINE RANKINGS (by Reliability Score)\n")
            f.write("-" * 80 + "\n\n")
            
            for idx, row in airline_stats.iterrows():
                f.write(f"Rank #{idx + 1}: {row['airline_code']}\n")
                f.write(f"  Reliability Score: {row['reliability_score']:.2f}\n")
                f.write(f"  Total Flights: {int(row['total_flights'])}\n")
                f.write(f"  On-Time Flights: {int(row['on_time_flights'])} ({row['on_time_percentage']:.1f}%)\n")
                f.write(f"  Average Delay: {row['avg_delay_minutes']:.1f} minutes\n")
                f.write(f"  Median Delay: {row['median_delay_minutes']:.1f} minutes\n")
                f.write(f"  Delay Range: {row['min_delay_minutes']:.1f} to {row['max_delay_minutes']:.1f} minutes\n")
                f.write("\n")
        
        print(f"Saved reliability report to {filepath}")


if __name__ == "__main__":
    # Example usage
    processor = FlightDataProcessor()
    
    # Load sample data
    today = datetime.now().strftime('%Y-%m-%d')
    
    print("=== Flight Data Processor Test ===\n")
    
    # Try to load departures
    departures = processor.load_flight_data(f"departures_{today}.json")
    
    if departures:
        print(f"Loaded {len(departures)} departure flights")
        
        # Process to DataFrame
        df = processor.process_flights_to_dataframe(departures)
        print(f"\nProcessed DataFrame shape: {df.shape}")
        print(f"\nSample processed data:")
        print(df.head())
        
        # Calculate airline reliability
        airline_stats = processor.calculate_airline_reliability(df)
        print(f"\nAirline Reliability Rankings:")
        print(airline_stats[['airline_code', 'reliability_score', 'on_time_percentage', 'total_flights']])
        
        # Save processed data
        processor.save_processed_data(df, f"processed_departures_{today}.csv")
        
        # Generate report
        processor.generate_reliability_report(airline_stats, f"reliability_report_{today}.txt")
