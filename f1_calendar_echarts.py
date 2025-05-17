#!/usr/bin/env python3
"""
Streamlit web app to display F1 race calendar data.
"""

import streamlit as st
import pandas as pd
import fastf1
import json
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="F1 Calendar 2025",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "F1 Calendar App - Data provided by FastF1 API"
    }
)

# Apply dark theme with minimal custom CSS
st.markdown("""
<style>
    /* Force dark mode throughout */
    [data-testid="stSidebar"], .stApp, .stApp > header, .stApp > footer {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }
    
    /* F1 colors and theme */
    :root {
        --f1-red: #FF1801;
        --f1-dark: #15151E;
        --f1-gray: #38383F;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: var(--f1-red) !important;
    }
    
    /* Add F1 font */
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap');
    
    html, body, h1, h2, h3, p, div {
        font-family: 'Titillium Web', sans-serif !important;
    }
    
    /* Card styling */
    .race-card {
        background-color: var(--f1-dark);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
        text-transform: uppercase;
    }
    .badge-completed {
        background-color: #4CAF50;
        color: white;
    }
    .badge-ongoing {
        background-color: #2196F3;
        color: white;
    }
    .badge-upcoming {
        background-color: var(--f1-red);
        color: white;
    }
    .badge-sprint {
        background-color: #FF9800;
        color: white;
        margin-left: 8px;
    }
    
    /* Table styling */
    .dataframe {
        width: 100%;
        color: #FAFAFA !important;
        background-color: var(--f1-dark) !important;
    }
    .dataframe th {
        background-color: var(--f1-gray) !important;
        color: white !important;
        font-weight: bold !important;
    }
    .dataframe td {
        background-color: var(--f1-dark) !important;
        color: #FAFAFA !important;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: var(--f1-dark);
        padding: 10px;
        border-radius: 5px;
    }
    [data-testid="stMetricLabel"] {
        color: #CCCCCC !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--f1-red) !important;
        font-weight: bold !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Selectbox styling */
    .stSelectbox [data-baseweb="select"] {
        background-color: var(--f1-dark);
    }
    .stSelectbox [data-baseweb="select"] > div {
        background-color: var(--f1-dark);
        color: white;
    }
    
    /* Apply dark styling to all Streamlit elements */
    .css-1d391kg, .css-10trblm, .css-16idsys p, .stRadio label, .css-81oif8, .css-1aehpvj,
    .stCheckbox label, .stButton > button, .css-1kyxreq {
        color: #FAFAFA !important;
    }
    
    /* Filter dropdown */
    .css-81oif8, .css-1kyxreq, [data-baseweb="select"] {
        background-color: var(--f1-dark) !important;
    }
</style>
""", unsafe_allow_html=True)

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
        
        if race_date < today:
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
        
        event_data = {
            "round": round_num,
            "name": row["EventName"],
            "official_name": row["OfficialEventName"],
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

def display_featured_race(race, title, emoji):
    """Display a featured race in a card using the simplest possible approach"""
    if not race:
        return st.info(f"{emoji} No {title.lower()} race available")
    
    # Create a simple container with a border
    with st.container():
        # Title with emoji and colored by status
        color_map = {
            "Completed": "green",
            "Ongoing": "blue",
            "Upcoming": "red"
        }
        title_color = color_map.get(race['status'], "white")
        
        # Title
        st.markdown(f"<h3 style='color:{title_color};'>{emoji} {title}</h3>", unsafe_allow_html=True)
        
        # Race name and round
        st.subheader(f"Round {race['round']}: {race['name']}")
        
        # Basic info
        st.markdown(f"**Date:** {race['date_formatted']}")
        st.markdown(f"**Circuit:** {race['circuit']}")
        st.markdown(f"**Location:** {race['location']}, {race['country']}")
        
        # Winner info if completed
        if race['status'] == 'Completed' and race.get('winner'):
            st.markdown(f"**Winner:** {race['winner'].get('display', '')}")
            
        # Show countdown for upcoming races
        if race['status'] == 'Upcoming':
            race_date = datetime.strptime(race['date'], '%Y-%m-%d') if race['date'] else None
            today = datetime.now()
            if race_date:
                days_until = (race_date - today).days
                st.info(f"⏱️ Countdown: {days_until} days")
        
        # Status badge
        status_style = {
            "Completed": "success",
            "Ongoing": "primary", 
            "Upcoming": "danger"
        }
        badge_style = status_style.get(race['status'], "secondary")
        
        # Simple badges
        cols = st.columns([1, 1, 3])
        with cols[0]:
            st.markdown(f"<span style='background-color:{title_color}; color:white; padding:5px; border-radius:5px;'>{race['status']}</span>", unsafe_allow_html=True)
        
        # Sprint badge if applicable
        if race['is_sprint']:
            with cols[1]:
                st.markdown("<span style='background-color:orange; color:white; padding:5px; border-radius:5px;'>SPRINT</span>", unsafe_allow_html=True)
        
        # Separator
        st.markdown("---")

def display_season_overview(calendar_data):
    """Display season overview statistics"""
    season_info = calendar_data.get('season', {})
    if not season_info:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Races", season_info['total_races'])
    
    with col2:
        st.metric("Sprint Races", len(calendar_data['sprint_races']))
    
    with col3:
        completed = season_info['status_summary'].get('Completed', 0)
        st.metric("Completed", completed)
    
    with col4:
        upcoming = season_info['status_summary'].get('Upcoming', 0)
        st.metric("Upcoming", upcoming)
    
    # Season span
    st.markdown(f"""
    <div style="background-color: #15151E; padding: 10px; border-radius: 5px; text-align: center; margin: 15px 0;">
        <p>Season Span: <strong>{season_info['season_span']}</strong></p>
    </div>
    """, unsafe_allow_html=True)

def create_calendar_table(races):
    """Create a styled DataFrame for the race calendar"""
    # Filter out testing events and create a clean DataFrame
    filtered_races = [race for race in races if race['round'] > 0]
    
    # Create DataFrame with selected columns
    df = pd.DataFrame(filtered_races)
    
    if df.empty:
        return pd.DataFrame()
    
    # Select and rename columns for display
    display_df = df[['round', 'name', 'circuit', 'location', 'country', 'date_formatted', 'status', 'is_sprint']]
    display_df = display_df.rename(columns={
        'round': 'Round',
        'name': 'Race Name',
        'circuit': 'Circuit',
        'location': 'Location',
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
    # Header
    st.title("Formula 1 Calendar")
    
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
    st.header("Season Overview")
    display_season_overview(calendar_data)
    
    # Featured races section
    st.header("Featured Races")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_featured_race(calendar_data.get('ongoing_race'), "Ongoing Race", "🏎️")
    
    with col2:
        display_featured_race(calendar_data.get('next_race'), "Next Race", "🔜")
    
    with col3:
        display_featured_race(calendar_data.get('last_completed_race'), "Last Completed Race", "✅")
    
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
        # Style the table with colored status indicators
        def highlight_status(val):
            if val == 'Completed':
                return 'background-color: #4CAF5055; color: white'
            elif val == 'Ongoing':
                return 'background-color: #2196F355; color: white'
            elif val == 'Upcoming':
                return 'background-color: #FF180155; color: white'
            return ''
        
        # Apply styling and display table
        styled_table = calendar_table.style.map(highlight_status, subset=['Status'])
        st.dataframe(styled_table, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("Data provided by FastF1 API")

if __name__ == "__main__":
    main() 