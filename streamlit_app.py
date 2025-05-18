#!/usr/bin/env python3
"""
Streamlit web app to display F1 race calendar data.
"""

import os
import sys
import streamlit as st
import pandas as pd
import fastf1
import json
import setuptools
from datetime import datetime, timedelta

# Quick health check for deployment environments
if len(sys.argv) > 1 and sys.argv[1] == "healthcheck":
    print("Streamlit app is healthy")
    sys.exit(0)

# Page configuration
st.set_page_config(
    page_title="F1 Paddock by Shubham",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "F1 Paddock by Shubham - Data provided by FastF1 API"
    }
)

# Apply modern glassmorphism theme with enhanced typography
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Spotify-like dark mode theme */
    .stApp {
        background-color: #000000 !important; /* Pure black base like Spotify */
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"], .stApp > header, .stApp > footer {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    
    /* F1 colors and theme */
    :root {
        --f1-red: #FF1801;
        --spotify-black: #121212;
        --spotify-dark-gray: #181818;
        --spotify-light-gray: #282828;
        --spotify-lightest-gray: #B3B3B3;
        --text-primary: #FFFFFF;
        --text-secondary: #B3B3B3;
    }
    
    /* Spotify card style base */
    .spotify-card {
        background-color: #181818;
        border-radius: 8px;
        padding: 16px;
        transition: background-color 0.3s ease;
        border: 1px solid #282828;
    }
    
    .spotify-card:hover {
        background-color: #282828;
    }
    
    /* Typography with modern font stack */
    * {
        font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif !important;
        letter-spacing: -0.02em;
    }
    
    /* Spotify-like headers with F1 red accent */
    h1 {
        color: #FFFFFF !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.04em !important;
    }
    
    h1:after {
        content: "";
        display: block;
        width: 80px;
        height: 4px;
        background-color: var(--f1-red);
        margin-top: 8px;
    }
    
    h2 {
        color: #FFFFFF !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-top: 2rem !important;
        margin-bottom: 1.5rem !important;
        border-bottom: none !important;
        padding-bottom: 0.5rem !important;
        letter-spacing: -0.02em !important;
    }
    
    h3 {
        color: #FFFFFF !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        letter-spacing: -0.01em !important;
    }
    
    /* Improve section separation with modern spacing */
    .main > div {
        padding: 1.5rem 0;
    }
    
    /* Modern card styling with glassmorphism */
    .race-card, div[style*="border: 1px solid #333"] {
        background: rgba(16, 18, 27, 0.4) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        padding: 1.5rem !important;
        margin-bottom: 1.25rem !important;
        transition: all 0.3s ease !important;
    }
    
    /* Card hover effects */
    .race-card:hover, div[style*="border: 1px solid #333"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Improve text hierarchy with modern typography */
    p {
        color: rgba(255, 255, 255, 0.8) !important;
        line-height: 1.6 !important;
        font-weight: 400 !important;
    }
    
    strong, b {
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }
    
    /* Remove padding at top */
    .block-container {
        padding-top: 1rem !important;
    }
    
    /* Spotify-like stats styling */
    .stat-container {
        background-color: #181818;
        border-radius: 8px;
        padding: 1.2rem;
        border: 1px solid #282828;
        transition: background-color 0.3s ease;
        margin-bottom: 16px;
    }
    
    .stat-container:hover {
        background-color: #282828;
    }
    
    .stat-value {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: var(--f1-red) !important;
        line-height: 1 !important;
        letter-spacing: -0.03em !important;
    }
    
    .stat-label {
        color: #B3B3B3 !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        margin-top: 0.5rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em !important;
    }
    
    /* Status indicators with modern design */
    .completed {
        color: #10b981 !important;
    }
    
    .ongoing {
        color: var(--f1-red) !important;
    }
    
    .upcoming {
        color: #3b82f6 !important;
    }
    
    /* Custom scrollbar with modern design */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(16, 18, 27, 0.4);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--f1-red), #FF5E54);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #FF5E54, var(--f1-red));
    }
    
    /* Button and input styling */
    button, [data-testid="stButton"] > button {
        background: rgba(16, 18, 27, 0.4) !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    button:hover, [data-testid="stButton"] > button:hover {
        background: rgba(25, 28, 40, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Select box styling */
    [data-testid="stSelectbox"] {
        background: rgba(16, 18, 27, 0.4) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# F1 team colors for 2025 (with softer tones for better readability)
TEAM_COLORS = {
    "Red Bull Racing": "#5B70FF",  # Softer blue
    "Mercedes": "#7EEADB",  # Softer turquoise
    "Ferrari": "#FF5A5A",  # Softer red
    "McLaren": "#FFAE5D",  # Softer orange
    "Aston Martin": "#46B0A2",  # Softer green
    "Alpine": "#7EC2FF",  # Softer blue
    "Williams": "#7DA5FF",  # Softer blue
    "AlphaTauri": "#6D8AAF",  # Softer navy
    "Alfa Romeo": "#CB5454",  # Softer burgundy
    "Haas F1 Team": "#E0E0E0",  # Softer white
    "Sauber": "#CB5454",  # Softer burgundy
    # Fallback color for any team not listed
    "default": "#8A8A8A"
}

# Status colors with F1 aesthetics - more muted/pastel versions
STATUS_COLORS = {
    "Completed": "#7ED957",  # Softer green 
    "Ongoing": "#FF6B5B",    # Softer red
    "Upcoming": "#6BAAFF",   # Softer blue
    "Unknown": "#A0A0A0"     # Lighter gray
}

# CSS for race status badges with subtle animation
race_status_css = """
<style>
.race-status {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 600;
    color: white !important;  /* Force white text for better contrast */
    margin-right: 8px;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    border: 1px solid rgba(255,255,255,0.1);
    text-shadow: 0 1px 1px rgba(0,0,0,0.5);  /* Add text shadow for better readability */
}
.race-status:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.race-status.completed {
    background-color: """ + STATUS_COLORS["Completed"] + """;
}
.race-status.ongoing {
    background-color: """ + STATUS_COLORS["Ongoing"] + """;
    animation: pulse 2s infinite;
}
.race-status.upcoming {
    background-color: """ + STATUS_COLORS["Upcoming"] + """;
}
.race-status.unknown {
    background-color: """ + STATUS_COLORS["Unknown"] + """;
}
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.8; }
    100% { opacity: 1; }
}
</style>
"""

# Function to create HTML for status indicator
def status_badge(status):
    """Create an HTML badge for race status with appropriate direct styling"""
    # Map status to specific colors
    if status == "Completed":
        color = "#7ED957"  # Green
    elif status == "Ongoing":
        color = "#FF6B5B"  # Red
    elif status == "Upcoming":
        color = "#6BAAFF"  # Blue
    else:
        color = "#A0A0A0"  # Gray
        
    # Ultra-simple HTML with no special characters
    return f'<span style="display:inline-block; background-color:{color}; color:white; font-weight:bold; padding:4px 10px; border-radius:4px;">{status}</span>'

# Helper function to get team color with fallback
def get_team_color(team_name):
    """Return the color for a given team with fallback to default if not found"""
    if not team_name:
        return TEAM_COLORS["default"]
    return TEAM_COLORS.get(team_name, TEAM_COLORS["default"])

# ---------- DATA PROCESSING FUNCTIONS ----------

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_f1_calendar(year=2024):
    """Fetch F1 calendar data for the specified year"""
    try:
        # Try to get calendar data with ergast backend
        calendar = fastf1.get_event_schedule(year, backend='ergast')
        
        # Check if the returned dataframe is empty
        if calendar.empty:
            # Fall back to current year if requested year has no data
            current_year = datetime.now().year
            calendar = fastf1.get_event_schedule(current_year, backend='ergast')
            
        return calendar
    except Exception as e:
        st.error(f"Error fetching F1 calendar: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_circuit_info(circuit_name):
    """
    Fetch circuit information using FastF1 API
    
    Args:
        circuit_name (str): The name of the circuit
        
    Returns:
        dict: Circuit information including corners, marshal lights, marshal sectors, and rotation
    """
    try:
        # Use the fastf1.mvapi.CircuitInfo class to get circuit details
        from fastf1.mvapi import CircuitInfo
        
        # Log the fetch attempt
        print(f"Fetching circuit info for: {circuit_name}")
        
        # Circuit data is accessed through fastf1 events module
        circuits = fastf1.get_event_schedule(2024)['CircuitKey']
        
        # Find the circuit key for the given circuit name
        circuit_key = None
        for idx, key in circuits.items():
            circuit_data = fastf1.get_event(2024, idx)
            if circuit_name.lower() in circuit_data.location.lower() or circuit_name.lower() in circuit_data.name.lower():
                circuit_key = key
                break
                
        if not circuit_key:
            print(f"Circuit key not found for: {circuit_name}")
            return None
            
        # Get circuit info
        info = None
        try:
            info = fastf1.CircuitInfo(circuit_key)
        except:
            try:
                # Alternative fetch using raw MVApi object
                info = fastf1.mvapi.CircuitInfo(
                    corners=pd.DataFrame(),
                    marshal_lights=pd.DataFrame(),
                    marshal_sectors=pd.DataFrame(),
                    rotation=0
                )
            except Exception as e:
                print(f"Error creating circuit info object: {e}")
                return None
                
        if info:
            # Extract useful data
            result = {
                "name": circuit_name,
                "circuit_key": circuit_key,
                "corners": info.corners.to_dict() if hasattr(info, 'corners') and not info.corners.empty else {},
                "marshal_lights": info.marshal_lights.to_dict() if hasattr(info, 'marshal_lights') and not info.marshal_lights.empty else {},
                "marshal_sectors": info.marshal_sectors.to_dict() if hasattr(info, 'marshal_sectors') and not info.marshal_sectors.empty else {},
                "rotation": info.rotation if hasattr(info, 'rotation') else 0
            }
            return result
        
        return None
        
    except Exception as e:
        print(f"Error fetching circuit info: {e}")
        return None

def get_race_status(race_date):
    """Determine the status of a race based on date comparison"""
    if race_date is None or pd.isna(race_date):
        return "Unknown"
    
    try:
        if not isinstance(race_date, datetime):
            race_date = pd.to_datetime(race_date)
        
        today = datetime.now()
        
        # For race weekend consideration
        race_weekend_start = race_date - timedelta(days=2)
        race_weekend_end = race_date + timedelta(hours=6)
        
        # Mark as completed only on the day after the race (day+1)
        race_day_plus_one = race_date + timedelta(days=1)
        
        if race_date.date() < today.date() and race_day_plus_one.date() <= today.date():
            return "Completed"
        elif race_weekend_start <= today <= race_weekend_end:
            return "Ongoing"
        else:
            return "Upcoming"
    except Exception as e:
        st.error(f"Error calculating race status: {e}")
        return "Unknown"

def get_race_winner(year, race_round):
    """Get the winner of a specific race"""
    try:
        # Get the race session for this event
        session = fastf1.get_session(year, race_round, 'Race')
        # Load the session data - minimal data for speed
        session.load(laps=False, telemetry=False, weather=False)
        # Get the results
        results = session.results
        
        if results is not None and not results.empty:
            # Winner is the driver with position 1
            winner = results[results['Position'] == 1]
            if not winner.empty:
                driver_code = winner.iloc[0]['Abbreviation']
                team = winner.iloc[0]['TeamName']
                return {
                    "driver_code": driver_code,
                    "driver_name": winner.iloc[0]['FullName'],
                    "team": team,
                    "position": "1",
                    "display": f"{driver_code} ({team})"
                }
        
        return {}
    except Exception:
        # Silently fail - winner may not be available yet
        return {}

def prepare_calendar_data(calendar_df):
    """
    Prepare calendar data for display
    
    Args:
        calendar_df (pandas.DataFrame): The raw calendar DataFrame
        
    Returns:
        dict: Structured calendar data object
    """
    if calendar_df.empty:
        return {}
        
    calendar_data = []
    winners = {}
    year = datetime.now().year  # Use current year for race data
    
    # Add status based on date
    calendar_df['Status'] = calendar_df['EventDate'].apply(get_race_status)
    
    # Get winners for completed races
    completed_races = calendar_df[calendar_df['Status'] == 'Completed']
    if not completed_races.empty:
        for _, race in completed_races.iterrows():
            try:
                round_num = race['RoundNumber']
                winners[round_num] = get_race_winner(year, round_num)
            except:
                pass  # Silently skip if winner data is unavailable
    
    for _, row in calendar_df.iterrows():
        event_date = pd.to_datetime(row['EventDate']) if pd.notna(row['EventDate']) else None
        round_num = int(row['RoundNumber']) if pd.notna(row['RoundNumber']) else None
        
        # Use the official event name for display if available
        # The FastF1 API uses 'OfficialEventName' for the full race name including sponsors
        event_name = row['EventName'] if pd.notna(row['EventName']) else ""
        official_name = row['OfficialEventName'] if 'OfficialEventName' in row and pd.notna(row['OfficialEventName']) else ""
        
        # If official name is empty or None, fall back to regular event name
        display_name = official_name if official_name else event_name
        
        event_data = {
            "round": round_num,
            "name": display_name,  # Use official name as the primary name for display
            "short_name": event_name,  # Keep the short name as a backup
            "country": row["Country"],
            "location": row["Location"],
            "circuit": row["CircuitName"] if "CircuitName" in row else row["Location"],
            "date": event_date.strftime('%Y-%m-%d') if event_date else None,
            "date_formatted": event_date.strftime('%d %b %Y') if event_date else "TBA",
            "status": row["Status"],
            "format": row["EventFormat"],
            "is_sprint": row["EventFormat"] == 'sprint_qualifying',
            "winner": winners.get(round_num, {})
        }
        
        calendar_data.append(event_data)
    
    # Create the full data object structure
    result = {
        "season": {
            "year": year,
            "total_races": len(calendar_df[calendar_df['RoundNumber'] > 0]),
            "first_race_date": calendar_df['EventDate'].min().strftime('%Y-%m-%d') if not calendar_df.empty else None,
            "last_race_date": calendar_df['EventDate'].max().strftime('%Y-%m-%d') if not calendar_df.empty else None,
            "season_span": f"{calendar_df['EventDate'].min().strftime('%d %b %Y')} - {calendar_df['EventDate'].max().strftime('%d %b %Y')}" if not calendar_df.empty else "TBA",
            "status_summary": calendar_df['Status'].value_counts().to_dict(),
            "format_summary": {
                "conventional": len(calendar_df[calendar_df['EventFormat'] == 'conventional']),
                "sprint_qualifying": len(calendar_df[calendar_df['EventFormat'] == 'sprint_qualifying'])
            }
        },
        "races": calendar_data,
        "sprint_races": [race for race in calendar_data if race["is_sprint"]],
        "next_race": next((race for race in calendar_data if race["status"] == "Upcoming"), None),
        "ongoing_race": next((race for race in calendar_data if race["status"] == "Ongoing"), None),
        "last_completed_race": next((race for race in sorted(calendar_data, key=lambda x: -x["round"]) if race["status"] == "Completed"), None),
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save to JSON for potential use by other components
    with open("calendar_data.json", "w") as f:
        json.dump(result, f, indent=2)
    
    return result

# ---------- UI COMPONENTS ----------

def display_race_card(race, card_type):
    """Display a featured race card with better visual hierarchy."""
    if not race:
        return st.info(f"No {card_type} race available")
    
    # Status mapping
    if card_type == "ongoing":
        icon = "🏎️"
        status = "Ongoing"
    elif card_type == "next":
        icon = "➡️"
        status = "Upcoming"
    else:  # completed
        icon = "✅"
        status = "Completed"
    
    # Format race details
    race_name = race.get('name', 'Unknown Race')
    race_round = race.get('round', '')
    race_date = race.get('date_formatted', '')
    circuit = race.get('circuit', '')
    location = f"{race.get('location', '')}, {race.get('country', '')}"
    
    # Winner information removed per user request
    
    # Apply the badge to the card
    status_html = status_badge(status)
    
        # Create a simple HTML card that will definitely render properly
    st.markdown(
        f"""
        <div style="background-color: #121212; padding: 15px; border-radius: 4px; border-left: 4px solid #FF1801; margin-bottom: 15px;">
            <div>{status_html} <span style="margin-left: 10px;">{icon}</span></div>
            <h3>Round {race_round}: {race_name}</h3>
            <p><strong>Date:</strong> {race_date}</p>
            <p><strong>Circuit:</strong> {circuit}</p>
            <p><strong>Location:</strong> {location}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_season_overview(calendar_data, season_info):
    """Display season overview metrics."""
    # Season overview header
    st.header("Season Overview")
    
    # Layout with 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics - use status_summary or count directly
    completed = season_info['status_summary'].get('Completed', 0)
    upcoming = season_info['status_summary'].get('Upcoming', 0)
    
    # Display metrics with direct styling (no CSS classes)
    with col1:
        st.markdown(
            f"""
            <div style="background-color: #181818; border-radius: 8px; padding: 1.2rem; border: 1px solid #282828; margin-bottom: 16px;">
                <div style="font-size: 0.9rem; color: #B3B3B3; text-transform: uppercase; letter-spacing: 0.05em;">Total Races</div>
                <div style="font-size: 2.5rem; color: #FF1801; font-weight: 700; line-height: 1;">{season_info['total_races']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color: #181818; border-radius: 8px; padding: 1.2rem; border: 1px solid #282828; margin-bottom: 16px;">
                <div style="font-size: 0.9rem; color: #B3B3B3; text-transform: uppercase; letter-spacing: 0.05em;">Sprint Races</div>
                <div style="font-size: 2.5rem; color: #FF1801; font-weight: 700; line-height: 1;">{len(calendar_data['sprint_races'])}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div style="background-color: #181818; border-radius: 8px; padding: 1.2rem; border: 1px solid #282828; margin-bottom: 16px;">
                <div style="font-size: 0.9rem; color: #B3B3B3; text-transform: uppercase; letter-spacing: 0.05em;">Completed</div>
                <div style="font-size: 2.5rem; color: #FF1801; font-weight: 700; line-height: 1;">{completed}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col4:
        st.markdown(
            f"""
            <div style="background-color: #181818; border-radius: 8px; padding: 1.2rem; border: 1px solid #282828; margin-bottom: 16px;">
                <div style="font-size: 0.9rem; color: #B3B3B3; text-transform: uppercase; letter-spacing: 0.05em;">Upcoming</div>
                <div style="font-size: 2.5rem; color: #FF1801; font-weight: 700; line-height: 1;">{upcoming}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Display season span with direct styling
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px 0; background-color: #181818; border-radius: 8px; margin: 10px 0; border: 1px solid #282828;">
            <p style="margin: 8px 0; color: #B3B3B3;">Season Span: <strong style="color: white;">{season_info['season_span']}</strong></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

def create_calendar_table(races):
    """Create a styled DataFrame for the race calendar"""
    # Filter out testing events and create a clean DataFrame
    filtered_races = [race for race in races if race['round'] > 0]
    
    if not filtered_races:
        return pd.DataFrame()
    
    # Create DataFrame with selected columns
    df = pd.DataFrame(filtered_races)
    
    if df.empty:
        return pd.DataFrame()
    
    # Make sure we use the name field which has the official name if available,
    # or falls back to short_name if official name is not available
    # We'll combine the round number with the race name for better display
    df['formatted_name'] = df.apply(lambda x: f"{x['name'] if x['name'] else x['short_name']}", axis=1)
    
    # Select and rename columns for display
    display_df = df[['round', 'formatted_name', 'circuit', 'country', 'date_formatted', 'status', 'is_sprint']]
    display_df = display_df.rename(columns={
        'round': 'Round',
        'formatted_name': 'Race Name',
        'circuit': 'Circuit',
        'country': 'Country',
        'date_formatted': 'Date',
        'status': 'Status',
        'is_sprint': 'Sprint'
    })
    
    # Convert boolean to Yes/No
    display_df['Sprint'] = display_df['Sprint'].map({True: 'Yes', False: 'No'})
    
    # Add winner information for completed races
    winner_info = []
    for _, race in df.iterrows():
        if race['status'] == 'Completed' and race.get('winner'):
            winner_info.append(race['winner'].get('display', '-'))
        else:
            winner_info.append('-')
    
    display_df['Winner'] = winner_info
    
    # Sort by round number
    display_df = display_df.sort_values('Round')
    
    return display_df

# ---------- MAIN APP ----------

def main():
    # Header with navigation
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("F1 Paddock by Shubham")
    with col2:
        # Create navigation buttons with Spotify-like styling
        st.markdown("""
        <div style="text-align: right; margin-top: 20px;">
            <a href="/" style="display: inline-block; background-color: #121212; color: white; text-decoration: none; padding: 8px 16px; margin-right: 8px; border-radius: 50px;">Home</a>
            <a href="/1_Circuits" style="display: inline-block; background-color: #FF1801; color: white; text-decoration: none; padding: 8px 16px; border-radius: 50px; font-weight: bold;">Circuits</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Apply CSS for status badges and animations
    st.markdown(race_status_css, unsafe_allow_html=True)
    
    # Additional CSS for cards and hover effects
    st.markdown("""
    <style>
    /* Gradient background for race cards */
    div[data-testid="stVerticalBlock"] > div:has(div.race-status) {
        background: linear-gradient(135deg, #111 0%, #252525 100%);
        transition: all 0.3s ease;
    }
    
    /* Card hover effect */
    div[style*="border: 1px solid #333"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    /* Animated border for race cards */
    @keyframes border-pulse {
        0% { border-color: #333; }
        50% { border-color: #555; }
        100% { border-color: #333; }
    }
    
    div[style*="border: 1px solid #333"] {
        animation: border-pulse 4s infinite;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1E1E1E;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #FF1801;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #FF3722;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Fetch and process calendar data - use current year
    with st.spinner("Loading F1 calendar data..."):
        current_year = datetime.now().year
        calendar_df = fetch_f1_calendar(year=current_year)
    
    if calendar_df.empty:
        st.error("No calendar data available. Please try again later.")
        return
    
    # Process calendar data
    calendar_data = prepare_calendar_data(calendar_df)
    
    # Season overview
    display_season_overview(calendar_data, calendar_data['season'])
    
    # Featured races section
    st.header("Featured Races")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_race_card(calendar_data.get('ongoing_race'), "ongoing")
    
    with col2:
        display_race_card(calendar_data.get('next_race'), "next")
    
    with col3:
        display_race_card(calendar_data.get('last_completed_race'), "completed")
    
    # Full race calendar as a table
    st.header("Full Race Calendar")
    
    # Create table
    calendar_table = create_calendar_table(calendar_data['races'])
    
    # Add filter
    filter_options = ["All Races", "Upcoming", "Ongoing", "Completed"]
    filter_choice = st.selectbox("Filter races by status:", filter_options)
    
    # Apply filter
    if filter_choice != "All Races":
        calendar_table = calendar_table[calendar_table['Status'] == filter_choice]
    
    if calendar_table.empty:
        st.warning(f"No races with status '{filter_choice}' found.")
    else:
        # Display the table with enhanced HTML styling
        html_table = "<table class='dataframe'><thead><tr>"
        
        # Add headers
        for col in calendar_table.columns:
            html_table += f"<th>{col}</th>"
        
        html_table += "</tr></thead><tbody>"
        
        # Add rows with enhanced styling
        for _, row in calendar_table.iterrows():
            html_table += "<tr>"
            for col in calendar_table.columns:
                if col == 'Status':
                    # Use our status badge function
                    status = row[col]
                    html_table += f"<td>{status_badge(status)}</td>"
                elif col == 'Winner' and row[col] != '-':
                    # Get winner details from the original data
                    race_found = next((r for r in calendar_data['races'] if r['round'] == row['Round']), None)
                    if race_found and race_found.get('winner'):
                        team = race_found['winner'].get('team', '')
                        team_color = get_team_color(team)
                        # Convert hex to rgba with opacity
                        team_color_rgb = team_color
                        if team_color.startswith('#'):
                            r = int(team_color[1:3], 16)
                            g = int(team_color[3:5], 16)
                            b = int(team_color[5:7], 16)
                            team_color_rgb = f"rgba({r}, {g}, {b}, 0.9)"
                        # Premium glassmorphism styling for winner names
                        html_table += f'''<td>
                            <div style="
                                display: inline-block;
                                background: rgba(16, 18, 27, 0.4);
                                backdrop-filter: blur(6px);
                                -webkit-backdrop-filter: blur(6px);
                                border: 1px solid rgba(255, 255, 255, 0.05);
                                border-radius: 8px;
                                padding: 8px 12px;
                                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                                position: relative;
                                overflow: hidden;
                            ">
                                <div style="
                                    position: absolute;
                                    top: 0;
                                    left: 0;
                                    width: 4px;
                                    height: 100%;
                                    background: {team_color};
                                "></div>
                                <span style="
                                    color: {team_color_rgb}; 
                                    font-weight: 600; 
                                    margin-left: 5px;
                                    text-shadow: 0 0 1px rgba(0,0,0,0.8);
                                    letter-spacing: -0.01em;
                                ">{row[col]}</span>
                            </div>
                        </td>'''
                    else:
                        html_table += f"<td>{row[col]}</td>"
                else:
                    html_table += f"<td>{row[col]}</td>"
            html_table += "</tr>"
        
        html_table += "</tbody></table>"
        
        # Apply additional table styling
        st.markdown("""
        <style>
        /* Spotify-like table styling */
        .dataframe {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 14px;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 24px;
            background-color: #181818;
            border: 1px solid #282828;
        }
        
        .dataframe thead tr {
            background-color: #121212;
        }
        
        .dataframe th {
            text-align: left;
            padding: 16px 20px;
            font-weight: 600;
            color: white;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-size: 0.85rem;
            border-bottom: 2px solid #FF1801;
            position: relative;
        }
        
        /* Add subtle diagonal lines in header cells */
        .dataframe th::after {
            content: '';
            position: absolute;
            right: 0;
            top: 0;
            height: 100%;
            width: 1px;
            background: linear-gradient(to bottom, rgba(255,255,255,0.05), rgba(255,255,255,0));
        }
        
        .dataframe td {
            padding: 14px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
            font-weight: 400;
            letter-spacing: -0.01em;
        }
        
        .dataframe tr {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .dataframe tbody tr:hover {
            background-color: #282828 !important;
        }
        
        .dataframe tr:hover td {
            border-bottom: 1px solid var(--f1-red);
        }
        
        .dataframe tr:nth-child(even) {
            background-color: #181818;
        }
        
        .dataframe tr:nth-child(odd) {
            background-color: #121212;
        }
        
        /* Add subtle glow effect on hover */
        .dataframe tbody tr:hover::after {
            content: '';
            position: absolute;
            left: 0;
            right: 0;
            top: 0;
            bottom: 0;
            box-shadow: 0 0 20px rgba(255, 24, 1, 0.1);
            pointer-events: none;
            z-index: -1;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Display the table
        st.markdown(html_table, unsafe_allow_html=True)
    
    # Footer with animation
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px; opacity: 0.8; animation: fade 3s infinite alternate;">
        <p>Data provided by FastF1 API</p>
        <p style="font-size: 0.8em;">Last updated: """ + calendar_data['last_updated'] + """</p>
    </div>
    
    <style>
    @keyframes fade {
        0% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

# This ensures the main function runs only if this file is executed directly
if __name__ == "__main__":
    main() 