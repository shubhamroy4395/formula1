#!/usr/bin/env python3
"""
Script to display Formula 1 race calendar data with Rich formatting.
"""

import logging
from datetime import datetime
import fastf1
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

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
        
        try:
            calendar = fastf1.get_event_schedule(year)
            logger.info(f"Successfully fetched calendar for {year}")
        except Exception as e:
            logger.warning(f"Could not fetch {year} calendar: {e}")
            logger.info("Fetching most recent available calendar instead")
            
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

def display_rich_calendar_table(calendar_data):
    """
    Display the calendar data in a beautiful Rich formatted table
    
    Args:
        calendar_data (list): List of dictionaries with calendar data
    """
    console = Console()
    
    # Create a beautiful header
    title = Text("Formula 1 Race Calendar", style="bold white on red")
    subtitle = Text(f"Season {datetime.now().year}", style="italic")
    
    console.print(Panel(title, subtitle=subtitle, border_style="red", expand=False))
    console.print()
    
    # Create the table
    table = Table(
        show_header=True, 
        header_style="bold white on dark_red", 
        border_style="red",
        box=box.ROUNDED,
        title_justify="center",
        highlight=True,
        min_width=100
    )
    
    # Add columns
    table.add_column("Round", style="dim cyan", justify="center", no_wrap=True)
    table.add_column("Event", style="bold white", justify="left")
    table.add_column("Country", style="green", justify="left")
    table.add_column("Date", style="yellow", justify="center")
    table.add_column("Circuit", style="magenta", justify="left", max_width=40)
    
    # Add rows
    for event in calendar_data:
        round_num = str(event['round']) if event['round'] is not None else "-"
        date = event['event_date'].split('T')[0] if event['event_date'] else "-"
        
        # Add color to special events
        event_style = ""
        if "Pre-Season" in event['event_name']:
            event_style = "dim"
        elif "Monaco" in event['event_name']:
            event_style = "bold bright_white on blue"
        
        table.add_row(
            round_num,
            Text(event['event_name'], style=event_style),
            event['country'],
            date,
            event['circuit_name']
        )
    
    console.print(table)
    
    # Add some statistics
    races_count = sum(1 for event in calendar_data if event['round'] is not None and event['round'] > 0)
    countries_count = len(set(event['country'] for event in calendar_data if event['country']))
    
    stats_table = Table(show_header=False, box=box.SIMPLE, border_style="bright_black")
    stats_table.add_column(justify="right")
    stats_table.add_column(justify="left")
    
    stats_table.add_row("Total Races:", Text(str(races_count), style="bold white"))
    stats_table.add_row("Countries Visited:", Text(str(countries_count), style="bold white"))
    stats_table.add_row("Season Span:", Text(f"{calendar_data[0]['event_date'].split('T')[0]} to {calendar_data[-1]['event_date'].split('T')[0]}", style="bold white"))
    
    console.print()
    console.print(Panel(stats_table, title="Season Statistics", border_style="bright_black"))

def main():
    """Main function to fetch and display F1 calendar data with Rich formatting"""
    try:
        # Fetch calendar data
        calendar_df = fetch_f1_calendar(2025)
        
        # Prepare data for display
        calendar_data = prepare_calendar_data(calendar_df)
        
        # Display rich formatted calendar table
        display_rich_calendar_table(calendar_data)
        
        logger.info("Rich display completed successfully")
        
    except Exception as e:
        logger.error(f"Error in rich display process: {e}")

if __name__ == "__main__":
    main() 