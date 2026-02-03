"""
Configuration module for airline reliability tracker
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Schiphol API Configuration
SCHIPHOL_CONFIG = {
    'base_url': 'https://api.schiphol.nl/public-flights',
    'app_id': os.getenv('SCHIPHOL_APP_ID', '8a1d0f4c'),
    'app_key': os.getenv('SCHIPHOL_APP_KEY', '288f3b5bf862f61e73aaea3ca936612e'),
    'resource_version': 'v4'
}

# Data storage configuration
DATA_DIR = 'data'
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Flight data collection settings
COLLECTION_SETTINGS = {
    'max_pages': 1000,  # Maximum number of pages to fetch per request
    'page_size': 20,  # Default page size from API
    'delay_between_requests': 1,  # Seconds to wait between API requests
}

# Reliability calculation settings
RELIABILITY_SETTINGS = {
    'on_time_threshold_minutes': 15,  # Flights within 15 minutes are considered on-time
    'minimum_flights_for_ranking': 10,  # Minimum flights needed to include airline in ranking
}
