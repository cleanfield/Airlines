
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
                # Format times
                sched_dt = datetime.combine(row['schedule_date'], (datetime.min + row['schedule_time']).time()) if row['schedule_date'] and row['schedule_time'] else None
                
                flights.append({
                    'flightNumber': row['flight_number'],
                    'date': row['schedule_date'].strftime('%Y-%m-%d') if row['schedule_date'] else None,
                    'schedTime': str(row['schedule_time']) if row['schedule_time'] else None,
                    'actualTime': row['actual_time'].strftime('%H:%M') if row['actual_time'] else None,
                    'delay': float(row['delay_minutes']) if row['delay_minutes'] is not None else 0,
                    'status': row['flight_status'],
                    'destination': row['destinations'],
                    'direction': row['flight_direction'],
                    'terminal': row['terminal'],
                    'gate': row['gate'],
                    'onTime': bool(row['on_time'])
                })
                
            airline_name = AIRLINE_MAPPING.get(airline_code, airline_code)
            
            return jsonify({
                'airline': {'code': airline_code, 'name': airline_name},
                'flights': flights,
                'count': len(flights)
            })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch flight details'
        }), 500
