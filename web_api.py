
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
except Exception as e:
    print(f"Error loading destination mapping: {e}")

@app.route('/')
def index():
    """Serve the main web page"""
    return send_from_directory('web', 'index.html')

@app.route('/logs')
def logs():
    """Serve the logs page"""
    return send_from_directory('web', 'logs.html')

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
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get airline statistics from database
        airlines = get_airline_statistics(start_date, end_date, flight_type, min_flights)
        
        # Calculate total flights
        total_flights = sum(airline['totalFlights'] for airline in airlines)
        
        return jsonify({
            'airlines': airlines,
            'totalFlights': total_flights,
            'lastUpdate': datetime.now().isoformat(),
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

def get_airline_statistics(start_date, end_date, flight_type='all', min_flights=10):
    """
    Query database for airline statistics
    """
    conn = db.get_connection()
    with conn.cursor() as cursor:
        
        if flight_type == 'departures':
            direction_filter = "AND flight_direction = 'D'"
        elif flight_type == 'arrivals':
            direction_filter = "AND flight_direction = 'A'"
        else:
            direction_filter = ""
        
        query = f"""
            SELECT 
                airline_code,
                COUNT(*) as total_flights,
                SUM(CASE WHEN on_time = 1 THEN 1 ELSE 0 END) as on_time_flights,
                AVG(delay_minutes) as avg_delay,
                MIN(delay_minutes) as min_delay,
                MAX(delay_minutes) as max_delay
            FROM flights
            WHERE schedule_date BETWEEN %s AND %s
                AND actual_time IS NOT NULL
                {direction_filter}
            GROUP BY airline_code
            HAVING COUNT(*) >= %s
            ORDER BY 
                (SUM(CASE WHEN on_time = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) - (AVG(delay_minutes) / 10) DESC
        """
        
        cursor.execute(query, (start_date, end_date, min_flights))
        results = cursor.fetchall()
        
        airlines = []
        for row in results:
            airline_iata = row['airline_code']
            # Lookup airline name, default to code if not found
            airline_name = AIRLINE_MAPPING.get(str(airline_iata), airline_iata)
            
            total_flights = row['total_flights']
            on_time_flights = float(row['on_time_flights']) if row['on_time_flights'] else 0
            avg_delay = float(row['avg_delay']) if row['avg_delay'] else 0
            min_delay = float(row['min_delay']) if row['min_delay'] else 0
            max_delay = float(row['max_delay']) if row['max_delay'] else 0
            # direction = row['flight_direction'] # Removed as it's not in SELECT anymore
            
            # Calculate metrics
            on_time_percentage = (on_time_flights / total_flights * 100) if total_flights > 0 else 0
            reliability_score = on_time_percentage - (avg_delay / 10)
            
            # Calculate trend
            trend = calculate_trend(cursor, airline_iata, start_date, days=(end_date - start_date).days)
            
            # Determine flight type string
            type_str = flight_type
            if type_str == 'all':
                type_str = 'mixed'
            
            airlines.append({
                'code': airline_iata,
                'name': airline_name,
                'totalFlights': total_flights,
                'onTimeFlights': on_time_flights,
                'onTimePercentage': round(on_time_percentage, 2),
                'avgDelay': round(avg_delay, 1),
                'minDelay': round(min_delay, 1),
                'maxDelay': round(max_delay, 1),
                'reliabilityScore': round(reliability_score, 2),
                'trend': round(trend, 2),
                'flightType': type_str
            })
        
        return airlines

def calculate_trend(cursor, airline_iata, current_start_date, days=30):
    try:
        prev_end_date = current_start_date
        prev_start_date = prev_end_date - timedelta(days=days)
        
        query = """
            SELECT 
                COUNT(*) as total_flights,
                SUM(CASE WHEN on_time = 1 THEN 1 ELSE 0 END) as on_time_flights,
                AVG(delay_minutes) as avg_delay
            FROM flights
            WHERE airline_code = %s
                AND schedule_date BETWEEN %s AND %s
                AND actual_time IS NOT NULL
        """
        
        cursor.execute(query, (airline_iata, prev_start_date, prev_end_date))
        result = cursor.fetchone()
        
        if result and result['total_flights'] >= 5:
            total_flights = result['total_flights']
            on_time_flights = float(result['on_time_flights']) if result['on_time_flights'] else 0
            avg_delay = float(result['avg_delay']) if result['avg_delay'] else 0
            
            prev_on_time_pct = (on_time_flights / total_flights * 100) if total_flights > 0 else 0
            prev_score = prev_on_time_pct - (avg_delay / 10)
            
            cursor.execute(query, (airline_iata, current_start_date, current_start_date + timedelta(days=days)))
            current_result = cursor.fetchone()
            
            if current_result and current_result['total_flights'] > 0:
                curr_total = current_result['total_flights']
                curr_on_time = float(current_result['on_time_flights']) if current_result['on_time_flights'] else 0
                curr_delay = float(current_result['avg_delay']) if current_result['avg_delay'] else 0
                
                curr_on_time_pct = (curr_on_time / curr_total * 100) if curr_total > 0 else 0
                curr_score = curr_on_time_pct - (curr_delay / 10)
                
                if prev_score > 0:
                    trend = ((curr_score - prev_score) / prev_score) * 100
                    return trend
        
        return 0.0
        
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

if __name__ == '__main__':
    port = int(os.getenv('WEB_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    print(f"Starting Airlines Reliability Web Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
