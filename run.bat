@echo off
echo Running F1 Calendar App

REM Check if .env file exists
if not exist .env (
    echo Error: .env file not found.
    echo Please create a .env file with the following variables:
    echo SUPABASE_URL=your_supabase_url
    echo SUPABASE_KEY=your_supabase_key
    echo FASTF1_CACHE_DIR=./fastf1_cache
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set up Supabase tables
echo Setting up Supabase tables...
python setup_supabase.py

REM Fetch F1 calendar data
echo Fetching F1 calendar data...
python fetch_calendar.py

REM Display calendar data
echo Displaying F1 calendar data...
python display_calendar.py

echo Done!
pause 