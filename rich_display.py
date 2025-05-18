#!/usr/bin/env python3
"""
Script to display Formula 1 race calendar data with Rich formatting.
"""

import logging
from datetime import datetime, timedelta
import json
import fastf1
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.layout import Layout
from rich.console import Group
from rich.columns import Columns

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

def get_race_status(race_date, simulated_date=None):
    """Determine the status of a race based on date comparison"""
    if race_date is None or pd.isna(race_date):
        return "Unknown"
    
    try:
        if not isinstance(race_date, datetime):
            race_date = pd.to_datetime(race_date)
        
        # Use simulated date or actual date
        today = simulated_date if simulated_date else datetime.now()
        
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
        logger.error(f"Error calculating race status: {e}")
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
    except Exception as e:
        logger.warning(f"Error fetching race winner: {e}")
        return {}

def prepare_calendar_data(calendar_df, simulated_date=None):
    """
    Prepare calendar data for display
    
    Args:
        calendar_df (pandas.DataFrame): The raw calendar DataFrame
        simulated_date (datetime, optional): Simulated date for testing
        
    Returns:
        list: A list of dictionaries with formatted calendar data
    """
    calendar_data = []
    winners = {}
    
    # Add status based on date
    calendar_df['Status'] = calendar_df['EventDate'].apply(
        lambda date: get_race_status(date, simulated_date)
    )
    
    # Get winners for completed races
    completed_races = calendar_df[calendar_df['Status'] == 'Completed']
    if not completed_races.empty:
        for _, race in completed_races.iterrows():
            try:
                round_num = race['RoundNumber']
                winners[round_num] = get_race_winner(2025, round_num)
            except Exception as e:
                logger.warning(f"Couldn't fetch winner for Round {round_num}: {e}")
    
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
            "year": 2025,
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

def display_rich_calendar_table(calendar_data):
    """
    Display the calendar data in a beautiful Rich formatted table
    
    Args:
        calendar_data (dict): Calendar data object with races and season info
    """
    console = Console(width=120)
    
    # Create a beautiful header
    title = Text("Formula 1 Race Calendar", style="bold white on red")
    subtitle = Text(f"Season {calendar_data['season']['year']}", style="italic")
    
    console.print(Panel(title, subtitle=subtitle, border_style="red", expand=False))
    console.print()
    
    # Display season overview
    season_info = calendar_data['season']
    overview = Table(show_header=False, box=box.SIMPLE, expand=True)
    overview.add_column("Stat", style="bright_black", justify="right")
    overview.add_column("Value", style="white bold", justify="left")
    
    overview.add_row("Total Races:", str(season_info['total_races']))
    overview.add_row("Sprint Races:", str(len(calendar_data['sprint_races'])))
    overview.add_row("Completed:", str(season_info['status_summary'].get('Completed', 0)))
    overview.add_row("Ongoing:", str(season_info['status_summary'].get('Ongoing', 0)))
    overview.add_row("Upcoming:", str(season_info['status_summary'].get('Upcoming', 0)))
    overview.add_row("Season Span:", season_info['season_span'])
    
    console.print(Panel(overview, title="Season Overview", border_style="bright_cyan", padding=(1, 2)))
    console.print()
    
    # Display featured races
    featured_races = Layout()
    featured_races.split_column(
        Layout(name="title", size=3),
        Layout(name="races", size=35)
    )
    featured_races["races"].split_row(
        Layout(name="ongoing"),
        Layout(name="next"),
        Layout(name="last")
    )
    
    featured_races["title"].update(Text("Featured Races", style="bold white on red", justify="center"))
    
    # Ongoing race
    if calendar_data['ongoing_race']:
        race = calendar_data['ongoing_race']
        panel_content = [
            Text(f"Round {race['round']}: {race['name']}", style="bold white"),
            Text(f"Date: {race['date_formatted']}", style="yellow"),
            Text(f"Circuit: {race['circuit']}", style="magenta"),
            Text(f"Location: {race['location']}, {race['country']}", style="green"),
            Text("HAPPENING NOW", style="bold white on blue")
        ]
        if race['is_sprint']:
            panel_content.append(Text("SPRINT RACE", style="black on yellow"))
        ongoing_panel = Panel(
            Group(*panel_content),
            title="🏎️ Ongoing Race",
            border_style="blue",
            padding=(1, 2)
        )
        featured_races["ongoing"].update(ongoing_panel)
    else:
        featured_races["ongoing"].update(Panel(
            "No races are currently in progress",
            title="🏎️ Ongoing Race",
            border_style="dim blue",
            padding=(1, 2)
        ))
    
    # Next race
    if calendar_data['next_race']:
        race = calendar_data['next_race']
        race_date = datetime.strptime(race['date'], '%Y-%m-%d') if race['date'] else None
        today = datetime.now()
        days_until = (race_date - today).days if race_date else None
        
        panel_content = [
            Text(f"Round {race['round']}: {race['name']}", style="bold white"),
            Text(f"Date: {race['date_formatted']}", style="yellow"),
            Text(f"Circuit: {race['circuit']}", style="magenta"),
            Text(f"Location: {race['location']}, {race['country']}", style="green")
        ]
        
        if days_until is not None:
            panel_content.append(Text(f"Countdown: {days_until} days", style="yellow"))
        
        if race['is_sprint']:
            panel_content.append(Text("SPRINT RACE", style="black on yellow"))
        
        next_panel = Panel(
            Group(*panel_content),
            title="🔜 Next Race",
            border_style="bright_red",
            padding=(1, 2)
        )
        featured_races["next"].update(next_panel)
    else:
        featured_races["next"].update(Panel(
            "No upcoming races scheduled",
            title="🔜 Next Race",
            border_style="dim red",
            padding=(1, 2)
        ))
    
    # Last completed race
    if calendar_data['last_completed_race']:
        race = calendar_data['last_completed_race']
        panel_content = [
            Text(f"Round {race['round']}: {race['name']}", style="bold white"),
            Text(f"Date: {race['date_formatted']}", style="yellow"),
            Text(f"Circuit: {race['circuit']}", style="magenta"),
            Text(f"Location: {race['location']}, {race['country']}", style="green")
        ]
        
        if race.get('winner') and race['winner']:
            panel_content.append(Text(f"Winner: {race['winner']['display']}", style="bright_yellow bold"))
        
        if race['is_sprint']:
            panel_content.append(Text("SPRINT RACE", style="black on yellow"))
        
        last_panel = Panel(
            Group(*panel_content),
            title="✅ Last Completed Race",
            border_style="green",
            padding=(1, 2)
        )
        featured_races["last"].update(last_panel)
    else:
        featured_races["last"].update(Panel(
            "No races have been completed yet",
            title="✅ Last Completed Race",
            border_style="dim green",
            padding=(1, 2)
        ))
    
    console.print(featured_races)
    console.print()
    
    # Create the full race calendar table
    console.print(Text("Full Race Calendar", style="bold white on red"))
    console.print()
    
    table = Table(
        show_header=True, 
        header_style="bold white on dark_red", 
        border_style="red",
        box=box.ROUNDED,
        title_justify="center",
        expand=True
    )
    
    # Add columns
    table.add_column("Round", style="dim cyan", justify="center", no_wrap=True)
    table.add_column("Event", style="bold white", justify="left")
    table.add_column("Date", style="yellow", justify="center")
    table.add_column("Status", style="", justify="center")
    table.add_column("Circuit", style="magenta", justify="left")
    table.add_column("Winner", style="bright_green", justify="left")
    table.add_column("Sprint", style="yellow", justify="center")
    
    # Add rows
    races = calendar_data['races']
    for race in races:
        # Skip testing events
        if race['round'] == 0:
            continue
            
        round_num = str(race['round']) if race['round'] is not None else "-"
        
        # Set status style
        status_style = ""
        if race['status'] == "Completed":
            status_style = "green"
        elif race['status'] == "Ongoing":
            status_style = "blue bold"
        elif race['status'] == "Upcoming":
            status_style = "yellow"
        
        # Get winner display if available
        winner_display = race['winner'].get('display', '') if race.get('winner') else ''
        
        # Sprint indicator
        sprint = "✓" if race['is_sprint'] else ""
        
        table.add_row(
            round_num,
            race['name'],
            race['date_formatted'],
            Text(race['status'], style=status_style),
            race['circuit'],
            winner_display,
            sprint
        )
    
    console.print(table)
    
    # Add footer
    console.print()
    console.print(f"Data provided by FastF1 API | Last updated: {calendar_data['last_updated']}", style="dim")
    console.print("© 2024 | Created with Rich", style="dim")

def main():
    """Main function to fetch and display F1 calendar data with Rich formatting"""
    try:
        # Allow simulating a specific date for testing
        # simulated_date = datetime(2025, 5, 17)  # Example: May 17, 2025
        simulated_date = None # Use current date
        
        # Fetch calendar data
        calendar_df = fetch_f1_calendar(2025)
        
        # Prepare data for display with structured format
        calendar_data = prepare_calendar_data(calendar_df, simulated_date)
        
        # Display rich formatted calendar table
        display_rich_calendar_table(calendar_data)
        
        logger.info("Rich display completed successfully")
        
    except Exception as e:
        logger.error(f"Error in rich display process: {e}")

if __name__ == "__main__":
    main() 