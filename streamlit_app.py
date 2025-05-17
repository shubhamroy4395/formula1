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
    page_title="F1 Paddock by Shubham",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "F1 Paddock by Shubham - Data provided by FastF1 API"
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
        --f1-light-gray: #CCCCCC;
    }
    
    /* Header styling with hierarchy */
    h1 {
        color: var(--f1-red) !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.5px !important;
    }
    
    h2 {
        color: var(--f1-red) !important;
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 1px solid rgba(255,24,1,0.3) !important;
        padding-bottom: 0.5rem !important;
    }
    
    h3 {
        color: #FFFFFF !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    /* Improve section separation */
    .main > div {
        padding: 1rem 0;
    }
    
    /* Card styling */
    .race-card {
        background-color: var(--f1-dark);
        border-left: 4px solid var(--f1-red);
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
    
    /* Improve text hierarchy */
    p {
        color: var(--f1-light-gray) !important;
    }
    
    strong, b {
        color: #FFFFFF !important;
    }
    
    /* Remove padding at top */
    .block-container {
        padding-top: 1rem !important;
    }
    
    /* Stats styling */
    .stat-container {
        background-color: rgba(255,255,255,0.05);
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }
    
    .stat-value {
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: var(--f1-red) !important;
        line-height: 1 !important;
    }
    
    .stat-label {
        color: var(--f1-light-gray) !important;
        font-size: 0.9rem !important;
    }
    
    /* Status indicators */
    .completed {
        color: #10b981 !important;
    }
    
    .ongoing {
        color: var(--f1-red) !important;
    }
    
    .upcoming {
        color: #3b82f6 !important;
    }
    
    /* Keep existing imports and other CSS */
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Titillium Web', sans-serif !important;
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
        
    # Set icon and status based on card type
    if card_type == "ongoing":
        icon = "🏎️"
        status_class = "ongoing"
        status_text = "Ongoing Race"
    elif card_type == "next":
        icon = "➡️"
        status_class = "upcoming"
        status_text = "Next Race"
    else:  # completed
        icon = "✅"
        status_class = "completed"
        status_text = "Last Completed Race"
        
    # Format race details
    race_name = race.get('name', 'Unknown Race')
    race_round = race.get('round', '')
    race_date = race.get('date_formatted', '')
    circuit = race.get('circuit', '')
    location = f"{race.get('location', '')}, {race.get('country', '')}"
    
    # Add winner for completed races
    winner_html = ""
    if card_type == "completed" and race.get('winner'):
        winner = race['winner'].get('display', '')
        if winner:
            winner_html = f"<p><strong>Winner:</strong> {winner}</p>"
    
    # Create card with better hierarchy
    st.markdown(f"""
    <div class="race-card">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.3rem; margin-right: 10px;">{icon}</span>
            <span class="{status_class}" style="font-weight: 600; font-size: 1.1rem;">{status_text}</span>
        </div>
        <h3 style="margin-top: 0;">Round {race_round}: {race_name}</h3>
        <p><strong>Date:</strong> {race_date}</p>
        <p><strong>Circuit:</strong> {circuit}</p>
        <p><strong>Location:</strong> {location}</p>
        {winner_html}
    </div>
    """, unsafe_allow_html=True)

def display_season_overview(calendar_data, season_info):
    """Display season overview metrics."""
    # Season overview header
    st.header("Season Overview")
    
    # Layout with 4 columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics - use status_summary or count directly
    completed = season_info['status_summary'].get('Completed', 0)
    upcoming = season_info['status_summary'].get('Upcoming', 0)
    
    # Display metrics with custom HTML for better styling
    with col1:
        st.markdown(
            f"""
            <div class="stat-container">
                <div class="stat-label">Total Races</div>
                <div class="stat-value">{season_info['total_races']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="stat-container">
                <div class="stat-label">Sprint Races</div>
                <div class="stat-value">{len(calendar_data['sprint_races'])}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col3:
        st.markdown(
            f"""
            <div class="stat-container">
                <div class="stat-label">Completed</div>
                <div class="stat-value">{completed}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with col4:
        st.markdown(
            f"""
            <div class="stat-container">
                <div class="stat-label">Upcoming</div>
                <div class="stat-value">{upcoming}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Display season span
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px 0;">
            <p>Season Span: <strong>{season_info['season_span']}</strong></p>
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
    # Header
    st.title("F1 Paddock by Shubham")
    
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
        # Apply CSS to force dark mode for the table
        st.markdown("""
        <style>
        /* Force dark mode for tables */
        .dataframe {
            background-color: #0E1117 !important;
            color: #E0E0E0 !important;
            border-collapse: collapse;
            width: 100%;
        }
        .dataframe th {
            background-color: #1E1E1E !important;
            color: #E0E0E0 !important;
            font-weight: bold !important;
            border: 1px solid #333 !important;
            padding: 8px;
            text-align: left;
        }
        .dataframe td {
            background-color: #0E1117 !important;
            color: #E0E0E0 !important;
            border: 1px solid #333 !important;
            padding: 8px;
        }
        .dataframe tr:nth-child(even) {
            background-color: #161B22 !important;
        }
        
        /* Enhanced status styling with indicator dots */
        .completed {
            background-color: rgba(76, 175, 80, 0.2) !important;
            border-left: 4px solid #4CAF50 !important;
            font-weight: bold;
        }
        .ongoing {
            background-color: rgba(33, 150, 243, 0.2) !important;
            border-left: 4px solid #2196F3 !important;
            font-weight: bold;
        }
        .upcoming {
            background-color: rgba(255, 24, 1, 0.2) !important;
            border-left: 4px solid #FF1801 !important;
            font-weight: bold;
        }
        
        /* Status indicator dots */
        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .dot-completed {
            background-color: #4CAF50;
        }
        .dot-ongoing {
            background-color: #2196F3;
        }
        .dot-upcoming {
            background-color: #FF1801;
        }
        
        /* Hide index column */
        .index_col {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Format the data with enhanced status display
        html_table = "<table class='dataframe'><thead><tr>"
        
        # Add headers without index column
        for col in calendar_table.columns:
            html_table += f"<th>{col}</th>"
        
        html_table += "</tr></thead><tbody>"
        
        # Add rows without index column
        for _, row in calendar_table.iterrows():
            html_table += "<tr>"
            for i, col in enumerate(calendar_table.columns):
                # Special styling for Status column with indicator dots
                if col == 'Status':
                    status_class = row[col].lower()
                    dot_class = f"dot-{status_class}"
                    html_table += f"<td class='{status_class}'><span class='status-dot {dot_class}'></span>{row[col]}</td>"
                else:
                    html_table += f"<td>{row[col]}</td>"
            html_table += "</tr>"
        
        html_table += "</tbody></table>"
        
        # Display the table
        st.markdown(html_table, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("Data provided by FastF1 API")

# This ensures the main function runs only if this file is executed directly
if __name__ == "__main__":
    main() 