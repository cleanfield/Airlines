"""
Database Module - MariaDB Integration with SSH Tunneling
Handles database connections and flight data storage
"""
import os
import socket

# Workaround for paramiko DSS key deprecation issue in sshtunnel 0.4.0
# Must be done before importing sshtunnel
import sys

# Create a dummy DSSKey class to prevent AttributeError
class DummyDSSKey:
    """Dummy class to replace deprecated DSSKey"""
    @classmethod
    def from_private_key_file(cls, *args, **kwargs):
        raise NotImplementedError("DSS keys are deprecated and not supported")

try:
    import paramiko
    
    # Replace DSSKey with dummy class if it doesn't exist
    if not hasattr(paramiko, 'DSSKey'):
        paramiko.DSSKey = DummyDSSKey
    
    # Remove DSS from preferred keys
    if hasattr(paramiko.Transport, '_preferred_keys'):
        paramiko.Transport._preferred_keys = tuple(
            k for k in paramiko.Transport._preferred_keys 
            if 'dss' not in k.lower()
        )
except Exception as e:
    print(f"Warning: Could not apply paramiko workaround: {e}")
    pass  # Continue anyway

import pymysql
from sshtunnel import SSHTunnelForwarder
from typing import Optional, List, Dict, Tuple
import pandas as pd
from datetime import datetime
import config


class DatabaseManager:
    """Manage MariaDB database connections via SSH tunnel"""
    
    def __init__(self):
        """Initialize database connection parameters from environment"""
        self.ssh_host = os.getenv('MARIA_SERVER')
        self.ssh_user = os.getenv('MARIA_SSH_USER')
        self.db_name = os.getenv('MARIA_DB')
        self.db_user = os.getenv('MARIA_DB_USER')
        self.db_password = os.getenv('MARIA_DB_PASSWORD')
        self.ssh_key_path = os.getenv('MARIA_ID_ED25519', '').strip('"')
        
        self.connection = None
        self.tunnel = None
        self.local_bind_port = None
        
    def get_connection(self):
        """
        Get the database connection.
        Ensures connection is established and alive.
        Returns the connection object which can be used as a context manager.
        """
        if not self.connection:
            self.connect()
        else:
            try:
                # Ping to check/keep alive
                self.connection.ping(reconnect=True)
            except Exception:
                # If ping fails (e.g. tunnel broken), full reconnect
                print("Connection lost, reconnecting...")
                if self.tunnel:
                    try:
                        self.tunnel.stop()
                    except:
                        pass
                    self.tunnel = None
                self.connect()
                
        return self.connection

    def __enter__(self):
        """Context manager entry - establish connection"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection"""
        self.disconnect()
        
    def connect(self):
        """Establish SSH tunnel and database connection"""
        try:
            # Check if running on the droplet or requested to skip SSH
            skip_ssh = False
            
            # Check environment variable
            if os.getenv('SKIP_SSH_TUNNEL', '').lower() == 'true':
                skip_ssh = True
                print("Skipping SSH tunnel (SKIP_SSH_TUNNEL=true)")
            
            # Check if running on the target server
            if not skip_ssh and self.ssh_host:
                try:
                    # Get all local IPs
                    hostname = socket.gethostname()
                    local_ips = socket.gethostbyname_ex(hostname)[2]
                    if self.ssh_host in local_ips:
                        skip_ssh = True
                        print(f"Skipping SSH tunnel (Running on target server {self.ssh_host})")
                except Exception as e:
                    print(f"Warning: Could not check local IPs: {e}")

            if skip_ssh:
                print(f"Connecting directly to MariaDB database '{self.db_name}'...")
                self.connection = pymysql.connect(
                    host='127.0.0.1',
                    port=3306,
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_name,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor
                )
                print("Database connection established successfully!")
                return

            print(f"Establishing SSH tunnel to {self.ssh_host}...")
            
            # Load SSH private key explicitly to avoid DSSKey deprecation issue
            import paramiko
            
            # Disable DSS keys globally to avoid deprecation warnings
            paramiko.Transport._preferred_keys = tuple(
                k for k in paramiko.Transport._preferred_keys 
                if k != 'ssh-dss'
            )
            
            ssh_pkey = None
            if self.ssh_key_path and os.path.exists(self.ssh_key_path):
                print(f"Loading SSH key from: {self.ssh_key_path}")
                
                # Get passphrase from environment if provided
                ssh_passphrase = os.getenv('MARIA_SSH_PASSPHRASE', None)
                
                try:
                    # Try Ed25519 key first
                    ssh_pkey = paramiko.Ed25519Key.from_private_key_file(
                        self.ssh_key_path, 
                        password=ssh_passphrase
                    )
                    print("✓ Loaded Ed25519 key")
                except Exception as e1:
                    try:
                        # Try RSA key
                        ssh_pkey = paramiko.RSAKey.from_private_key_file(
                            self.ssh_key_path,
                            password=ssh_passphrase
                        )
                        print("✓ Loaded RSA key")
                    except Exception as e2:
                        try:
                            # Try ECDSA key
                            ssh_pkey = paramiko.ECDSAKey.from_private_key_file(
                                self.ssh_key_path,
                                password=ssh_passphrase
                            )
                            print("✓ Loaded ECDSA key")
                        except Exception as e3:
                            print(f"Failed to load SSH key:")
                            print(f"  Ed25519: {e1}")
                            print(f"  RSA: {e2}")
                            print(f"  ECDSA: {e3}")
                            raise Exception(f"Could not load SSH key from {self.ssh_key_path}")
            
            # Create SSH tunnel with disabled DSS support
            self.tunnel = SSHTunnelForwarder(
                self.ssh_host,
                ssh_username=self.ssh_user,
                ssh_pkey=ssh_pkey,
                remote_bind_address=('127.0.0.1', 3306),
                local_bind_address=('127.0.0.1', 0),  # 0 = auto-assign port
                allow_agent=False,  # Disable SSH agent to avoid DSSKey issues
                host_pkey_directories=[],  # Don't auto-load keys
                set_keepalive=30.0  # Keep connection alive
            )
            
            self.tunnel.start()
            self.local_bind_port = self.tunnel.local_bind_port
            
            print(f"SSH tunnel established on local port {self.local_bind_port}")
            print(f"Connecting to MariaDB database '{self.db_name}'...")
            
            # Connect to database through tunnel
            self.connection = pymysql.connect(
                host='127.0.0.1',
                port=self.local_bind_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            print("Database connection established successfully!")
            
        except Exception as e:
            print(f"Error connecting to database: {e}")
            if self.tunnel:
                self.tunnel.stop()
            raise
            
    def disconnect(self):
        """Close database connection and SSH tunnel"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
            
        if self.tunnel:
            self.tunnel.stop()
            print("SSH tunnel closed")
            
    def create_tables(self):
        """Create database tables if they don't exist"""
        with self.connection.cursor() as cursor:
            # Flights table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flights (
                    id BIGINT PRIMARY KEY,
                    flight_number VARCHAR(20) NOT NULL,
                    airline_code VARCHAR(10),
                    flight_direction CHAR(1),
                    schedule_date DATE,
                    schedule_time TIME,
                    actual_time DATETIME,
                    estimated_time DATETIME,
                    delay_minutes DECIMAL(10, 2),
                    on_time BOOLEAN,
                    flight_status VARCHAR(20),
                    destinations VARCHAR(255),
                    aircraft_type VARCHAR(10),
                    terminal VARCHAR(10),
                    gate VARCHAR(10),
                    baggage_claim VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_airline_code (airline_code),
                    INDEX idx_schedule_date (schedule_date),
                    INDEX idx_flight_direction (flight_direction)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Airline statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS airline_statistics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    airline_code VARCHAR(10) NOT NULL,
                    date_range_start DATE NOT NULL,
                    date_range_end DATE NOT NULL,
                    flight_direction CHAR(1),
                    total_flights INT,
                    on_time_flights INT,
                    avg_delay_minutes DECIMAL(10, 2),
                    median_delay_minutes DECIMAL(10, 2),
                    std_delay_minutes DECIMAL(10, 2),
                    min_delay_minutes DECIMAL(10, 2),
                    max_delay_minutes DECIMAL(10, 2),
                    on_time_percentage DECIMAL(5, 2),
                    reliability_score DECIMAL(10, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_airline_stats (airline_code, date_range_start, date_range_end, flight_direction),
                    INDEX idx_airline_code (airline_code),
                    INDEX idx_date_range (date_range_start, date_range_end)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Data collection log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_collection_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    operation_type VARCHAR(20) NOT NULL,
                    flight_direction CHAR(1),
                    date_range_start DATE NOT NULL,
                    date_range_end DATE NOT NULL,
                    records_collected INT DEFAULT 0,
                    records_processed INT DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'success',
                    error_message TEXT,
                    execution_time_seconds DECIMAL(10, 2),
                    api_pages_fetched INT,
                    notes TEXT,
                    INDEX idx_collection_date (collection_date),
                    INDEX idx_date_range (date_range_start, date_range_end),
                    INDEX idx_operation (operation_type),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            self.connection.commit()
            print("Database tables created/verified successfully")
            
    def save_flights(self, df: pd.DataFrame) -> int:
        """
        Save flight data to database
        
        Args:
            df: DataFrame with flight data
            
        Returns:
            Number of rows inserted/updated
        """
        if df.empty:
            print("No flights to save")
            return 0
            
        with self.connection.cursor() as cursor:
            rows_affected = 0
            
            for _, row in df.iterrows():
                # Helper function to parse datetime strings
                def parse_datetime_for_db(dt_str):
                    """Convert ISO datetime string to MySQL-compatible format"""
                    if pd.isna(dt_str) or not dt_str:
                        return None
                    try:
                        # Parse ISO format and convert to MySQL format (YYYY-MM-DD HH:MM:SS)
                        dt = datetime.fromisoformat(str(dt_str).replace('Z', '+00:00'))
                        return dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        return None
                
                # Convert pandas values to Python types
                flight_data = {
                    'id': int(row['flight_id']) if pd.notna(row['flight_id']) else None,
                    'flight_number': str(row['flight_number']) if pd.notna(row['flight_number']) else None,
                    'airline_code': str(row['airline_code']) if pd.notna(row['airline_code']) else None,
                    'flight_direction': str(row['flight_direction']) if pd.notna(row['flight_direction']) else None,
                    'schedule_date': row['schedule_date'] if pd.notna(row['schedule_date']) else None,
                    'schedule_time': row['schedule_time'] if pd.notna(row['schedule_time']) else None,
                    'actual_time': parse_datetime_for_db(row['actual_time']),
                    'estimated_time': parse_datetime_for_db(row['estimated_time']),
                    'delay_minutes': float(row['delay_minutes']) if pd.notna(row['delay_minutes']) else None,
                    'on_time': bool(row['on_time']) if pd.notna(row['on_time']) else None,
                    'flight_status': str(row['flight_status']) if pd.notna(row['flight_status']) else None,
                    'destinations': str(row['destinations']) if pd.notna(row['destinations']) else None,
                    'aircraft_type': str(row['aircraft_type']) if pd.notna(row['aircraft_type']) else None,
                    'terminal': str(row['terminal']) if pd.notna(row['terminal']) else None,
                    'gate': str(row['gate']) if pd.notna(row['gate']) else None,
                    'baggage_claim': str(row['baggage_claim']) if pd.notna(row['baggage_claim']) else None,
                }
                
                # Insert or update flight
                cursor.execute("""
                    INSERT INTO flights (
                        id, flight_number, airline_code, flight_direction,
                        schedule_date, schedule_time, actual_time, estimated_time,
                        delay_minutes, on_time, flight_status, destinations,
                        aircraft_type, terminal, gate, baggage_claim
                    ) VALUES (
                        %(id)s, %(flight_number)s, %(airline_code)s, %(flight_direction)s,
                        %(schedule_date)s, %(schedule_time)s, %(actual_time)s, %(estimated_time)s,
                        %(delay_minutes)s, %(on_time)s, %(flight_status)s, %(destinations)s,
                        %(aircraft_type)s, %(terminal)s, %(gate)s, %(baggage_claim)s
                    )
                    ON DUPLICATE KEY UPDATE
                        actual_time = VALUES(actual_time),
                        estimated_time = VALUES(estimated_time),
                        delay_minutes = VALUES(delay_minutes),
                        on_time = VALUES(on_time),
                        flight_status = VALUES(flight_status),
                        gate = VALUES(gate),
                        updated_at = CURRENT_TIMESTAMP
                """, flight_data)
                
                rows_affected += cursor.rowcount
                
            self.connection.commit()
            print(f"Saved {rows_affected} flight records to database")
            return rows_affected
            
    def save_airline_statistics(self, df: pd.DataFrame, date_range_start: str, 
                                date_range_end: str, flight_direction: str) -> int:
        """
        Save airline statistics to database
        
        Args:
            df: DataFrame with airline statistics
            date_range_start: Start date of the range
            date_range_end: End date of the range
            flight_direction: 'A' for arrivals, 'D' for departures
            
        Returns:
            Number of rows inserted/updated
        """
        if df.empty:
            print("No airline statistics to save")
            return 0
            
        with self.connection.cursor() as cursor:
            rows_affected = 0
            
            for _, row in df.iterrows():
                stats_data = {
                    'airline_code': str(row['airline_code']),
                    'date_range_start': date_range_start,
                    'date_range_end': date_range_end,
                    'flight_direction': flight_direction,
                    'total_flights': int(row['total_flights']),
                    'on_time_flights': int(row['on_time_flights']),
                    'avg_delay_minutes': float(row['avg_delay_minutes']),
                    'median_delay_minutes': float(row['median_delay_minutes']),
                    'std_delay_minutes': float(row['std_delay_minutes']) if pd.notna(row['std_delay_minutes']) else None,
                    'min_delay_minutes': float(row['min_delay_minutes']),
                    'max_delay_minutes': float(row['max_delay_minutes']),
                    'on_time_percentage': float(row['on_time_percentage']),
                    'reliability_score': float(row['reliability_score']),
                }
                
                cursor.execute("""
                    INSERT INTO airline_statistics (
                        airline_code, date_range_start, date_range_end, flight_direction,
                        total_flights, on_time_flights, avg_delay_minutes, median_delay_minutes,
                        std_delay_minutes, min_delay_minutes, max_delay_minutes,
                        on_time_percentage, reliability_score
                    ) VALUES (
                        %(airline_code)s, %(date_range_start)s, %(date_range_end)s, %(flight_direction)s,
                        %(total_flights)s, %(on_time_flights)s, %(avg_delay_minutes)s, %(median_delay_minutes)s,
                        %(std_delay_minutes)s, %(min_delay_minutes)s, %(max_delay_minutes)s,
                        %(on_time_percentage)s, %(reliability_score)s
                    )
                    ON DUPLICATE KEY UPDATE
                        total_flights = VALUES(total_flights),
                        on_time_flights = VALUES(on_time_flights),
                        avg_delay_minutes = VALUES(avg_delay_minutes),
                        median_delay_minutes = VALUES(median_delay_minutes),
                        std_delay_minutes = VALUES(std_delay_minutes),
                        min_delay_minutes = VALUES(min_delay_minutes),
                        max_delay_minutes = VALUES(max_delay_minutes),
                        on_time_percentage = VALUES(on_time_percentage),
                        reliability_score = VALUES(reliability_score),
                        updated_at = CURRENT_TIMESTAMP
                """, stats_data)
                
                rows_affected += cursor.rowcount
                
            self.connection.commit()
            print(f"Saved {rows_affected} airline statistics records to database")
            return rows_affected
            
    def get_flights(self, start_date: Optional[str] = None, 
                   end_date: Optional[str] = None,
                   airline_code: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieve flights from database
        
        Args:
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            airline_code: Airline code filter
            
        Returns:
            DataFrame with flight data
        """
        query = "SELECT * FROM flights WHERE 1=1"
        params = {}
        
        if start_date:
            query += " AND schedule_date >= %(start_date)s"
            params['start_date'] = start_date
            
        if end_date:
            query += " AND schedule_date <= %(end_date)s"
            params['end_date'] = end_date
            
        if airline_code:
            query += " AND airline_code = %(airline_code)s"
            params['airline_code'] = airline_code
            
        query += " ORDER BY schedule_date, schedule_time"
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
        return pd.DataFrame(results)
        
    def get_airline_statistics(self, start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieve airline statistics from database
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            DataFrame with airline statistics
        """
        query = "SELECT * FROM airline_statistics WHERE 1=1"
        params = {}
        
        if start_date:
            query += " AND date_range_start >= %(start_date)s"
            params['start_date'] = start_date
            
        if end_date:
            query += " AND date_range_end <= %(end_date)s"
            params['end_date'] = end_date
            
        query += " ORDER BY reliability_score DESC"
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
        return pd.DataFrame(results)
    
    def log_collection(self, operation_type: str, flight_direction: str,
                      date_range_start: str, date_range_end: str,
                      records_collected: int = 0, records_processed: int = 0,
                      status: str = 'success', error_message: str = None,
                      execution_time: float = None, api_pages: int = None,
                      notes: str = None) -> int:
        """
        Log a data collection operation
        
        Args:
            operation_type: Type of operation ('collect', 'process', 'analyze')
            flight_direction: 'A' for arrivals, 'D' for departures
            date_range_start: Start date (YYYY-MM-DD)
            date_range_end: End date (YYYY-MM-DD)
            records_collected: Number of records collected
            records_processed: Number of records processed
            status: Operation status ('success', 'partial', 'failed')
            error_message: Error message if failed
            execution_time: Execution time in seconds
            api_pages: Number of API pages fetched
            notes: Additional notes
            
        Returns:
            Log entry ID
        """
        log_data = {
            'operation_type': operation_type,
            'flight_direction': flight_direction,
            'date_range_start': date_range_start,
            'date_range_end': date_range_end,
            'records_collected': records_collected,
            'records_processed': records_processed,
            'status': status,
            'error_message': error_message,
            'execution_time_seconds': execution_time,
            'api_pages_fetched': api_pages,
            'notes': notes
        }
        
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO data_collection_log (
                    operation_type, flight_direction, date_range_start, date_range_end,
                    records_collected, records_processed, status, error_message,
                    execution_time_seconds, api_pages_fetched, notes
                ) VALUES (
                    %(operation_type)s, %(flight_direction)s, %(date_range_start)s, %(date_range_end)s,
                    %(records_collected)s, %(records_processed)s, %(status)s, %(error_message)s,
                    %(execution_time_seconds)s, %(api_pages_fetched)s, %(notes)s
                )
            """, log_data)
            
            log_id = cursor.lastrowid
            self.connection.commit()
            
        return log_id
    
    def get_collection_log(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          operation_type: Optional[str] = None,
                          limit: int = 100) -> pd.DataFrame:
        """
        Retrieve data collection log entries
        
        Args:
            start_date: Filter by date_range_start >= this date
            end_date: Filter by date_range_end <= this date
            operation_type: Filter by operation type
            limit: Maximum number of entries to return
            
        Returns:
            DataFrame with log entries
        """
        query = "SELECT * FROM data_collection_log WHERE 1=1"
        params = {}
        
        if start_date:
            query += " AND date_range_start >= %(start_date)s"
            params['start_date'] = start_date
            
        if end_date:
            query += " AND date_range_end <= %(end_date)s"
            params['end_date'] = end_date
            
        if operation_type:
            query += " AND operation_type = %(operation_type)s"
            params['operation_type'] = operation_type
            
        query += " ORDER BY collection_date DESC LIMIT %(limit)s"
        params['limit'] = limit
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            
        return pd.DataFrame(results)



if __name__ == "__main__":
    # Test database connection
    print("=== Database Connection Test ===\n")
    
    try:
        with DatabaseManager() as db:
            print("\nCreating tables...")
            db.create_tables()
            
            print("\nDatabase test completed successfully!")
            
    except Exception as e:
        print(f"\nDatabase test failed: {e}")
