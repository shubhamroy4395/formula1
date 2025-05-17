#!/usr/bin/env python3
"""
Script to retrieve and display the Formula 1 race calendar data from Supabase.
"""

import logging
import pandas as pd
import matplotlib.pyplot as plt
from config import get_supabase_client
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_calendar_from_supabase():
    """
    Retrieve the F1 calendar data from Supabase
    
    Returns:
        list: List of dictionaries with calendar data
    """
    try:
        logger.info("Connecting to Supabase")
        supabase = get_supabase_client()
        
        # Query the data
        logger.info("Retrieving F1 calendar data")
        response = supabase.table("f1_calendar").select("*").order("round").execute()
        
        # Extract the data from the response
        calendar_data = response.data
        
        logger.info(f"Retrieved {len(calendar_data)} races from Supabase")
        return calendar_data
    
    except Exception as e:
        logger.error(f"Error retrieving calendar data from Supabase: {e}")
        raise

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
    """Main function to retrieve and display F1 calendar data"""
    try:
        # Get calendar data from Supabase
        calendar_data = get_calendar_from_supabase()
        
        # Display calendar as a table
        display_calendar_table(calendar_data)
        
        # Create calendar visualization
        display_calendar_plot(calendar_data)
        
        logger.info("Process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")

if __name__ == "__main__":
    main() 