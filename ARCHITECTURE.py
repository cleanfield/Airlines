"""
System Architecture Diagram (ASCII)
"""

ARCHITECTURE = """
================================================================================
AIRLINE RELIABILITY TRACKER - SYSTEM ARCHITECTURE
================================================================================

┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA COLLECTION                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  Schiphol API    │
    │   (v4 REST)      │
    └────────┬─────────┘
             │
             │ HTTP GET with headers
             │ (app_id, app_key, ResourceVersion)
             │
             ▼
    ┌──────────────────┐
    │ schiphol_api.py  │
    │  - get_flights() │
    │  - pagination    │
    │  - date ranges   │
    └────────┬─────────┘
             │
             │ Save JSON
             │
             ▼
    ┌──────────────────┐
    │  data/raw/*.json │
    │  - departures    │
    │  - arrivals      │
    └──────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA PROCESSING                                 │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  data/raw/*.json │
    └────────┬─────────┘
             │
             │ Load & Parse
             │
             ▼
    ┌──────────────────────┐
    │ data_processor.py    │
    │  - parse_datetime()  │
    │  - calculate_delay() │
    │  - determine_ontime()│
    │  - aggregate_stats() │
    └────────┬─────────────┘
             │
             │ Save CSV
             │
             ▼
    ┌──────────────────────┐
    │ data/processed/*.csv │
    │  - flight records    │
    │  - airline stats     │
    └──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                            VISUALIZATION & REPORTS                           │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐
    │ data/processed/*.csv │
    └────────┬─────────────┘
             │
             │ Load Data
             │
             ▼
    ┌──────────────────────┐
    │   visualizer.py      │
    │  - rankings chart    │
    │  - scatter plot      │
    │  - histogram         │
    │  - trend lines       │
    └────────┬─────────────┘
             │
             │ Generate
             │
             ▼
    ┌──────────────────────┐
    │ data/reports/*.png   │
    │ data/reports/*.txt   │
    │  - charts            │
    │  - text reports      │
    └──────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              MAIN APPLICATION                                │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────┐
    │                         main.py                              │
    │                                                              │
    │  Commands:                                                   │
    │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
    │  │  collect   │  │  process   │  │ visualize  │            │
    │  └────────────┘  └────────────┘  └────────────┘            │
    │                                                              │
    │  ┌──────────────────────────────────────────┐              │
    │  │           analyze (all-in-one)           │              │
    │  │  collect → process → visualize           │              │
    │  └──────────────────────────────────────────┘              │
    └──────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   .env       │     │  config.py   │     │ .gitignore   │
    │              │     │              │     │              │
    │ - API keys   │────▶│ - Settings   │     │ - Excludes   │
    │ - Secrets    │     │ - Thresholds │     │ - Sensitive  │
    └──────────────┘     └──────────────┘     └──────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────┘

    API → JSON → DataFrame → Calculations → CSV → Charts/Reports
     │      │         │            │          │         │
     │      │         │            │          │         └─ PNG images
     │      │         │            │          └─────────── Text reports
     │      │         │            └────────────────────── Airline stats
     │      │         └─────────────────────────────────── Flight records
     │      └───────────────────────────────────────────── Raw data
     └──────────────────────────────────────────────────── Schiphol API


┌─────────────────────────────────────────────────────────────────────────────┐
│                              RELIABILITY METRICS                             │
└─────────────────────────────────────────────────────────────────────────────┘

    Input: Scheduled Time, Actual Time
           │
           ▼
    Calculate: Delay = Actual - Scheduled (in minutes)
           │
           ▼
    Determine: On-Time = |Delay| ≤ 15 minutes
           │
           ▼
    Aggregate by Airline:
           │
           ├─ Total Flights
           ├─ On-Time Flights
           ├─ On-Time Percentage
           ├─ Average Delay
           ├─ Median Delay
           ├─ Min/Max Delay
           │
           ▼
    Calculate: Reliability Score = On-Time % - (Avg Delay / 10)
           │
           ▼
    Rank: Sort by Reliability Score (descending)


┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTENSIBILITY                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    To add new airport:

    1. Create new_airport_api.py
       └─ Implement same interface as SchipholAPIClient
    
    2. Add credentials to .env
       └─ NEW_AIRPORT_API_KEY=xxx
    
    3. Update main.py
       └─ Add command line option for new airport
    
    4. Use existing processor & visualizer
       └─ No changes needed!


================================================================================
"""

if __name__ == "__main__":
    print(ARCHITECTURE)
