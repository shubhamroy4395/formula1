#!/usr/bin/env python3
"""
Script to create interactive visualizations of Formula 1 race calendar data using Plotly.
"""

import logging
from datetime import datetime
import fastf1
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

def create_interactive_timeline(calendar_data):
    """
    Create an interactive timeline visualization of the F1 calendar
    
    Args:
        calendar_data (list): List of dictionaries with calendar data
        
    Returns:
        None: Saves the visualization as an HTML file
    """
    # Convert to DataFrame
    df = pd.DataFrame(calendar_data)
    
    # Convert dates to datetime
    df['event_date'] = pd.to_datetime(df['event_date'])
    
    # Sort by event date
    df = df.sort_values('event_date')
    
    # Create timeline visualization
    fig = px.scatter(
        df, 
        x='event_date', 
        y='country',
        color='country',
        size=[30] * len(df),  # Fixed size for all points
        hover_name='event_name',
        hover_data={
            'event_date': True,
            'circuit_name': True,
            'round': True,
            'country': False,  # Hide duplicate in hover
            'event_format': True
        },
        title=f'Formula 1 Race Calendar {df["event_date"].dt.year.iloc[0]}',
        labels={
            'event_date': 'Date',
            'country': 'Country',
            'event_name': 'Event',
            'circuit_name': 'Circuit',
            'round': 'Round',
            'event_format': 'Format'
        }
    )
    
    # Add race names as text labels
    fig.add_trace(
        go.Scatter(
            x=df['event_date'],
            y=df['country'],
            mode='text',
            text=df['event_name'],
            textposition='top center',
            textfont=dict(
                size=10,
                color='black'
            ),
            showlegend=False
        )
    )
    
    # Add lines connecting events
    fig.add_trace(
        go.Scatter(
            x=df['event_date'],
            y=df['country'],
            mode='lines',
            line=dict(
                color='rgba(100, 100, 100, 0.2)',
                width=1
            ),
            showlegend=False
        )
    )
    
    # Customize layout
    fig.update_layout(
        height=800,
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='rgba(240, 240, 240, 0.5)',
        xaxis=dict(
            title='Date',
            gridcolor='white',
            linecolor='black',
            ticks='outside',
            tickcolor='black'
        ),
        yaxis=dict(
            title='Country',
            gridcolor='white',
            linecolor='black',
            ticks='outside',
            tickcolor='black'
        ),
        font=dict(
            family="Arial, sans-serif",
            size=14
        ),
        title=dict(
            text=f'Formula 1 Race Calendar {df["event_date"].dt.year.iloc[0]}',
            font=dict(
                family="Arial, sans-serif",
                size=24,
                color="#C00000"
            ),
            x=0.5
        )
    )
    
    # Save as HTML
    fig.write_html('f1_calendar_interactive.html')
    logger.info("Interactive calendar saved as 'f1_calendar_interactive.html'")
    
    # Show figure
    fig.show()

def create_race_distribution_chart(calendar_data):
    """
    Create a chart showing the distribution of races by country
    
    Args:
        calendar_data (list): List of dictionaries with calendar data
        
    Returns:
        None: Saves the visualization as an HTML file
    """
    # Convert to DataFrame
    df = pd.DataFrame(calendar_data)
    
    # Filter out non-race events
    df = df[df['round'] is not None and df['round'] > 0]
    
    # Count races by country
    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Number of Races']
    
    # Create bar chart
    fig = px.bar(
        country_counts,
        x='Country',
        y='Number of Races',
        color='Number of Races',
        color_continuous_scale='Reds',
        title='F1 Races by Country',
        labels={'Country': 'Country', 'Number of Races': 'Number of Races'}
    )
    
    # Customize layout
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        height=600,
        font=dict(
            family="Arial, sans-serif",
            size=14
        ),
        title=dict(
            font=dict(
                family="Arial, sans-serif",
                size=24,
                color="#C00000"
            ),
            x=0.5
        )
    )
    
    # Save as HTML
    fig.write_html('f1_races_by_country.html')
    logger.info("Country distribution chart saved as 'f1_races_by_country.html'")
    
    # Return figure
    return fig

def main():
    """Main function to create interactive visualizations of F1 calendar data"""
    try:
        # Fetch calendar data
        calendar_df = fetch_f1_calendar(2025)
        
        # Prepare data for visualization
        calendar_data = prepare_calendar_data(calendar_df)
        
        # Create interactive timeline
        create_interactive_timeline(calendar_data)
        
        # Create country distribution chart
        create_race_distribution_chart(calendar_data)
        
        logger.info("Plotly visualizations completed successfully")
        
    except Exception as e:
        logger.error(f"Error in plotly visualization process: {e}")

if __name__ == "__main__":
    main() 