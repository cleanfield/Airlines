"""
Main Application - Airline Reliability Tracker
Collects flight data from airport APIs and ranks airlines by reliability
"""
import argparse
from datetime import datetime, timedelta
from schiphol_api import SchipholAPIClient
from data_processor import FlightDataProcessor
from visualizer import ReliabilityVisualizer
from database import DatabaseManager


def collect_data(days_back: int = 0, days_forward: int = 0, max_pages: int = None):
    """
    Collect flight data from Schiphol API
    
    Args:
        days_back: Number of days in the past to collect
        days_forward: Number of days in the future to collect
        max_pages: Maximum pages to fetch per day
    """
    import time
    
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
    dep_start_time = time.time()
    dep_status = 'success'
    dep_error = None
    
    try:
        departures = client.get_flights_by_date_range(
            start_date=start_date,
            end_date=end_date,
            flight_direction='D'
        )
        
        if departures:
            filename = f"departures_{start_date}_to_{end_date}.json"
            client.save_flights_to_file(departures, filename)
    except Exception as e:
        departures = []
        dep_status = 'failed'
        dep_error = str(e)
        print(f"Error collecting departures: {e}")
    
    dep_execution_time = time.time() - dep_start_time
    
    # Log departures collection to database
    try:
        with DatabaseManager() as db:
            db.create_tables()  # Ensure tables exist
            db.log_collection(
                operation_type='collect',
                flight_direction='D',
                date_range_start=start_date,
                date_range_end=end_date,
                records_collected=len(departures),
                status=dep_status,
                error_message=dep_error,
                execution_time=dep_execution_time,
                notes=f"Collected via Schiphol API (days_back={days_back}, days_forward={days_forward})"
            )
    except Exception as e:
        print(f"Warning: Could not log to database: {e}")
    
    # Collect arrivals
    print("\n--- COLLECTING ARRIVALS ---")
    arr_start_time = time.time()
    arr_status = 'success'
    arr_error = None
    
    try:
        arrivals = client.get_flights_by_date_range(
            start_date=start_date,
            end_date=end_date,
            flight_direction='A'
        )
        
        if arrivals:
            filename = f"arrivals_{start_date}_to_{end_date}.json"
            client.save_flights_to_file(arrivals, filename)
    except Exception as e:
        arrivals = []
        arr_status = 'failed'
        arr_error = str(e)
        print(f"Error collecting arrivals: {e}")
    
    arr_execution_time = time.time() - arr_start_time
    
    # Log arrivals collection to database
    try:
        with DatabaseManager() as db:
            db.log_collection(
                operation_type='collect',
                flight_direction='A',
                date_range_start=start_date,
                date_range_end=end_date,
                records_collected=len(arrivals),
                status=arr_status,
                error_message=arr_error,
                execution_time=arr_execution_time,
                notes=f"Collected via Schiphol API (days_back={days_back}, days_forward={days_forward})"
            )
    except Exception as e:
        print(f"Warning: Could not log to database: {e}")
    
    print("\n" + "=" * 80)
    print(f"DATA COLLECTION COMPLETE")
    print(f"Total departures: {len(departures)}")
    print(f"Total arrivals: {len(arrivals)}")
    print("=" * 80)
    
    return departures, arrivals



def process_data(flight_type: str, date_range: str, save_to_db: bool = True):
    """
    Process collected flight data
    
    Args:
        flight_type: 'departures' or 'arrivals'
        date_range: Date range string (e.g., '2024-01-01_to_2024-01-07')
        save_to_db: Whether to save data to database (default: True)
    """
    import time
    
    start_time = time.time()
    process_status = 'success'
    process_error = None
    records_processed = 0
    
    print("=" * 80)
    print(f"PROCESSING {flight_type.upper()} DATA")
    print("=" * 80)
    
    processor = FlightDataProcessor()
    
    try:
        # Load data
        filename = f"{flight_type}_{date_range}.json"
        flights = processor.load_flight_data(filename)
        
        if not flights:
            print(f"No data found for {filename}")
            process_status = 'failed'
            process_error = f"No data found for {filename}"
            return None
        
        print(f"\nLoaded {len(flights)} flights")
        
        # Process to DataFrame
        df = processor.process_flights_to_dataframe(flights)
        records_processed = len(df)
        print(f"Processed {records_processed} flight records")
        
        # Save processed data to CSV
        output_filename = f"processed_{flight_type}_{date_range}.csv"
        processor.save_processed_data(df, output_filename)
        
        # Calculate airline reliability
        airline_stats = processor.calculate_airline_reliability(df)
        print(f"\nCalculated reliability for {len(airline_stats)} airlines")
        
        # Save airline stats to CSV
        stats_filename = f"airline_stats_{flight_type}_{date_range}.csv"
        processor.save_processed_data(airline_stats, stats_filename)
        
        # Generate report
        report_filename = f"reliability_report_{flight_type}_{date_range}.txt"
        processor.generate_reliability_report(airline_stats, report_filename)
        
        # Save to database if requested
        if save_to_db:
            try:
                print("\n--- SAVING TO DATABASE ---")
                with DatabaseManager() as db:
                    # Create tables if they don't exist
                    db.create_tables()
                    
                    # Save flight data
                    db.save_flights(df)
                    
                    # Extract date range for statistics
                    dates = date_range.split('_to_')
                    start_date = dates[0]
                    end_date = dates[1] if len(dates) > 1 else dates[0]
                    flight_dir = 'D' if flight_type == 'departures' else 'A'
                    
                    # Save airline statistics
                    if not airline_stats.empty:
                        db.save_airline_statistics(airline_stats, start_date, end_date, flight_dir)
                        
                print("Database save completed successfully!")
                
            except Exception as e:
                print(f"Warning: Could not save to database: {e}")
                print("Data has been saved to CSV files only.")
                process_status = 'partial'
                process_error = f"Database save failed: {str(e)}"
        
    except Exception as e:
        print(f"Error processing data: {e}")
        process_status = 'failed'
        process_error = str(e)
        df = None
        airline_stats = None
    
    execution_time = time.time() - start_time
    
    # Log processing to database
    try:
        dates = date_range.split('_to_')
        start_date = dates[0]
        end_date = dates[1] if len(dates) > 1 else dates[0]
        flight_dir = 'D' if flight_type == 'departures' else 'A'
        
        with DatabaseManager() as db:
            db.log_collection(
                operation_type='process',
                flight_direction=flight_dir,
                date_range_start=start_date,
                date_range_end=end_date,
                records_processed=records_processed,
                status=process_status,
                error_message=process_error,
                execution_time=execution_time,
                notes=f"Processed {flight_type} data, saved_to_db={save_to_db}"
            )
    except Exception as e:
        print(f"Warning: Could not log processing to database: {e}")
    
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
    process_parser.add_argument('--no-db', action='store_true',
                               help='Skip saving to database (CSV only)')
    
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
    full_parser.add_argument('--no-db', action='store_true',
                            help='Skip saving to database (CSV only)')
    
    # Database test command
    db_test_parser = subparsers.add_parser('db-test', help='Test database connection')
    
    args = parser.parse_args()
    
    if args.command == 'collect':
        collect_data(args.days_back, args.days_forward, args.max_pages)
    elif args.command == 'process':
        process_data(args.flight_type, args.date_range, save_to_db=not args.no_db)
    elif args.command == 'visualize':
        visualize_data(args.flight_type, args.date_range)
    elif args.command == 'analyze':
        run_full_analysis(args.days_back, args.days_forward, args.max_pages)
    elif args.command == 'db-test':
        print("=" * 80)
        print("DATABASE CONNECTION TEST")
        print("=" * 80)
        try:
            with DatabaseManager() as db:
                print("\nCreating/verifying tables...")
                db.create_tables()
                print("\n[OK] Database connection successful!")
                print("=" * 80)
        except Exception as e:
            print(f"\n[ERROR] Database connection failed: {e}")
            print("=" * 80)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
