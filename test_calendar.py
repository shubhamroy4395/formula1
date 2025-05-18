import fastf1
import pandas as pd
import traceback
import json
from datetime import datetime, timedelta

print("FastF1 API Test for 2025 Calendar")
print("---------------------------------")

# Function to determine race status based on date
def get_race_status(race_date):
    """Determine the status of a race based on date comparison"""
    # Handle empty or None values
    if race_date is None or pd.isna(race_date):
        return "Unknown"
    
    # Make sure we have a datetime object
    try:
        if not isinstance(race_date, datetime):
            race_date = pd.to_datetime(race_date)
        
        today = datetime.now()
        
        # For race weekend consideration (F1 race weekends typically span 3 days)
        race_weekend_start = race_date - timedelta(days=2)  # 2 days before race (typically Friday practice)
        race_weekend_end = race_date + timedelta(hours=6)  # Few hours after the race to account for finish time
        
        # Mark as completed only on the day after the race (day+1)
        race_day_plus_one = race_date + timedelta(days=1)
        
        if race_date.date() < today.date() and race_day_plus_one.date() <= today.date():
            return "Completed"
        elif race_weekend_start <= today <= race_weekend_end:
            return "Ongoing"
        else:
            return "Upcoming"
    except Exception as e:
        print(f"Error calculating race status: {e}")
        return "Unknown"

# Function to get race winner for completed races
def get_race_winner(year, race_round):
    try:
        print(f"  Fetching results for round {race_round}...")
        # Get the race session for this event
        session = fastf1.get_session(year, race_round, 'Race')
        # Load the session data
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
        print(f"  Error fetching race winner: {e}")
        return {}

# Create a structured data object for the frontend
def create_calendar_data_object(calendar_df, winners=None):
    """Create a comprehensive data object with all calendar information"""
    if winners is None:
        winners = {}
    
    # Overall season data
    first_date = pd.to_datetime(calendar_df['EventDate'].min()) if not calendar_df.empty else None
    last_date = pd.to_datetime(calendar_df['EventDate'].max()) if not calendar_df.empty else None
    
    season_data = {
        "year": 2025,
        "total_races": len(calendar_df),
        "first_race_date": first_date.strftime('%Y-%m-%d') if first_date else None,
        "last_race_date": last_date.strftime('%Y-%m-%d') if last_date else None,
        "season_span": f"{first_date.strftime('%d %b %Y')} - {last_date.strftime('%d %b %Y')}" if first_date and last_date else "TBA",
        "status_summary": calendar_df['Status'].value_counts().to_dict() if 'Status' in calendar_df.columns else {},
        "format_summary": calendar_df['EventFormat'].value_counts().to_dict() if 'EventFormat' in calendar_df.columns else {}
    }
    
    # Race details as a list
    races = []
    for _, race in calendar_df.iterrows():
        # Basic race info
        race_date = pd.to_datetime(race['EventDate']) if pd.notna(race['EventDate']) else None
        
        race_data = {
            "round": int(race['RoundNumber']),
            "name": race['EventName'],
            "official_name": race['OfficialEventName'],
            "country": race['Country'],
            "location": race['Location'],
            "circuit": race['CircuitName'] if 'CircuitName' in race.index else race['Location'],
            "date": race_date.strftime('%Y-%m-%d') if race_date else None,
            "date_formatted": race_date.strftime('%d %b %Y') if race_date else "TBA",
            "status": race['Status'] if 'Status' in race.index else "Unknown",
            "format": race['EventFormat'],
            "is_sprint": race['EventFormat'] == 'sprint_qualifying',
            "winner": winners.get(race['RoundNumber'], {})
        }
        
        # Session information if available
        if 'Session1' in race.index and pd.notna(race['Session1']):
            sessions = []
            for i in range(1, 6):  # Up to 5 sessions
                session_name_key = f'Session{i}'
                session_date_key = f'Session{i}Date'
                
                if session_name_key in race.index and pd.notna(race[session_name_key]):
                    session_date = pd.to_datetime(race[session_date_key]) if pd.notna(race[session_date_key]) else None
                    sessions.append({
                        "name": race[session_name_key],
                        "date": session_date.strftime('%Y-%m-%d') if session_date else None,
                        "date_formatted": session_date.strftime('%d %b %Y %H:%M') if session_date else "TBA"
                    })
            
            race_data["sessions"] = sessions
        
        races.append(race_data)
    
    # Full data object
    calendar_data = {
        "season": season_data,
        "races": races,
        "sprint_races": [race for race in races if race["is_sprint"]],
        "next_race": next((race for race in races if race["status"] == "Upcoming"), None),
        "ongoing_race": next((race for race in races if race["status"] == "Ongoing"), None),
        "last_completed_race": next((race for race in sorted(races, key=lambda x: -x["round"]) if race["status"] == "Completed"), None),
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return calendar_data

try:
    print("Attempting to fetch 2025 calendar...")
    
    calendar = fastf1.get_event_schedule(2025, backend='ergast')
    
    print(f"Success! Retrieved {len(calendar)} races for 2025")
    
    # For testing purposes, let's set a simulated date in 2025
    # This lets us simulate some races being completed
    simulated_date = datetime(2025, 5, 17)  # May 17, 2025
    print(f"\nSimulated current date: {simulated_date.strftime('%d %b %Y')}")
    
    # Calculate race status using the simulated date instead of actual current date
    def get_simulated_status(race_date):
        if race_date is None or pd.isna(race_date):
            return "Unknown"
        
        try:
            if not isinstance(race_date, datetime):
                race_date = pd.to_datetime(race_date)
            
            # Use simulated date instead of actual date
            # Mark as completed only on the day after the race (day+1)
            race_day_plus_one = race_date + timedelta(days=1)
            
            if race_date.date() < simulated_date.date() and race_day_plus_one.date() <= simulated_date.date():
                return "Completed"
            elif (race_date - timedelta(days=2)) <= simulated_date <= (race_date + timedelta(hours=6)):
                return "Ongoing"
            else:
                return "Upcoming"
        except Exception as e:
            print(f"Error calculating race status: {e}")
            return "Unknown"
    
    # Add status to the dataframe using the simulated date
    calendar['Status'] = calendar['EventDate'].apply(get_simulated_status)
    
    # Count races by status
    status_counts = calendar['Status'].value_counts().to_dict()
    print(f"Status summary: {status_counts}")
    
    # Fetch race winners for completed races
    print("\nFetching race winners for completed races...")
    winners = {}
    
    # Get list of completed races
    completed_races = calendar[calendar['Status'] == 'Completed']
    
    for _, race in completed_races.iterrows():
        round_num = race['RoundNumber']
        winners[round_num] = get_race_winner(2025, round_num)
    
    # Create the comprehensive data object
    print("\nCreating comprehensive data object...")
    calendar_data_object = create_calendar_data_object(calendar, winners)
    
    # Display key information
    print("\n2025 F1 RACE CALENDAR DATA OBJECT SUMMARY:")
    print("=========================================")
    print(f"Total races: {calendar_data_object['season']['total_races']}")
    print(f"Season span: {calendar_data_object['season']['season_span']}")
    print(f"Race status: {calendar_data_object['season']['status_summary']}")
    print(f"Race formats: {calendar_data_object['season']['format_summary']}")
    print(f"Sprint races: {len(calendar_data_object['sprint_races'])}")
    
    # Print information about next race
    if calendar_data_object['next_race']:
        next_race = calendar_data_object['next_race']
        print("\nNext race:")
        print(f"Round {next_race['round']}: {next_race['name']} ({next_race['date_formatted']})")
    
    # Print information about ongoing race
    if calendar_data_object['ongoing_race']:
        ongoing_race = calendar_data_object['ongoing_race']
        print("\nOngoing race:")
        print(f"Round {ongoing_race['round']}: {ongoing_race['name']} ({ongoing_race['date_formatted']})")
    
    # Print information about last completed race with winner
    if calendar_data_object['last_completed_race']:
        last_race = calendar_data_object['last_completed_race']
        print("\nLast completed race:")
        print(f"Round {last_race['round']}: {last_race['name']} ({last_race['date_formatted']})")
        if last_race['winner']:
            print(f"Winner: {last_race['winner']['display']}")
    
    # Save the data to JSON file
    print("\nSaving data to calendar_data.json...")
    with open('calendar_data.json', 'w') as f:
        json.dump(calendar_data_object, f, indent=2)
    
    print("Data successfully saved and ready for frontend!")
    
    # Simple tabular format for console output
    print("\n2025 F1 RACE CALENDAR WITH STATUS AND WINNERS:")
    print("===========================================")
    print("Round | Date       | Grand Prix               | Country        | Location        | Status     | Winner")
    print("--------------------------------------------------------------------------------------------")
    
    # Print each race on one line with simple formatting
    for _, race in calendar.iterrows():
        round_num = race['RoundNumber']
        event_name = race['EventName']
        country = race['Country']
        location = race['Location']
        status = race['Status']
        
        # Format date
        if pd.notna(race['EventDate']):
            date_obj = pd.to_datetime(race['EventDate'])
            date_str = date_obj.strftime('%d %b %Y')
        else:
            date_str = 'TBA'
        
        # Add status indicator
        status_indicator = {
            'Completed': '✓',
            'Ongoing': '▶',
            'Upcoming': '○',
            'Unknown': '?'
        }.get(status, '')
        
        # Get winner for completed races
        winner_display = winners.get(round_num, {}).get('display', "") if status == "Completed" else ""
        
        # Print with fixed width including status and winner
        print(f"{round_num:2}    | {date_str:10} | {event_name[:25]:<25} | {country[:15]:<15} | {location[:15]:<15} | {status_indicator} {status:<10} | {winner_display}")
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc() 