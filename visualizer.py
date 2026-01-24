"""
Data Visualization Module
Creates charts and visualizations for airline reliability data
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import config


class ReliabilityVisualizer:
    """Create visualizations for airline reliability data"""
    
    def __init__(self):
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
    
    def plot_airline_rankings(self, airline_stats: pd.DataFrame, output_file: str = None):
        """
        Create bar chart of airline reliability rankings
        
        Args:
            airline_stats: DataFrame with airline statistics
            output_file: Optional output filename
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Take top 20 airlines
        top_airlines = airline_stats.head(20)
        
        # Create bar chart
        bars = ax.barh(range(len(top_airlines)), top_airlines['reliability_score'])
        
        # Color bars based on score
        colors = ['green' if score >= 80 else 'orange' if score >= 60 else 'red' 
                 for score in top_airlines['reliability_score']]
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        # Set labels
        ax.set_yticks(range(len(top_airlines)))
        ax.set_yticklabels(top_airlines['airline_code'])
        ax.set_xlabel('Reliability Score')
        ax.set_ylabel('Airline')
        ax.set_title('Top 20 Airlines by Reliability Score', fontsize=16, fontweight='bold')
        
        # Add value labels on bars
        for i, (score, flights) in enumerate(zip(top_airlines['reliability_score'], 
                                                  top_airlines['total_flights'])):
            ax.text(score + 1, i, f'{score:.1f} ({int(flights)} flights)', 
                   va='center', fontsize=9)
        
        plt.tight_layout()
        
        if output_file:
            filepath = f"{config.REPORTS_DIR}/{output_file}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved chart to {filepath}")
        
        plt.show()
    
    def plot_on_time_performance(self, airline_stats: pd.DataFrame, output_file: str = None):
        """
        Create scatter plot of on-time performance vs average delay
        
        Args:
            airline_stats: DataFrame with airline statistics
            output_file: Optional output filename
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create scatter plot
        scatter = ax.scatter(
            airline_stats['avg_delay_minutes'],
            airline_stats['on_time_percentage'],
            s=airline_stats['total_flights'] * 2,  # Size by number of flights
            alpha=0.6,
            c=airline_stats['reliability_score'],
            cmap='RdYlGn'
        )
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Reliability Score')
        
        # Add labels for airlines
        for idx, row in airline_stats.iterrows():
            if row['total_flights'] > 50:  # Only label airlines with many flights
                ax.annotate(
                    row['airline_code'],
                    (row['avg_delay_minutes'], row['on_time_percentage']),
                    fontsize=8,
                    alpha=0.7
                )
        
        ax.set_xlabel('Average Delay (minutes)')
        ax.set_ylabel('On-Time Performance (%)')
        ax.set_title('Airline On-Time Performance vs Average Delay', 
                    fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            filepath = f"{config.REPORTS_DIR}/{output_file}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved chart to {filepath}")
        
        plt.show()
    
    def plot_delay_distribution(self, df: pd.DataFrame, airline_code: str = None, 
                               output_file: str = None):
        """
        Create histogram of delay distribution
        
        Args:
            df: DataFrame with flight data
            airline_code: Optional airline code to filter by
            output_file: Optional output filename
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Filter data
        data = df[df['delay_minutes'].notna()].copy()
        if airline_code:
            data = data[data['airline_code'] == airline_code]
            title = f'Delay Distribution for {airline_code}'
        else:
            title = 'Overall Delay Distribution'
        
        # Create histogram
        ax.hist(data['delay_minutes'], bins=50, edgecolor='black', alpha=0.7)
        
        # Add vertical line at 0 (on-time)
        ax.axvline(x=0, color='green', linestyle='--', linewidth=2, label='On-time')
        
        # Add vertical lines for threshold
        threshold = config.RELIABILITY_SETTINGS['on_time_threshold_minutes']
        ax.axvline(x=threshold, color='orange', linestyle='--', linewidth=1, 
                  label=f'±{threshold} min threshold')
        ax.axvline(x=-threshold, color='orange', linestyle='--', linewidth=1)
        
        ax.set_xlabel('Delay (minutes, negative = early)')
        ax.set_ylabel('Number of Flights')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            filepath = f"{config.REPORTS_DIR}/{output_file}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved chart to {filepath}")
        
        plt.show()
    
    def plot_daily_performance(self, df: pd.DataFrame, output_file: str = None):
        """
        Create line chart of daily performance trends
        
        Args:
            df: DataFrame with flight data
            output_file: Optional output filename
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Group by date
        df_with_dates = df[df['schedule_date'].notna()].copy()
        daily_stats = df_with_dates.groupby('schedule_date').agg({
            'on_time': lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0,
            'delay_minutes': 'mean',
            'flight_id': 'count'
        }).reset_index()
        
        daily_stats.columns = ['date', 'on_time_pct', 'avg_delay', 'total_flights']
        
        # Create dual-axis plot
        ax2 = ax.twinx()
        
        # Plot on-time percentage
        line1 = ax.plot(daily_stats['date'], daily_stats['on_time_pct'], 
                       'b-o', label='On-Time %', linewidth=2)
        
        # Plot average delay
        line2 = ax2.plot(daily_stats['date'], daily_stats['avg_delay'], 
                        'r-s', label='Avg Delay (min)', linewidth=2)
        
        # Set labels
        ax.set_xlabel('Date')
        ax.set_ylabel('On-Time Performance (%)', color='b')
        ax2.set_ylabel('Average Delay (minutes)', color='r')
        ax.set_title('Daily Performance Trends', fontsize=16, fontweight='bold')
        
        # Rotate x-axis labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Add legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if output_file:
            filepath = f"{config.REPORTS_DIR}/{output_file}"
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved chart to {filepath}")
        
        plt.show()


if __name__ == "__main__":
    # Example usage
    from data_processor import FlightDataProcessor
    
    processor = FlightDataProcessor()
    visualizer = ReliabilityVisualizer()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    print("=== Reliability Visualizer Test ===\n")
    
    # Load and process data
    try:
        df = pd.read_csv(f"{config.PROCESSED_DATA_DIR}/processed_departures_{today}.csv")
        print(f"Loaded {len(df)} processed flights")
        
        # Calculate airline stats
        airline_stats = processor.calculate_airline_reliability(df)
        
        # Create visualizations
        print("\nGenerating visualizations...")
        
        visualizer.plot_airline_rankings(
            airline_stats, 
            f"airline_rankings_{today}.png"
        )
        
        visualizer.plot_on_time_performance(
            airline_stats,
            f"on_time_performance_{today}.png"
        )
        
        visualizer.plot_delay_distribution(
            df,
            output_file=f"delay_distribution_{today}.png"
        )
        
        if len(df['schedule_date'].unique()) > 1:
            visualizer.plot_daily_performance(
                df,
                output_file=f"daily_performance_{today}.png"
            )
        
    except FileNotFoundError:
        print("No processed data found. Run data_processor.py first.")
