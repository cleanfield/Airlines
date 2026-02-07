
"""
Web API for Airlines Reliability Rankings
Serves airline statistics from the database to the web interface
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
from database import DatabaseManager
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)  # Enable CORS for development

# Database manager
db = DatabaseManager()


# Load airline mapping
AIRLINE_MAPPING = {}
try:
    mapping_path = os.path.join(os.path.dirname(__file__), 'airline_mapping.json')
    if os.path.exists(mapping_path):
        with open(mapping_path, 'r', encoding='utf-8') as f:
            AIRLINE_MAPPING = json.load(f)
        print(f"Loaded {len(AIRLINE_MAPPING)} airlines from mapping file")
    else:
        print(f"Warning: Airline mapping file not found at {mapping_path}")
except Exception as e:
    print(f"Error loading airline mapping: {e}")

# Load destination mapping
DESTINATION_MAPPING = {}
try:

    dest_mapping_path = os.path.join(os.path.dirname(__file__), 'destination_mapping.json')
    if os.path.exists(dest_mapping_path):
        with open(dest_mapping_path, 'r', encoding='utf-8') as f:
            DESTINATION_MAPPING = json.load(f)
        print(f"Loaded {len(DESTINATION_MAPPING)} destinations from mapping file")
    else:
        print(f"Warning: Destination mapping file not found at {dest_mapping_path}")
        
    # Load full destination details for drilldown
    dest_full_path = os.path.join(os.path.dirname(__file__), 'destinations_full.json')
    if os.path.exists(dest_full_path):
        with open(dest_full_path, 'r', encoding='utf-8') as f:
            DESTINATIONS_FULL = json.load(f)
        print(f"Loaded {len(DESTINATIONS_FULL)} full destinations")
    else:
        print(f"Warning: Full destination details not found at {dest_full_path}")
        DESTINATIONS_FULL = []
        
except Exception as e:
    print(f"Error loading destination mapping: {e}")
    DESTINATIONS_FULL = []

@app.route('/api/destinations')
def get_destinations():
    """Get destinations that actually have flights from Schiphol"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # 1. Get unique destination codes from actual flight data
            query = """
                SELECT DISTINCT destinations 
                FROM flights 
                WHERE destinations IS NOT NULL 
                  AND destinations != ''
                  AND flight_direction = 'D'
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Extract all unique airport codes (handle comma-separated)
            airport_codes = set()
            for row in results:
                dest_str = row['destinations']
                if dest_str:
                    # Split by comma and clean up
                    codes = [code.strip() for code in str(dest_str).split(',')]
                    airport_codes.update(codes)
            
            if not airport_codes:
                return jsonify([])

            # 2. Get details for these airports from relational tables
            # Prepare placeholders for IN clause
            placeholders = ', '.join(['%s'] * len(airport_codes))
            # Convert set to list for params
            params = list(airport_codes)
            
            query = f"""
                SELECT 
                    a.iata_code as code, 
                    a.name, 
                    c.name as country, 
                    co.name as continent
                FROM airports a
                LEFT JOIN countries c ON a.country_id = c.id
                LEFT JOIN continents co ON c.continent_id = co.id
                WHERE a.iata_code IN ({placeholders})
                ORDER BY a.name
            """
            
            cursor.execute(query, params)
            dest_rows = cursor.fetchall()
            
            destinations = []
            found_codes = set()
            
            for row in dest_rows:
                code = row['code']
                found_codes.add(code)
                destinations.append({
                    'code': code,
                    'name': row['name'] or code,
                    'country': row['country'] or 'Unknown',
                    'continent': row['continent'] or 'Unknown'
                })
            
            # Add any codes that weren't found in our DB tables (fallback)
            for code in airport_codes:
                if code not in found_codes:
                    # Try to look it up in the old JSON fallback if loaded, or just basic entry
                    fallback = {'code': code, 'name': code, 'country': 'Unknown', 'continent': 'Unknown'}
                    # If we still have DESTINATIONS_FULL loaded, maybe check there? 
                    # But ideally the DB should be the source.
                    destinations.append(fallback)
            
            # Sort by name
            destinations.sort(key=lambda x: x['name'])
            
            return jsonify(destinations)
            
    except Exception as e:
        print(f"Error getting destinations: {e}")
        traceback.print_exc()
        # Fallback to empty list or old method if catastrophe
        return jsonify([])


@app.route('/api/airports')
def get_airports():
    """Get all airports from the database"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.id, 
                    a.iata_code, 
                    a.name as airport_name,
                    c.name as country_name,
                    co.name as continent_name,
                    a.latitude, 
                    a.longitude, 
                    a.created_at
                FROM airports a
                LEFT JOIN countries c ON a.country_id = c.id
                LEFT JOIN continents co ON c.continent_id = co.id
                ORDER BY a.name
            """)
            results = cursor.fetchall()
            
            airports = []
            for row in results:
                airports.append({
                    'id': row['id'],
                    'name': row['airport_name'],
                    'iataCode': row['iata_code'],
                    'country': row['country_name'],
                    'continent': row['continent_name'],
                    'latitude': float(row['latitude']) if row['latitude'] else None,
                    'longitude': float(row['longitude']) if row['longitude'] else None,
                    'createdAt': row['created_at'].isoformat() if row['created_at'] else None
                })
            
            return jsonify(airports)
            
    except Exception as e:
        print(f"Error getting airports: {e}")
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch airports'
        }), 500


@app.route('/')
def index():
    """Serve the main web page"""
    return send_from_directory('web', 'index.html')

@app.route('/logs')
def logs():
    """Serve the logs page"""
    return send_from_directory('web', 'logs.html')

@app.route('/airports')
def airports():
    """Serve the airports page"""
    return send_from_directory('web', 'airports.html')

@app.route('/destinations')
def destinations():
    """Serve the destinations statistics page"""
    return send_from_directory('web', 'destinations.html')

@app.route('/aircraft')
def aircraft():
    """Serve the aircraft statistics page"""
    return send_from_directory('web', 'aircraft.html')


def get_airline_statistics(start_date, end_date, flight_type='all', min_flights=10, destination=None, country=None, continent=None):
    """
    Get statistics for all airlines within the date range
    """
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # 1. Get aggregated stats
            params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            
            query = """
                SELECT 
                    airline_code,
                    COUNT(*) as total_flights,
                    SUM(CASE WHEN on_time = 1 THEN 1 ELSE 0 END) as on_time_flights,
                    AVG(delay_minutes) as avg_delay
                FROM flights
                WHERE schedule_date BETWEEN %s AND %s
                    AND actual_time IS NOT NULL
            """
            
            if flight_type == 'departures':
                query += " AND flight_direction = 'D'"
            elif flight_type == 'arrivals':
                query += " AND flight_direction = 'A'"
                
            if destination:
                # Match exact airport code (handles comma-separated destinations)
                query += " AND (destinations = %s OR destinations LIKE %s OR destinations LIKE %s OR destinations LIKE %s)"
                params.extend([
                    destination,                    # Exact match
                    f"{destination},%",            # Start
                    f"%,{destination}",            # End
                    f"%,{destination},%"           # Middle
                ])
            elif country:
                # Filter by country name
                query += """ AND destinations IN (
                    SELECT a.iata_code FROM airports a 
                    JOIN countries c ON a.country_id = c.id 
                    WHERE c.name = %s
                )"""
                params.append(country)
            elif continent:
                # Filter by continent name
                query += """ AND destinations IN (
                    SELECT a.iata_code FROM airports a 
                    JOIN countries c ON a.country_id = c.id 
                    JOIN continents co ON c.continent_id = co.id
                    WHERE co.name = %s
                )"""
                params.append(continent)

                
            query += " GROUP BY airline_code HAVING total_flights >= %s"
            params.append(min_flights)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            airlines = []
            for row in results:
                airline_code = row['airline_code']
                airline_name = AIRLINE_MAPPING.get(airline_code, airline_code)
                
                total_flights = row['total_flights']
                on_time_flights = float(row['on_time_flights']) if row['on_time_flights'] else 0
                avg_delay = float(row['avg_delay']) if row['avg_delay'] else 0
                
                on_time_percentage = (on_time_flights / total_flights * 100)
                reliability_score = on_time_percentage - (avg_delay / 10)
                
                # 2. Calculate trend
                # Use the same start date for trend calculation
                trend = calculate_trend(cursor, airline_code, params[0])
                
                airlines.append({
                    'code': airline_code,
                    'name': airline_name,
                    'totalFlights': total_flights,
                    'onTimePercentage': round(on_time_percentage, 1),
                    'avgDelay': round(avg_delay, 1),
                    'reliabilityScore': round(reliability_score, 1),
                    'trend': round(trend, 2)
                })
                
            # Sort by reliability score desc
            airlines.sort(key=lambda x: x['reliabilityScore'], reverse=True)
            
            return airlines
    except Exception as e:
        print(f"Error getting airline statistics: {e}")
        traceback.print_exc()
        return []

@app.route('/api/rankings')
def get_rankings():
    """
    Get airline reliability rankings
    """
    try:
        # Get query parameters
        days = request.args.get('days', default=30, type=int)
        flight_type = request.args.get('flight_type', default='all', type=str)
        min_flights = request.args.get('min_flights', default=10, type=int)
        destination = request.args.get('destination', default=None, type=str)
        country = request.args.get('country', default=None, type=str)
        continent = request.args.get('continent', default=None, type=str)
        
        # Override min_flights when filtering by specific destination/country/continent
        # to ensure we show all carriers flying that route/region
        if destination or country or continent:
            min_flights = 1

        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get airline statistics from database
        airlines = get_airline_statistics(start_date, end_date, flight_type, min_flights, destination, country, continent)

        
        # Calculate total flights
        total_flights = sum(airline['totalFlights'] for airline in airlines)
        
        return jsonify({
            'airlines': airlines,
            'totalFlights': total_flights,
            'lastUpdate': datetime.now().isoformat(),
            'firstUpdate': get_first_update_date(),
            'dateRange': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'filters': {
                'flightType': flight_type,
                'minFlights': min_flights
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch airline rankings'
        }), 500

def get_first_update_date():
    """Get the date of the earliest flight record"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT MIN(schedule_date) as first_date FROM flights")
            result = cursor.fetchone()
            if result and result['first_date']:
                return result['first_date'].isoformat()
    except Exception as e:
        print(f"Error getting first update date: {e}")
    return None

def calculate_trend(cursor, airline_iata, current_start_date, days=30):
    """
    Calculate trend using linear regression slope of daily scores
    Returns: Average daily change in score (slope)
    """
    try:
        # Get daily statistics for the period
        end_date = datetime.now()
        # Ensure we cover the full range up to today for the trend
        # current_start_date is passed from the main function (end_date - days)
        
        query = """
            SELECT 
                schedule_date,
                COUNT(*) as total_flights,
                SUM(CASE WHEN on_time = 1 THEN 1 ELSE 0 END) as on_time_flights,
                AVG(delay_minutes) as avg_delay
            FROM flights
            WHERE airline_code = %s
                AND schedule_date BETWEEN %s AND %s
                AND actual_time IS NOT NULL
            GROUP BY schedule_date
            ORDER BY schedule_date ASC
        """
        
        cursor.execute(query, (airline_iata, current_start_date, end_date))
        results = cursor.fetchall()
        
        if not results or len(results) < 2:
            return 0.0
            
        x_values = [] # Days since start
        y_values = [] # Scores
        
        start_ts = results[0]['schedule_date'].toordinal()
        
        for row in results:
            if row['total_flights'] < 1:
                continue
                
            total_flights = row['total_flights']
            on_time_flights = float(row['on_time_flights']) if row['on_time_flights'] else 0
            avg_delay = float(row['avg_delay']) if row['avg_delay'] else 0
            
            on_time_pct = (on_time_flights / total_flights * 100)
            score = on_time_pct - (avg_delay / 10)
            
            # X is days relative to start of data points
            day_idx = row['schedule_date'].toordinal() - start_ts
            
            x_values.append(day_idx)
            y_values.append(score)
            
        if len(x_values) < 2:
            return 0.0
            
        # Calculate Linear Regression Slope (m)
        # m = (N * sum(xy) - sum(x) * sum(y)) / (N * sum(x^2) - sum(x)^2)
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x_sq = sum(x * x for x in x_values)
        
        denominator = (n * sum_x_sq - sum_x * sum_x)
        
        if denominator == 0:
            return 0.0
            
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        return slope
        
    except Exception as e:
        print(f"Error calculating trend: {e}")
        return 0.0

@app.route('/api/stats')
def get_overall_stats():
    """Get overall statistics"""
    try:
        days = request.args.get('days', default=30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conn = db.get_connection()
        with conn.cursor() as cursor:
            
            query = """
                SELECT 
                    COUNT(*) as total_flights,
                    COUNT(DISTINCT airline_code) as total_airlines,
                    SUM(CASE WHEN on_time = 1 THEN 1 ELSE 0 END) as on_time_flights,
                    AVG(delay_minutes) as avg_delay
                FROM flights
                WHERE schedule_date BETWEEN %s AND %s
                    AND actual_time IS NOT NULL
            """
            
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            
            if result:
                total_flights = result['total_flights']
                total_airlines = result['total_airlines']
                on_time_flights = float(result['on_time_flights']) if result['on_time_flights'] else 0
                avg_delay = float(result['avg_delay']) if result['avg_delay'] else 0
                
                on_time_percentage = (on_time_flights / total_flights * 100) if total_flights > 0 else 0
                
                return jsonify({
                    'totalFlights': total_flights,
                    'totalAirlines': total_airlines,
                    'onTimePercentage': round(on_time_percentage, 2),
                    'avgDelay': round(avg_delay, 1),
                    'dateRange': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat(),
                        'days': days
                    }
                })
            
            return jsonify({'error': 'No data available'}), 404
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch statistics'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/api/logs/collection')
def get_collection_logs():
    """Get recent data collection logs"""
    try:
        limit = request.args.get('limit', default=50, type=int)
        
        conn = db.get_connection()
        with conn.cursor() as cursor:
            
            query = """
                SELECT 
                    id,
                    collection_date,
                    operation_type,
                    flight_direction,
                    date_range_start,
                    date_range_end,
                    records_collected,
                    records_processed,
                    status,
                    error_message,
                    execution_time_seconds,
                    notes
                FROM data_collection_log
                ORDER BY collection_date DESC
                LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            result = cursor.fetchall()
            
            logs = []
            for row in result:
                logs.append({
                    'id': row['id'],
                    'date': row['collection_date'].isoformat() if row.get('collection_date') else None,
                    'operation': row['operation_type'],
                    'direction': row['flight_direction'],
                    'dateRange': f"{row['date_range_start']} to {row['date_range_end']}",
                    'collected': row['records_collected'],
                    'processed': row['records_processed'],
                    'status': row['status'],
                    'error': row['error_message'],
                    'executionTime': float(row['execution_time_seconds']) if row.get('execution_time_seconds') else 0,
                    'notes': row['notes']
                })
                
            return jsonify({'logs': logs})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch collection logs'
        }), 500

@app.route('/api/airlines/<airline_code>/flights')
def get_airline_flights(airline_code):
    """
    Get detailed flight list for a specific airline
    """
    try:
        days = request.args.get('days', default=1, type=int)
        flight_type = request.args.get('flight_type', default='all', type=str)
        limit = request.args.get('limit', default=100, type=int)
        destination = request.args.get('destination', default=None, type=str)
        country = request.args.get('country', default=None, type=str)
        continent = request.args.get('continent', default=None, type=str)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # Build query
            query = """
                SELECT 
                    flight_number,
                    schedule_date,
                    schedule_time,
                    actual_time,
                    estimated_time,
                    delay_minutes,
                    on_time,
                    flight_status,
                    destinations,
                    flight_direction,
                    terminal,
                    gate
                FROM flights
                WHERE airline_code = %s
                    AND schedule_date BETWEEN %s AND %s
            """
            params = [airline_code, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
            
            if flight_type == 'departures':
                query += " AND flight_direction = 'D'"
            elif flight_type == 'arrivals':
                query += " AND flight_direction = 'A'"
                
            if destination:
                # Match exact airport code (handles comma-separated destinations)
                query += " AND (destinations = %s OR destinations LIKE %s OR destinations LIKE %s OR destinations LIKE %s)"
                params.extend([
                    destination,                    # Exact match
                    f"{destination},%",            # Start
                    f"%,{destination}",            # End
                    f"%,{destination},%"           # Middle
                ])
            elif country:
                # Filter by country name
                query += """ AND destinations IN (
                    SELECT a.iata_code FROM airports a 
                    JOIN countries c ON a.country_id = c.id 
                    WHERE c.name = %s
                )"""
                params.append(country)
            elif continent:
                # Filter by continent name
                query += """ AND destinations IN (
                    SELECT a.iata_code FROM airports a 
                    JOIN countries c ON a.country_id = c.id 
                    JOIN continents co ON c.continent_id = co.id
                    WHERE co.name = %s
                )"""
                params.append(continent)
                
            query += " ORDER BY schedule_date DESC, schedule_time DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            flights = []
            for row in results:
                try:
                    # Format times
                    sched_dt = None
                    if row['schedule_date'] and row['schedule_time']:
                        # Handle potential timedelta vs time type difference
                        t = row['schedule_time']
                        if hasattr(t, 'seconds'): # timedelta
                             # Convert timedelta to time
                             seconds = t.total_seconds()
                             hours = int(seconds // 3600)
                             minutes = int((seconds % 3600) // 60)
                             timestamp = (datetime.min + t).time()
                             sched_dt = datetime.combine(row['schedule_date'], timestamp)
                        else: # time object
                             sched_dt = datetime.combine(row['schedule_date'], t)

                    # Lookup destination name
                    dest_code = row['destinations']
                    dest_name = dest_code
                    if dest_code:
                        try:
                            # Split by comma if multiple destinations
                            codes = [c.strip() for c in str(dest_code).split(',')]
                            names = [DESTINATION_MAPPING.get(c, c) for c in codes]
                            dest_name = ", ".join(names)
                        except Exception:
                            dest_name = str(dest_code) # Fallback

                    # Handle actual_time safely
                    actual_time_str = None
                    if row.get('actual_time'):
                        at = row['actual_time']
                        if hasattr(at, 'strftime'):
                             actual_time_str = at.strftime('%H:%M')
                        elif hasattr(at, 'seconds'): # timedelta
                             actual_time_str = (datetime.min + at).time().strftime('%H:%M')
                        else:
                             actual_time_str = str(at)

                    flights.append({
                        'flightNumber': row['flight_number'],
                        'date': row['schedule_date'].strftime('%Y-%m-%d') if row['schedule_date'] else None,
                        'schedTime': sched_dt.strftime('%H:%M') if sched_dt else "",
                        'actualTime': actual_time_str,
                        'delay': float(row['delay_minutes']) if row['delay_minutes'] is not None else 0,
                        'status': row['flight_status'],
                        'destination': dest_name,
                        'direction': row['flight_direction'],
                        'terminal': row['terminal'],
                        'gate': row['gate'],
                        'onTime': bool(row['on_time'])
                    })
                except Exception as row_e:
                    with open('api_error.log', 'a') as f:
                        f.write(f"Error processing row {row.get('flight_number')}: {row_e}\n")
                    print(f"Error processing row {row.get('flight_number')}: {row_e}")
                    continue
                
            airline_name = AIRLINE_MAPPING.get(airline_code, airline_code)
            
            return jsonify({
                'airline': {'code': airline_code, 'name': airline_name},
                'flights': flights,
                'count': len(flights)
            })
            
    except Exception as e:
        with open('api_error.log', 'w') as f:
            f.write(f"Top Level API Error: {str(e)}\n")
            traceback.print_exc(file=f)
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch flight details'
        }), 500

@app.route('/api/stats/destinations')
def get_destination_stats():
    """Get top destinations statistics"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # Get period from query params (default: week)
            period = request.args.get('period', default='week', type=str)
            limit = request.args.get('limit', default=10, type=int)
            
            end_date = datetime.now()
            if period == 'day':
                start_date = end_date - timedelta(days=1)
            elif period == 'month':
                start_date = end_date - timedelta(days=30)
            else: # week
                start_date = end_date - timedelta(days=7)
                
            # Query for top destinations
            # Note: We are filtering for Departures ('D') as destination stats usually imply where people are going
            query = """
                SELECT 
                    destinations,
                    COUNT(*) as flight_count
                FROM flights
                WHERE schedule_date BETWEEN %s AND %s
                  AND flight_direction = 'D'
                  AND destinations IS NOT NULL
                  AND destinations != ''
                GROUP BY destinations
                ORDER BY flight_count DESC
                LIMIT %s
            """
            
            cursor.execute(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), limit))
            results = cursor.fetchall()
            
            stats = []
            for row in results:
                # Handle comma-separated destinations
                dest_code_raw = row['destinations']
                codes = [c.strip() for c in str(dest_code_raw).split(',')]
                
                # Get names
                names = []
                for code in codes:
                    # Try destination mapping first
                    if code in DESTINATION_MAPPING:
                        names.append(DESTINATION_MAPPING[code])
                    else:
                        names.append(code)
                
                name_display = " / ".join(names)
                
                stats.append({
                    'code': dest_code_raw,
                    'name': name_display,
                    'count': row['flight_count']
                })
                
            return jsonify({
                'period': period,
                'stats': stats,
                'dateRange': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch destination statistics'
        }), 500

@app.route('/api/stats/aircraft')
def get_aircraft_stats():
    """Get top aircraft types statistics"""
    try:
        conn = db.get_connection()
        with conn.cursor() as cursor:
            # Get period from query params (default: week)
            period = request.args.get('period', default='week', type=str)
            limit = request.args.get('limit', default=10, type=int)
            
            end_date = datetime.now()
            if period == 'day':
                start_date = end_date - timedelta(days=1)
            elif period == 'month':
                start_date = end_date - timedelta(days=30)
            else: # week
                start_date = end_date - timedelta(days=7)
                
            # Query for top aircraft types with descriptions
            query = """
                SELECT 
                    f.aircraft_type,
                    a.long_description,
                    COUNT(*) as flight_count
                FROM flights f
                LEFT JOIN aircraft_types a ON TRIM(f.aircraft_type) COLLATE utf8mb4_unicode_ci = a.iata_sub
                WHERE f.schedule_date BETWEEN %s AND %s
                  AND f.aircraft_type IS NOT NULL
                  AND f.aircraft_type != ''
                GROUP BY f.aircraft_type, a.long_description
                ORDER BY flight_count DESC
                LIMIT %s
            """
            
            cursor.execute(query, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), limit))
            results = cursor.fetchall()
            
            stats = []
            for row in results:
                # Use description if available, else code
                name = row['long_description'] if row['long_description'] else row['aircraft_type']
                
                stats.append({
                    'code': row['aircraft_type'],
                    'name': name,
                    'count': row['flight_count']
                })
                
            return jsonify({
                'period': period,
                'stats': stats,
                'dateRange': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch aircraft statistics'
        }), 500

@app.route('/api/stats/aircraft/<aircraft_code>/airlines')
def get_aircraft_airlines(aircraft_code):
    """Get airline distribution for a specific aircraft type"""
    try:
        # Get period to match the main stats
        period = request.args.get('period', default='week', type=str)
        
        end_date = datetime.now()
        if period == 'day':
            start_date = end_date - timedelta(days=1)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        else: # week
            start_date = end_date - timedelta(days=7)

        conn = db.get_connection()
        with conn.cursor() as cursor:
            # Query grouped by airline
            # Match TRIM(aircraft_type) to handle whitespace inconsistencies
            query = """
                SELECT 
                    airline_code,
                    COUNT(*) as flight_count
                FROM flights
                WHERE TRIM(aircraft_type) = %s
                  AND schedule_date BETWEEN %s AND %s
                  AND airline_code IS NOT NULL
                GROUP BY airline_code
                ORDER BY flight_count DESC
                LIMIT 20
            """
            
            # Since aircraft_code comes from URL, we verify/trim it too? 
            # The query uses TRIM(db_column) = param. So if param="EMJ", it matches "EMJ ".
            cursor.execute(query, (aircraft_code, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            results = cursor.fetchall()
            
            stats = []
            for row in results:
                code = row['airline_code']
                name = AIRLINE_MAPPING.get(code, code)
                stats.append({
                    'code': code,
                    'name': name,
                    'count': row['flight_count']
                })
                
            return jsonify({
                'aircraft': aircraft_code,
                'stats': stats,
                'period': period,
                'dateRange': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch airline breakdown'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    print(f"Starting Airlines Reliability Web Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)