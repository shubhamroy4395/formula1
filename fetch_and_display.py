#!/usr/bin/env python3
"""
Script to fetch and display Formula 1 race calendar data using FastF1 API.
This version works without Supabase to demonstrate core functionality.
"""

import fastf1
import pandas as pd
from datetime import datetime
import logging
import matplotlib.pyplot as plt
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_f1_calendar(year=2025):
    """
    Fetch the Formula 1 race calendar for the specified year
    
    Args:
        year (int): The year to fetch the calendar for
        
    Returns:
        pandas.DataFrame: The race calendar data
    """
    try:
        logger.info(f"Fetching F1 calendar for {year}")
        
        # Note: As of now, FastF1 might not have 2025 data available yet
        # This will fetch the most recent available calendar
        # We'll use a try-except block to handle potential errors
        
        try:
            calendar = fastf1.get_event_schedule(year)
            logger.info(f"Successfully fetched calendar for {year}")
        except Exception as e:
            logger.warning(f"Could not fetch {year} calendar: {e}")
            logger.info("Fetching most recent available calendar instead")
            
            # Try to get the most recent available calendar (e.g., 2024)
            current_year = datetime.now().year
            calendar = fastf1.get_event_schedule(current_year)
            logger.info(f"Using {current_year} calendar as fallback")
        
        return calendar
    
    except Exception as e:
        logger.error(f"Error fetching F1 calendar: {e}")
        raise

def prepare_calendar_data(calendar_df):
    """
    Prepare calendar data for display
    
    Args:
        calendar_df (pandas.DataFrame): The raw calendar DataFrame
        
    Returns:
        list: A list of dictionaries with formatted calendar data
    """
    calendar_data = []
    
    for _, row in calendar_df.iterrows():
        event_data = {
            "event_name": row["EventName"],
            "round": int(row["RoundNumber"]) if pd.notna(row["RoundNumber"]) else None,
            "country": row["Country"],
            "location": row["Location"],
            "circuit_name": row["OfficialEventName"],
            "event_date": row["EventDate"].isoformat() if pd.notna(row["EventDate"]) else None,
            "event_format": row["EventFormat"],
            "session1_name": "Practice 1",
            "session1_date": row["Session1Date"].isoformat() if pd.notna(row["Session1Date"]) else None,
            "session2_name": "Practice 2",
            "session2_date": row["Session2Date"].isoformat() if pd.notna(row["Session2Date"]) else None,
            "session3_name": "Practice 3",
            "session3_date": row["Session3Date"].isoformat() if pd.notna(row["Session3Date"]) else None,
            "session4_name": "Qualifying",
            "session4_date": row["Session4Date"].isoformat() if pd.notna(row["Session4Date"]) else None,
            "session5_name": "Race",
            "session5_date": row["Session5Date"].isoformat() if pd.notna(row["Session5Date"]) else None,
        }
        
        calendar_data.append(event_data)
    
    return calendar_data

def display_calendar_table(calendar_data):
    """
    Display the calendar data in a formatted table
    
    Args:
        calendar_data (list): List of dictionaries with calendar data
    """
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(calendar_data)
    
    # Select and rename columns for display
    display_df = df[['round', 'event_name', 'country', 'event_date', 'circuit_name']]
    display_df.columns = ['Round', 'Event', 'Country', 'Date', 'Circuit']
    
    # Display as table
    print("\nFormula 1 Race Calendar\n")
    print(tabulate(display_df, headers='keys', tablefmt='pretty', showindex=False))

def display_calendar_plot(calendar_data):
    """
    Create a visualization of the race calendar
    
    Args:
        calendar_data (list): List of dictionaries with calendar data
    """
    # Convert to DataFrame
    df = pd.DataFrame(calendar_data)
    
    # Convert event_date to datetime
    df['event_date'] = pd.to_datetime(df['event_date'])
    
    # Sort by event date
    df = df.sort_values('event_date')
    
    # Create figure and axis
    plt.figure(figsize=(12, 8))
    
    # Plot events as points
    plt.scatter(df['event_date'], df['country'], s=100, color='red')
    
    # Connect events with lines
    plt.plot(df['event_date'], df['country'], 'b-', alpha=0.3)
    
    # Add event names as labels
    for i, row in df.iterrows():
        plt.text(row['event_date'], row['country'], f" {row['event_name']}", 
                 verticalalignment='center')
    
    # Set title and labels
    plt.title('F1 Race Calendar', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Country', fontsize=12)
    
    # Adjust layout
    plt.tight_layout()
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Save figure
    plt.savefig('f1_calendar.png')
    logger.info("Calendar visualization saved as 'f1_calendar.png'")
    
    # Show plot
    plt.show()

def main():
    """Main function to fetch and display F1 calendar data"""
    try:
        # Fetch calendar data
        calendar_df = fetch_f1_calendar(2025)
        
        # Prepare data for display
        calendar_data = prepare_calendar_data(calendar_df)
        
        # Display calendar as a table
        display_calendar_table(calendar_data)
        
        # Create calendar visualization
        display_calendar_plot(calendar_data)
        
        logger.info("Process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")

if __name__ == "__main__":
    main() 