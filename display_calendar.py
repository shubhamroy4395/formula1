#!/usr/bin/env python3
"""
Script to retrieve and display the Formula 1 race calendar data from Supabase.
"""

import logging
import pandas as pd
import matplotlib.pyplot as plt
from config import get_supabase_client
from tabulate import tabulate
import streamlit as st
from datetime import datetime, timedelta
import json

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

def load_calendar_data(json_path='calendar_data.json'):
    """Load the calendar data from the JSON file"""
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading calendar data: {e}")
        return None

def display_calendar_summary(calendar_data):
    """Display a summary of the F1 calendar season"""
    if not calendar_data:
        return
    
    season = calendar_data['season']
    
    # Create a clean summary container
    st.container()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.metric("Total Races", season['total_races'])
    
    with col2:
        st.markdown(f"""
        <div class="season-span" style="text-align: center; padding: 10px; border-radius: 5px; background-color: #f0f2f6;">
            <h3>2025 F1 Season</h3>
            <p>Season Span: <strong>{season['season_span']}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        sprint_count = len(calendar_data['sprint_races'])
        st.metric("Sprint Races", sprint_count)
    
    # Display race status counts
    status_counts = season['status_summary']
    st.markdown("### Race Status")
    status_cols = st.columns(len(status_counts))
    
    for i, (status, count) in enumerate(status_counts.items()):
        with status_cols[i]:
            emoji = {"Completed": "✅", "Ongoing": "🏎️", "Upcoming": "🔜"}.get(status, "❓")
            st.metric(f"{emoji} {status}", count)

def display_featured_race(race_data, title, emoji):
    """Display a featured race (next, ongoing, last completed)"""
    if not race_data:
        return
    
    st.markdown(f"### {emoji} {title}")
    
    # Card style for featured race
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 20px;">
        <h3>Round {race_data['round']}: {race_data['name']}</h3>
        <p><strong>Date:</strong> {race_data['date_formatted']}</p>
        <p><strong>Location:</strong> {race_data['location']}, {race_data['country']}</p>
        <p><strong>Circuit:</strong> {race_data['circuit']}</p>
        {"<p><strong>Winner:</strong> " + race_data['winner']['display'] + "</p>" if race_data.get('winner') and race_data['winner'] else ""}
    </div>
    """, unsafe_allow_html=True)

def create_race_card_html(race):
    """Create HTML for a race card"""
    # Determine status color and indicator
    status_colors = {
        "Completed": "#4CAF50",  # Green
        "Ongoing": "#FF9800",    # Orange
        "Upcoming": "#2196F3"    # Blue
    }
    
    status_color = status_colors.get(race['status'], "#9E9E9E")  # Grey default
    status_emoji = {"Completed": "✅", "Ongoing": "🏎️", "Upcoming": "🔜"}.get(race['status'], "❓")
    
    # Special badge for sprint races
    sprint_badge = f'<span style="background-color: #F44336; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-left: 5px;">SPRINT</span>' if race['is_sprint'] else ''
    
    # Winner info if available
    winner_html = ""
    if race['status'] == "Completed" and race.get('winner') and race['winner']:
        winner_html = f"""
        <div style="margin-top: 8px; font-size: 14px;">
            <strong>Winner:</strong> {race['winner']['display']}
        </div>
        """
    
    # Round badge in top-right corner
    round_badge = f"""
    <div style="position: absolute; top: 10px; right: 10px; background-color: #333; color: white; 
                border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; 
                justify-content: center; font-weight: bold;">
        {race['round']}
    </div>
    """
    
    # Create the HTML for the card
    card_html = f"""
    <div style="position: relative; border-radius: 8px; border-left: 5px solid {status_color}; 
                padding: 12px; margin-bottom: 10px; background-color: #f8f9fa; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        {round_badge}
        <div style="font-size: 16px; font-weight: bold; margin-bottom: 6px;">
            {race['name']} {sprint_badge}
        </div>
        <div style="font-size: 14px; margin-bottom: 4px;">
            <strong>Date:</strong> {race['date_formatted']}
        </div>
        <div style="font-size: 14px; margin-bottom: 4px;">
            <strong>Location:</strong> {race['location']}, {race['country']}
        </div>
        <div style="display: flex; align-items: center; margin-top: 8px;">
            <span style="background-color: {status_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                {status_emoji} {race['status']}
            </span>
        </div>
        {winner_html}
    </div>
    """
    return card_html

def display_race_cards(calendar_data, filter_status=None):
    """Display all races as cards with optional filtering by status"""
    if not calendar_data:
        return
    
    races = calendar_data['races']
    
    # Apply filter if requested
    if filter_status:
        races = [race for race in races if race['status'] == filter_status]
    
    if not races:
        st.info("No races match the selected filter.")
        return
    
    # Define number of columns based on screen size
    columns = st.columns(3)  # Can be adjusted based on screen size
    
    # Create cards and distribute them among columns
    for i, race in enumerate(races):
        with columns[i % len(columns)]:
            st.markdown(create_race_card_html(race), unsafe_allow_html=True)

def display_f1_calendar(data_path='calendar_data.json'):
    """Main function to display the F1 calendar"""
    # Load the calendar data
    calendar_data = load_calendar_data(data_path)
    
    if not calendar_data:
        st.error("Unable to load calendar data. Please check if the file exists.")
        return
    
    # Display calendar header
    st.markdown("# 🏎️ F1 2025 Race Calendar")
    st.markdown(f"*Last updated: {calendar_data['last_updated']}*")
    
    # Display calendar summary
    display_calendar_summary(calendar_data)
    
    # Display featured races
    st.markdown("---")
    
    # Create 3 columns for highlighted races
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if calendar_data['ongoing_race']:
            display_featured_race(calendar_data['ongoing_race'], "Ongoing Race", "🏎️")
    
    with col2:
        if calendar_data['next_race']:
            display_featured_race(calendar_data['next_race'], "Next Race", "🔜")
    
    with col3:
        if calendar_data['last_completed_race']:
            display_featured_race(calendar_data['last_completed_race'], "Last Race", "✅")
    
    # Display calendar filter options
    st.markdown("---")
    st.markdown("### Race Calendar")
    
    # Status filter
    filter_options = ["All Races", "Upcoming", "Ongoing", "Completed"]
    selected_filter = st.selectbox("Filter races by status:", filter_options)
    
    # Display race cards based on filter
    if selected_filter == "All Races":
        display_race_cards(calendar_data)
    else:
        display_race_cards(calendar_data, filter_status=selected_filter)

if __name__ == "__main__":
    # For testing as standalone
    st.set_page_config(page_title="F1 2025 Calendar", page_icon="🏎️", layout="wide")
    display_f1_calendar() 