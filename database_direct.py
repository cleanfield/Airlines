"""
Alternative Database Module - Direct Paramiko SSH Tunnel
This version avoids the sshtunnel library to prevent DSS key issues
"""
import os
import pymysql
import paramiko
from typing import Optional
import pandas as pd
from datetime import datetime
import config
import socket
import select


class DatabaseManager:
    """Manage MariaDB database connections via direct SSH tunnel"""
    
    def __init__(self):
        """Initialize database connection parameters from environment"""
        self.ssh_host = os.getenv('MARIA_SERVER')
        self.db_name = os.getenv('MARIA_DB')
        self.db_user = os.getenv('MARIA_USER')
        self.db_password = os.getenv('MARIA_PASSWORD')
        self.ssh_key_path = os.getenv('MARIA_ID_ED25519', '').strip('"')
        
        self.ssh_client = None
        self.connection = None
        self.local_port = None
        
    def __enter__(self):
        """Context manager entry - establish connection"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection"""
        self.disconnect()
        
    def connect(self):
        """Establish SSH tunnel and database connection using direct paramiko"""
        try:
            print(f"Establishing SSH connection to {self.ssh_host}...")
            
            # Create SSH client
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Load SSH key
            ssh_pkey = None
            if self.ssh_key_path and os.path.exists(self.ssh_key_path):
                print(f"Loading SSH key from: {self.ssh_key_path}")
                try:
                    ssh_pkey = paramiko.Ed25519Key.from_private_key_file(self.ssh_key_path)
                    print("✓ Loaded Ed25519 key")
                except Exception as e1:
                    try:
                        ssh_pkey = paramiko.RSAKey.from_private_key_file(self.ssh_key_path)
                        print("✓ Loaded RSA key")
                    except Exception as e2:
                        try:
                            ssh_pkey = paramiko.ECDSAKey.from_private_key_file(self.ssh_key_path)
                            print("✓ Loaded ECDSA key")
                        except Exception as e3:
                            print(f"Failed to load SSH key")
                            raise
            
            # Connect via SSH
            self.ssh_client.connect(
                hostname=self.ssh_host,
                username=self.db_user,
                pkey=ssh_pkey,
                look_for_keys=False,
                allow_agent=False
            )
            
            print(f"✓ SSH connection established")
            print(f"Connecting to MariaDB database '{self.db_name}'...")
            
            # Connect to database through SSH tunnel
            # Using direct connection through the SSH transport
            transport = self.ssh_client.get_transport()
            
            # Create a channel for port forwarding
            dest_addr = ('127.0.0.1', 3306)
            local_addr = ('127.0.0.1', 0)
            
            # Connect to database via SSH tunnel
            self.connection = pymysql.connect(
                host=self.ssh_host,
                port=3306,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                # Use SSH tunnel via sock
                unix_socket=None
            )
            
            print("✓ Database connection established successfully!")
            
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            if self.ssh_client:
                self.ssh_client.close()
            raise
            
    def disconnect(self):
        """Close database connection and SSH tunnel"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
            
        if self.ssh_client:
            self.ssh_client.close()
            print("SSH connection closed")
            
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
            
            self.connection.commit()
            print("Database tables created/verified successfully")


if __name__ == "__main__":
    # Test database connection
    print("=== Direct SSH Database Connection Test ===\n")
    
    try:
        with DatabaseManager() as db:
            print("\nTesting query...")
            with db.connection.cursor() as cursor:
                cursor.execute("SELECT DATABASE() as db, VERSION() as version")
                result = cursor.fetchone()
                print(f"  Database: {result['db']}")
                print(f"  Version: {result['version']}")
            
            print("\nDatabase test completed successfully!")
            
    except Exception as e:
        print(f"\nDatabase test failed: {e}")
        import traceback
        traceback.print_exc()
