# Airline Reliability Tracker

A Python application that collects flight arrival and departure data from airport APIs and ranks airlines based on their reliability by comparing scheduled vs actual times.
<<<<<<< Updated upstream

## Features

=======
Users can use this application to track the reliability of airlines and make informed decisions about their travel plans.

## Features

**Timezone Handling** - Handles timezone mismatches between scheduled and actual times

**Reliability Scoring** - Calculates reliability metrics including:

- On-time performance percentage
- Average delays
- Reliability scores
- Delay distributions

**Data Collection** - Collects flight data from airport APIs with date range support

**Data Processing** - Processes flight data with date range support

**Use mariadb to store flight data**
Use tables so data has to be retrieved only once.

**Use ssh to connect to remote Maria db server**
Details in .env file:
Server name : MARIA_SERVER
SSH user : MARIA_SSH_USER
Private key : MARIA_ID_ED25519
Public key : MARIA_ID_ED25519_PUB
Key passphrase :  MARIA_ID_ED25519_PASSPHRASE

Database name : MARIA_DB
Database user : MARIA_DB_USER
Database password : MARIA_DB_PASSWORD

**Data Visualization** - Visualizes flight data with date range support

**Data Analysis** - Analyzes flight data with date range support

**Data Reporting** - Reports flight data with date range support

>>>>>>> Stashed changes
✈️ **Multi-Airport Support** - Currently supports Schiphol Airport API (v4), designed to easily add more airports

📊 **Comprehensive Analysis** - Calculates reliability metrics including:

- On-time performance percentage
- Average delays
- Reliability scores
- Delay distributions

📈 **Rich Visualizations** - Generates professional charts:

- Airline reliability rankings
- On-time performance scatter plots
- Delay distribution histograms
- Daily performance trends

🔄 **Automated Data Collection** - Collect historical and future flight data with date range support

📝 **Detailed Reports** - Text-based reports with complete airline statistics

## Project Structure

<<<<<<< Updated upstream
```
=======
``` text
>>>>>>> Stashed changes
Airlines/
├── main.py                 # Main application with CLI
├── schiphol_api.py        # Schiphol Airport API client
├── data_processor.py      # Data processing and reliability calculations
├── visualizer.py          # Chart and graph generation
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # API credentials (not in git)
├── .env.example          # Template for credentials
├── README.md             # This file
├── USAGE.md              # Detailed usage guide
└── data/                 # Data storage
    ├── raw/              # Raw JSON from APIs
    ├── processed/        # Processed CSV files
    └── reports/          # Reports and visualizations
```

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

The Schiphol API credentials are already configured in `.env`. If you need to update them or add other airports, edit the `.env` file.

### 3. Run Analysis

Collect and analyze today's flight data:

```bash
python main.py analyze
```

Analyze the past week:

```bash
python main.py analyze --days-back 7
```

## Usage Examples

### Collect Flight Data

```bash
# Collect today's flights
python main.py collect

# Collect past 7 days
python main.py collect --days-back 7

# Collect next 3 days (scheduled flights)
python main.py collect --days-forward 3
```

### Process Data

```bash
# Process departures
python main.py process departures 2024-01-22_to_2024-01-22

# Process arrivals
python main.py process arrivals 2024-01-22_to_2024-01-22
```

### Generate Visualizations

```bash
# Create charts for departures
python main.py visualize departures 2024-01-22_to_2024-01-22
```

### Full Analysis (Recommended)

```bash
# Complete workflow: collect, process, and visualize
python main.py analyze --days-back 7
```

## How It Works

### 1. Data Collection (`schiphol_api.py`)

- Connects to Schiphol Flight API v4
- Fetches flight data with pagination support
- Retrieves scheduled and actual times
- Saves raw data as JSON files

### 2. Data Processing (`data_processor.py`)

- Parses flight records
- Calculates delay in minutes (actual - scheduled)
- Determines on-time status (within ±15 minutes)
- Aggregates statistics by airline
- Computes reliability scores

### 3. Visualization (`visualizer.py`)

- Creates bar charts of airline rankings
- Generates scatter plots of performance metrics
- Produces delay distribution histograms
- Shows daily performance trends

### 4. Reliability Scoring

**Reliability Score Formula:**

<<<<<<< Updated upstream
```
=======
``` python
>>>>>>> Stashed changes
reliability_score = on_time_percentage - (avg_delay_minutes / 10)
```

**On-Time Definition:**

- Flight is on-time if actual time is within ±15 minutes of scheduled time
- Configurable in `config.py`

**Minimum Flights:**

- Airlines need at least 10 flights to be included in rankings
- Prevents unreliable statistics from small samples

## Output Files

### Reports Directory (`data/reports/`)

- **reliability_report_*.txt** - Text report with airline rankings and statistics
- **airline_rankings_*.png** - Bar chart of top 20 airlines by reliability score
- **on_time_performance_*.png** - Scatter plot showing on-time % vs average delay
- **delay_distribution_*.png** - Histogram of flight delays
- **daily_performance_*.png** - Line chart of daily trends

### Processed Data (`data/processed/`)

- **processed_departures_*.csv** - Individual flight records with calculated delays
- **airline_stats_*.csv** - Aggregated airline statistics

### Raw Data (`data/raw/`)

- **departures_*.json** - Raw departure data from API
- **arrivals_*.json** - Raw arrival data from API

## Configuration

Edit `config.py` to customize:

```python
# Reliability calculation settings
RELIABILITY_SETTINGS = {
    'on_time_threshold_minutes': 15,  # On-time window
    'minimum_flights_for_ranking': 10,  # Min flights for ranking
}

# Data collection settings
COLLECTION_SETTINGS = {
    'max_pages': 10,  # Max pages per request
    'delay_between_requests': 1,  # Seconds between API calls
}
```

## API Information

### Schiphol Airport API

- **Base URL:** `https://api.schiphol.nl/public-flights`
- **Version:** v4
- **Documentation:** Included in `Schiphol Developer Portal.html`
- **Rate Limits:** Adjust `delay_between_requests` if needed

### Required Headers

<<<<<<< Updated upstream
```
=======
``` text
>>>>>>> Stashed changes
Accept: application/json
app_id: <your_app_id>
app_key: <your_app_key>
ResourceVersion: v4
```

## Adding More Airports

To support additional airports:

1. Create a new API client (e.g., `heathrow_api.py`)
2. Implement the same interface as `SchipholAPIClient`
3. Add credentials to `.env`
4. Update `main.py` to support the new airport

Example structure:

```python
class HeathrowAPIClient:
    def get_flights(self, ...):
        # Implementation
        pass
    
    def get_all_flights(self, ...):
        # Implementation
        pass
```

## Requirements

- Python 3.7+
- requests
- pandas
- matplotlib
- seaborn
- python-dotenv
- schedule

Install all with:

```bash
pip install -r requirements.txt
```

## Troubleshooting

### No Data Collected

- Check internet connection
- Verify API credentials in `.env`
- Check API rate limits
- Try reducing `--max-pages`

### Processing Errors

- Ensure data collection completed successfully
- Check that JSON files exist in `data/raw/`
- Verify date range format: `YYYY-MM-DD_to_YYYY-MM-DD`

### Visualization Errors

- Ensure data processing completed successfully
- Check that CSV files exist in `data/processed/`
- Verify matplotlib and seaborn are installed

## Future Enhancements

- [ ] Add more airport APIs (Heathrow, JFK, etc.)
- [ ] Web dashboard for real-time monitoring
- [ ] Email alerts for significant delays
- [ ] Historical trend analysis
- [ ] Machine learning predictions
- [ ] API for programmatic access
- [ ] Database storage (SQLite/PostgreSQL)
- [ ] Scheduled automatic data collection

## Contributing

To contribute:

1. Add support for new airport APIs
2. Improve reliability calculations
3. Create additional visualizations
4. Enhance documentation
5. Report bugs or suggest features

## License

This project is for educational and research purposes. Please respect the terms of service of the airport APIs you use.

## Contact

For Schiphol API support: <api-support@schiphol.nl>

## Acknowledgments

- Schiphol Airport for providing the Flight API
- Airport operators worldwide for making flight data accessible

---

**Note:** This application is designed to help analyze airline reliability. Always verify critical flight information through official airline and airport channels.
