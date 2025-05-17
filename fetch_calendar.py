#!/usr/bin/env python3
"""
Script to fetch Formula 1 race calendar data using FastF1 API
and store it in Supabase database.
"""

import fastf1
import pandas as pd
from datetime import datetime
import logging
from config import get_supabase_client
import time

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
    Prepare calendar data for storage in Supabase
    
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

def store_calendar_in_supabase(calendar_data):
    """
    Store the calendar data in Supabase
    
    Args:
        calendar_data (list): List of dictionaries with calendar data
        
    Returns:
        dict: Response from Supabase
    """
    try:
        logger.info("Connecting to Supabase")
        supabase = get_supabase_client()
        
        # Clear existing data (optional, you might want to update instead)
        logger.info("Clearing existing calendar data")
        supabase.table("f1_calendar").delete().execute()
        
        # Insert new data
        logger.info(f"Inserting {len(calendar_data)} races into Supabase")
        response = supabase.table("f1_calendar").insert(calendar_data).execute()
        
        logger.info("Successfully stored calendar data in Supabase")
        return response
    
    except Exception as e:
        logger.error(f"Error storing calendar data in Supabase: {e}")
        raise

def main():
    """Main function to fetch and store F1 calendar data"""
    try:
        # Fetch calendar data
        calendar_df = fetch_f1_calendar(2025)
        
        # Prepare data for Supabase
        calendar_data = prepare_calendar_data(calendar_df)
        
        # Store data in Supabase
        store_calendar_in_supabase(calendar_data)
        
        logger.info("Process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")

if __name__ == "__main__":
    main() 