# Paddock by Shubham - F1 Calendar App

A comprehensive web application that fetches and displays Formula 1 race calendar data using FastF1 APIs with multiple visualization options and data storage capabilities.

## Features

- **Data Retrieval**: Fetches F1 race calendar data using the FastF1 API
- **Multiple Visualization Options**:
  - Streamlit web interface with interactive elements
  - Plotly interactive HTML charts
  - Rich console output for terminal-based viewing
- **Smart Race Status**: Automatically categorizes races as Completed, Ongoing, or Upcoming
- **Featured Race Card**: Highlights the current/next race with countdown and engaging facts
- **Data Filtering**: Filter races by status (Completed/Ongoing/Upcoming)
- **Season Statistics**: View race counts, participating countries, and season progress
- **Database Integration**: Optional Supabase storage for persistent data

## Project Structure

### Core Components

| File | Description |
|------|-------------|
| `fetch_calendar.py` | Core script to fetch F1 calendar data using FastF1 and store it in Supabase |
| `fetch_and_display.py` | Simplified version that works without Supabase dependency |
| `config.py` | Environment configuration and Supabase client setup |
| `setup_supabase.py` | Scripts to set up required tables in Supabase |
| `requirements.txt` | Python dependencies for the project |

### Visualization Components

| File | Description |
|------|-------------|
| `streamlit_app.py` | Main web application built with Streamlit framework |
| `plotly_display.py` | Creates interactive HTML visualizations using Plotly |
| `rich_display.py` | Console-based visualizations using Rich library |
| `display_calendar.py` | General display utilities for calendar data |

### Run Scripts

| File | Description |
|------|-------------|
| `run.bat` | Windows batch script to set up environment and run the application |
| `run.sh` | Unix/Linux shell script to set up environment and run the application |

## Architecture

The application follows a modular architecture with clear separation of concerns:

1. **Data Layer**:
   - FastF1 API integration for fetching race calendar data
   - Optional Supabase database for persistent storage
   - Data processing and transformation utilities

2. **Visualization Layer**:
   - Multiple independent visualization methods (Streamlit, Plotly, Rich)
   - Each visualization component can work with the processed data

3. **Configuration Layer**:
   - Environment variables management
   - Database connection handling

### Data Flow

```
FastF1 API → fetch_calendar.py → Data Processing → Visualization Components
                              ↘ (Optional) → Supabase Database
```

## Installation

### Prerequisites

- Python 3.8 or later
- pip package manager
- (Optional) Supabase account for database storage

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd paddock-by-shubham
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/macOS: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. (Optional) For Supabase integration, create a `.env` file with:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   FASTF1_CACHE_DIR=./fastf1_cache
   ```

## Usage

### Running the Streamlit Web App

```
streamlit run streamlit_app.py
```

This launches a web interface with the full F1 calendar visualization, including:
- Interactive race calendar with status badges
- Featured race card with countdown and facts
- Filtering options by race status
- Season statistics and metrics

### Using the Console Visualization

```
python rich_display.py
```

Displays a formatted table in the console using the Rich library.

### Generating Interactive HTML Charts

```
python plotly_display.py
```

Creates interactive HTML charts for viewing F1 calendar data.

### Basic Usage Without Database

If you don't want to set up Supabase, you can use the simplified version:

```
python fetch_and_display.py
```

### Automated Setup and Run

- Windows: `run.bat`
- Unix/Linux: `run.sh`

These scripts will set up the environment, install dependencies, and run the application.

## Technologies Used

- **FastF1**: Python library for accessing Formula 1 data
- **Streamlit**: Web application framework for data apps
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **Rich**: Terminal text formatting and display
- **Supabase**: Backend-as-a-Service for database storage

## Future Development

- Driver standings and statistics integration
- Historical race results comparison
- Weather forecast integration for upcoming races
- Team and constructor information
- Circuit maps and layout visualization

## License

[Specify your license here]

## Acknowledgments

- FastF1 API for providing Formula 1 data
- Formula 1 for the sport that inspires this project
