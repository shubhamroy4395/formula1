#!/usr/bin/env python3
"""
Streamlit web app to display Formula 1 race calendar data.
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import fastf1
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="F1 Calendar App",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title with custom style
st.markdown(
    """
    <style>
    .main-title {
        font-size: 3rem;
        color: #FF1801;
        text-align: center;
        font-weight: bold;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-title {
        font-size: 1.5rem;
        color: #15151E;
        text-align: center;
        margin-top: 0px;
        padding-top: 0px;
    }
    </style>
    <div class="main-title">Formula 1 Race Calendar</div>
    """, 
    unsafe_allow_html=True
)

# Function to fetch F1 calendar data
@st.cache_data
def fetch_f1_calendar(year=2025):
    """Fetch F1 calendar data for the specified year"""
    try:
        calendar = fastf1.get_event_schedule(year)
        return calendar
    except Exception as e:
        st.warning(f"Could not fetch {year} calendar: {e}")
        st.info("Fetching most recent available calendar instead")
        current_year = datetime.now().year
        calendar = fastf1.get_event_schedule(current_year)
        return calendar

# Function to prepare calendar data
def prepare_calendar_data(calendar_df):
    """Prepare calendar data for display"""
    calendar_data = []
    
    for _, row in calendar_df.iterrows():
        event_data = {
            "event_name": row["EventName"],
            "round": int(row["RoundNumber"]) if pd.notna(row["RoundNumber"]) else None,
            "country": row["Country"],
            "location": row["Location"],
            "circuit_name": row["OfficialEventName"],
            "event_date": row["EventDate"] if pd.notna(row["EventDate"]) else None,
            "event_format": row["EventFormat"],
            "session1_name": "Practice 1",
            "session1_date": row["Session1Date"] if pd.notna(row["Session1Date"]) else None,
            "session2_name": "Practice 2",
            "session2_date": row["Session2Date"] if pd.notna(row["Session2Date"]) else None,
            "session3_name": "Practice 3",
            "session3_date": row["Session3Date"] if pd.notna(row["Session3Date"]) else None,
            "session4_name": "Qualifying",
            "session4_date": row["Session4Date"] if pd.notna(row["Session4Date"]) else None,
            "session5_name": "Race",
            "session5_date": row["Session5Date"] if pd.notna(row["Session5Date"]) else None,
        }
        
        calendar_data.append(event_data)
    
    return pd.DataFrame(calendar_data)

# Sidebar configuration
st.sidebar.image("https://www.formula1.com/etc/designs/fom-website/images/f1_logo.svg", width=200)
st.sidebar.markdown("## F1 Calendar App")

# Year selection in sidebar
year_options = list(range(2018, 2026))
selected_year = st.sidebar.selectbox("Select Season", year_options, index=len(year_options)-1)

# Add some information in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    """
    This app displays Formula 1 race calendar data fetched using the FastF1 API.
    
    Data is visualized using Streamlit with enhanced table formatting.
    """
)

# Display the subtitle with the selected year
st.markdown(f'<div class="sub-title">Season {selected_year}</div>', unsafe_allow_html=True)

# Load and process data
with st.spinner(f"Loading {selected_year} F1 calendar data..."):
    calendar_df = fetch_f1_calendar(selected_year)
    df = prepare_calendar_data(calendar_df)

# Display metrics at the top
col1, col2, col3 = st.columns(3)
with col1:
    races_count = df[df['round'] > 0].shape[0] if 'round' in df.columns else 0
    st.metric("Total Races", races_count)
with col2:
    countries_count = df['country'].nunique() if 'country' in df.columns else 0
    st.metric("Countries", countries_count)
with col3:
    first_race = df['event_date'].min().strftime('%d %b %Y') if not df.empty and 'event_date' in df.columns and df['event_date'].notna().any() else "N/A"
    last_race = df['event_date'].max().strftime('%d %b %Y') if not df.empty and 'event_date' in df.columns and df['event_date'].notna().any() else "N/A"
    st.metric("Season Span", f"{first_race} - {last_race}")

# Display F1 calendar table
st.subheader("F1 Race Calendar")

# Select and rename columns for display
display_df = df[['round', 'event_name', 'country', 'event_date', 'circuit_name']]
display_df.columns = ['Round', 'Event', 'Country', 'Date', 'Circuit']

# Use Streamlit's data display with sorting and filtering
st.dataframe(
    display_df.style.background_gradient(cmap="Reds", subset=['Round']),
    height=600,
    use_container_width=True,
    hide_index=True
)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #999999; font-size: 0.8rem;'>
    Data provided by FastF1 API. This app is for demonstration purposes only.
    </div>
    """, 
    unsafe_allow_html=True
) 