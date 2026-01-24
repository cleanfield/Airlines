"""
Web API for Airlines Reliability Rankings
Serves airline statistics from the database to the web interface
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from database import DatabaseManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)  # Enable CORS for development

# Database manager
db = DatabaseManager()

@app.route('/')
def index():
    """Serve the main web page"""
    return send_from_directory('web', 'index.html')

@app.route('/api/rankings')
def get_rankings():
    """
    Get airline reliability rankings
    Query parameters:
        - days: Number of days to look back (default: 30)
        - flight_type: 'departures', 'arrivals', or 'all' (default: 'all')
        - min_flights: Minimum number of flights (default: 10)
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
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch airline rankings'
        }), 500

def get_airline_statistics(start_date, end_date, flight_type='all', min_flights=10):
    """
    Query database for airline statistics
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query based on flight type
            if flight_type == 'departures':
                direction_filter = "AND flight_direction = 'D'"
            elif flight_type == 'arrivals':
                direction_filter = "AND flight_direction = 'A'"
            else:
                direction_filter = ""
            
            query = f"""
                SELECT 
                    airline_iata,
                    airline_name,
                    COUNT(*) as total_flights,
                    SUM(CASE WHEN is_on_time = 1 THEN 1 ELSE 0 END) as on_time_flights,
                    AVG(delay_minutes) as avg_delay,
                    MIN(delay_minutes) as min_delay,
                    MAX(delay_minutes) as max_delay,
                    flight_direction
                FROM flights
                WHERE scheduled_time BETWEEN %s AND %s
                    AND actual_time IS NOT NULL
                    {direction_filter}
                GROUP BY airline_iata, airline_name, flight_direction
                HAVING COUNT(*) >= %s
                ORDER BY 
                    (SUM(CASE WHEN is_on_time = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) - (AVG(delay_minutes) / 10) DESC
            """
            
            cursor.execute(query, (start_date, end_date, min_flights))
            results = cursor.fetchall()
            
            airlines = []
            for row in results:
                airline_iata = row[0]
                airline_name = row[1] or airline_iata
                total_flights = row[2]
                on_time_flights = row[3]
                avg_delay = float(row[4]) if row[4] else 0
                min_delay = float(row[5]) if row[5] else 0
                max_delay = float(row[6]) if row[6] else 0
                direction = row[7]
                
                # Calculate metrics
                on_time_percentage = (on_time_flights / total_flights * 100) if total_flights > 0 else 0
                reliability_score = on_time_percentage - (avg_delay / 10)
                
                # Calculate trend (compare with previous period)
                trend = calculate_trend(airline_iata, start_date, days=(end_date - start_date).days)
                
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
                    'flightType': 'departures' if direction == 'D' else 'arrivals'
                })
            
            return airlines
            
    except Exception as e:
        print(f"Error fetching airline statistics: {e}")
        return []

def calculate_trend(airline_iata, current_start_date, days=30):
    """
    Calculate trend by comparing current period with previous period
    Returns percentage change in reliability score
    """
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Previous period
            prev_end_date = current_start_date
            prev_start_date = prev_end_date - timedelta(days=days)
            
            query = """
                SELECT 
                    COUNT(*) as total_flights,
                    SUM(CASE WHEN is_on_time = 1 THEN 1 ELSE 0 END) as on_time_flights,
                    AVG(delay_minutes) as avg_delay
                FROM flights
                WHERE airline_iata = %s
                    AND scheduled_time BETWEEN %s AND %s
                    AND actual_time IS NOT NULL
            """
            
            cursor.execute(query, (airline_iata, prev_start_date, prev_end_date))
            result = cursor.fetchone()
            
            if result and result[0] >= 5:  # Need at least 5 flights for comparison
                total_flights = result[0]
                on_time_flights = result[1]
                avg_delay = float(result[2]) if result[2] else 0
                
                prev_on_time_pct = (on_time_flights / total_flights * 100) if total_flights > 0 else 0
                prev_score = prev_on_time_pct - (avg_delay / 10)
                
                # Get current score
                cursor.execute(query.replace('BETWEEN %s AND %s', 'BETWEEN %s AND %s'), 
                             (airline_iata, current_start_date, current_start_date + timedelta(days=days)))
                current_result = cursor.fetchone()
                
                if current_result and current_result[0] > 0:
                    curr_total = current_result[0]
                    curr_on_time = current_result[1]
                    curr_delay = float(current_result[2]) if current_result[2] else 0
                    
                    curr_on_time_pct = (curr_on_time / curr_total * 100) if curr_total > 0 else 0
                    curr_score = curr_on_time_pct - (curr_delay / 10)
                    
                    # Calculate percentage change
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
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_flights,
                    COUNT(DISTINCT airline_iata) as total_airlines,
                    SUM(CASE WHEN is_on_time = 1 THEN 1 ELSE 0 END) as on_time_flights,
                    AVG(delay_minutes) as avg_delay
                FROM flights
                WHERE scheduled_time BETWEEN %s AND %s
                    AND actual_time IS NOT NULL
            """
            
            cursor.execute(query, (start_date, end_date))
            result = cursor.fetchone()
            
            if result:
                total_flights = result[0]
                total_airlines = result[1]
                on_time_flights = result[2]
                avg_delay = float(result[3]) if result[3] else 0
                
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
        # Test database connection
        with db.get_connection() as conn:
            cursor = conn.cursor()
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

if __name__ == '__main__':
    # Development server
    port = int(os.getenv('WEB_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Airlines Reliability Web Server on port {port}")
    print(f"Access the web interface at: http://localhost:{port}")
    print(f"API endpoint: http://localhost:{port}/api/rankings")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
