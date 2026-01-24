# Airline Reliability Tracker - Usage Guide

## Overview

This application collects flight data from airport APIs (starting with Schiphol) and ranks airlines based on their reliability by comparing scheduled vs actual arrival/departure times.

## Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

1. Set up environment variables:

```bash
# Copy the example file
copy .env.example .env

# Edit .env with your API credentials (Schiphol credentials are already included)
```

## Quick Start

### Run Full Analysis (Recommended for first-time users)

Collect, process, and visualize data for today:

```bash
python main.py analyze
```

Collect data for the past 7 days:

```bash
python main.py analyze --days-back 7
```

Collect data for the next 3 days (scheduled flights):

```bash
python main.py analyze --days-forward 3
```

## Individual Commands

### 1. Collect Flight Data

Collect data from Schiphol API:

```bash
# Collect today's flights
python main.py collect

# Collect past 7 days
python main.py collect --days-back 7

# Collect next 3 days (scheduled)
python main.py collect --days-forward 3

# Limit to 5 pages per day (faster, less data)
python main.py collect --days-back 7 --max-pages 5
```

### 2. Process Collected Data

Process the collected flight data:

```bash
# Process departures
python main.py process departures 2024-01-22_to_2024-01-22

# Process arrivals
python main.py process arrivals 2024-01-22_to_2024-01-22
```

### 3. Generate Visualizations

Create charts and graphs:

```bash
# Visualize departure data
python main.py visualize departures 2024-01-22_to_2024-01-22

# Visualize arrival data
python main.py visualize arrivals 2024-01-22_to_2024-01-22
```

## Understanding the Output

### Data Files

All data is stored in the `data/` directory:

- **data/raw/**: Raw JSON data from APIs
  - `departures_YYYY-MM-DD_to_YYYY-MM-DD.json`
  - `arrivals_YYYY-MM-DD_to_YYYY-MM-DD.json`

- **data/processed/**: Processed CSV files
  - `processed_departures_*.csv` - Individual flight records
  - `airline_stats_departures_*.csv` - Airline reliability statistics

- **data/reports/**: Reports and visualizations
  - `reliability_report_*.txt` - Text report with rankings
  - `airline_rankings_*.png` - Bar chart of top airlines
  - `on_time_performance_*.png` - Scatter plot of performance
  - `delay_distribution_*.png` - Histogram of delays
  - `daily_performance_*.png` - Time series of daily trends

### Reliability Metrics

- **Reliability Score**: Combined metric (higher is better)
  - Based on on-time percentage and average delay
  - Formula: `on_time_percentage - (avg_delay_minutes / 10)`

- **On-Time Performance**: Percentage of flights within ±15 minutes of schedule

- **Average Delay**: Mean delay in minutes (negative = early, positive = late)

## Configuration

Edit `config.py` to customize:

- **On-time threshold**: Default is 15 minutes
- **Minimum flights for ranking**: Default is 10 flights
- **Data collection limits**: Max pages, delays between requests

## Examples

### Example 1: Weekly Analysis

```bash
# Collect and analyze the past week
python main.py analyze --days-back 7
```

This will:

1. Collect all flights from the past 7 days
2. Process both departures and arrivals
3. Generate reliability reports
4. Create visualizations

### Example 2: Quick Daily Check

```bash
# Just collect today's data
python main.py collect

# Process it
python main.py process departures 2024-01-22_to_2024-01-22

# View the report
type data\reports\reliability_report_departures_2024-01-22_to_2024-01-22.txt
```

### Example 3: Using Individual Modules

You can also run modules directly:

```python
# Test the API client
python schiphol_api.py

# Test the data processor
python data_processor.py

# Test the visualizer
python visualizer.py
```

## Troubleshooting

### No data collected

- Check your internet connection
- Verify API credentials in `.env`
- Try reducing `--max-pages` to avoid rate limits

### Processing errors

- Ensure you've collected data first
- Check that the date range matches your collected data
- Verify JSON files exist in `data/raw/`

### Visualization errors

- Ensure you've processed data first
- Check that CSV files exist in `data/processed/`
- Install matplotlib and seaborn if missing

## Adding More Airports

To add support for other airports:

1. Create a new API client (e.g., `heathrow_api.py`)
2. Follow the same pattern as `schiphol_api.py`
3. Add credentials to `.env`
4. Update `main.py` to support the new airport

## API Rate Limits

The Schiphol API has rate limits. If you encounter errors:

- Reduce `--max-pages`
- Increase delay in `config.py` (`delay_between_requests`)
- Collect data in smaller date ranges

## Support

For issues with:

- **Schiphol API**: <api-support@schiphol.nl>
- **This application**: Check the code comments and README.md
