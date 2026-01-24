"""
Main Application - Airline Reliability Tracker
Collects flight data from airport APIs and ranks airlines by reliability
"""
import argparse
from datetime import datetime, timedelta
from schiphol_api import SchipholAPIClient
from data_processor import FlightDataProcessor
from visualizer import ReliabilityVisualizer


def collect_data(days_back: int = 0, days_forward: int = 0, max_pages: int = None):
    """
    Collect flight data from Schiphol API
    
    Args:
        days_back: Number of days in the past to collect
        days_forward: Number of days in the future to collect
        max_pages: Maximum pages to fetch per day
    """
    print("=" * 80)
    print("COLLECTING FLIGHT DATA FROM SCHIPHOL AIRPORT")
    print("=" * 80)
    
    client = SchipholAPIClient()
    
    # Calculate date range
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=days_forward)).strftime('%Y-%m-%d')
    
    print(f"\nDate range: {start_date} to {end_date}")
    print(f"Max pages per day: {max_pages or 'unlimited'}\n")
    
    # Collect departures
    print("\n--- COLLECTING DEPARTURES ---")
    departures = client.get_flights_by_date_range(
        start_date=start_date,
        end_date=end_date,
        flight_direction='D'
    )
    
    if departures:
        filename = f"departures_{start_date}_to_{end_date}.json"
        client.save_flights_to_file(departures, filename)
    
    # Collect arrivals
    print("\n--- COLLECTING ARRIVALS ---")
    arrivals = client.get_flights_by_date_range(
        start_date=start_date,
        end_date=end_date,
        flight_direction='A'
    )
    
    if arrivals:
        filename = f"arrivals_{start_date}_to_{end_date}.json"
        client.save_flights_to_file(arrivals, filename)
    
    print("\n" + "=" * 80)
    print(f"DATA COLLECTION COMPLETE")
    print(f"Total departures: {len(departures)}")
    print(f"Total arrivals: {len(arrivals)}")
    print("=" * 80)
    
    return departures, arrivals


def process_data(flight_type: str, date_range: str):
    """
    Process collected flight data
    
    Args:
        flight_type: 'departures' or 'arrivals'
        date_range: Date range string (e.g., '2024-01-01_to_2024-01-07')
    """
    print("=" * 80)
    print(f"PROCESSING {flight_type.upper()} DATA")
    print("=" * 80)
    
    processor = FlightDataProcessor()
    
    # Load data
    filename = f"{flight_type}_{date_range}.json"
    flights = processor.load_flight_data(filename)
    
    if not flights:
        print(f"No data found for {filename}")
        return None
    
    print(f"\nLoaded {len(flights)} flights")
    
    # Process to DataFrame
    df = processor.process_flights_to_dataframe(flights)
    print(f"Processed {len(df)} flight records")
    
    # Save processed data
    output_filename = f"processed_{flight_type}_{date_range}.csv"
    processor.save_processed_data(df, output_filename)
    
    # Calculate airline reliability
    airline_stats = processor.calculate_airline_reliability(df)
    print(f"\nCalculated reliability for {len(airline_stats)} airlines")
    
    # Save airline stats
    stats_filename = f"airline_stats_{flight_type}_{date_range}.csv"
    processor.save_processed_data(airline_stats, stats_filename)
    
    # Generate report
    report_filename = f"reliability_report_{flight_type}_{date_range}.txt"
    processor.generate_reliability_report(airline_stats, report_filename)
    
    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    
    return df, airline_stats


def visualize_data(flight_type: str, date_range: str):
    """
    Create visualizations for processed data
    
    Args:
        flight_type: 'departures' or 'arrivals'
        date_range: Date range string
    """
    print("=" * 80)
    print(f"GENERATING VISUALIZATIONS FOR {flight_type.upper()}")
    print("=" * 80)
    
    import pandas as pd
    import config
    
    processor = FlightDataProcessor()
    visualizer = ReliabilityVisualizer()
    
    # Load processed data
    try:
        df = pd.read_csv(f"{config.PROCESSED_DATA_DIR}/processed_{flight_type}_{date_range}.csv")
        airline_stats = pd.read_csv(f"{config.PROCESSED_DATA_DIR}/airline_stats_{flight_type}_{date_range}.csv")
        
        print(f"\nLoaded {len(df)} flights and {len(airline_stats)} airline statistics")
        
        # Generate visualizations
        print("\nGenerating charts...")
        
        visualizer.plot_airline_rankings(
            airline_stats,
            f"airline_rankings_{flight_type}_{date_range}.png"
        )
        
        visualizer.plot_on_time_performance(
            airline_stats,
            f"on_time_performance_{flight_type}_{date_range}.png"
        )
        
        visualizer.plot_delay_distribution(
            df,
            output_file=f"delay_distribution_{flight_type}_{date_range}.png"
        )
        
        if len(df['schedule_date'].unique()) > 1:
            visualizer.plot_daily_performance(
                df,
                output_file=f"daily_performance_{flight_type}_{date_range}.png"
            )
        
        print("\n" + "=" * 80)
        print("VISUALIZATION COMPLETE")
        print("=" * 80)
        
    except FileNotFoundError as e:
        print(f"Error: Could not find processed data files. Run process command first.")
        print(f"Details: {e}")


def run_full_analysis(days_back: int = 0, days_forward: int = 0, max_pages: int = None):
    """
    Run complete analysis: collect, process, and visualize
    
    Args:
        days_back: Number of days in the past to collect
        days_forward: Number of days in the future to collect
        max_pages: Maximum pages to fetch per day
    """
    # Calculate date range string
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    end_date = (datetime.now() + timedelta(days=days_forward)).strftime('%Y-%m-%d')
    date_range = f"{start_date}_to_{end_date}"
    
    # Step 1: Collect data
    departures, arrivals = collect_data(days_back, days_forward, max_pages)
    
    # Step 2: Process departures
    if departures:
        df_dep, stats_dep = process_data('departures', date_range)
        
        # Step 3: Visualize departures
        if df_dep is not None:
            visualize_data('departures', date_range)
    
    # Step 4: Process arrivals
    if arrivals:
        df_arr, stats_arr = process_data('arrivals', date_range)
        
        # Step 5: Visualize arrivals
        if df_arr is not None:
            visualize_data('arrivals', date_range)
    
    print("\n" + "=" * 80)
    print("FULL ANALYSIS COMPLETE!")
    print(f"Check the 'data/reports' directory for results")
    print("=" * 80)


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description='Airline Reliability Tracker - Collect and analyze flight data'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect flight data')
    collect_parser.add_argument('--days-back', type=int, default=0,
                               help='Number of days in the past to collect')
    collect_parser.add_argument('--days-forward', type=int, default=0,
                               help='Number of days in the future to collect')
    collect_parser.add_argument('--max-pages', type=int, default=None,
                               help='Maximum pages to fetch per day')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process collected data')
    process_parser.add_argument('flight_type', choices=['departures', 'arrivals'],
                               help='Type of flights to process')
    process_parser.add_argument('date_range', help='Date range (e.g., 2024-01-01_to_2024-01-07)')
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Create visualizations')
    viz_parser.add_argument('flight_type', choices=['departures', 'arrivals'],
                           help='Type of flights to visualize')
    viz_parser.add_argument('date_range', help='Date range (e.g., 2024-01-01_to_2024-01-07)')
    
    # Full analysis command
    full_parser = subparsers.add_parser('analyze', help='Run full analysis (collect, process, visualize)')
    full_parser.add_argument('--days-back', type=int, default=0,
                            help='Number of days in the past to collect')
    full_parser.add_argument('--days-forward', type=int, default=0,
                            help='Number of days in the future to collect')
    full_parser.add_argument('--max-pages', type=int, default=None,
                            help='Maximum pages to fetch per day')
    
    args = parser.parse_args()
    
    if args.command == 'collect':
        collect_data(args.days_back, args.days_forward, args.max_pages)
    elif args.command == 'process':
        process_data(args.flight_type, args.date_range)
    elif args.command == 'visualize':
        visualize_data(args.flight_type, args.date_range)
    elif args.command == 'analyze':
        run_full_analysis(args.days_back, args.days_forward, args.max_pages)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
