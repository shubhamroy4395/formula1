#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found."
    echo "Please create a .env file with the following variables:"
    echo "SUPABASE_URL=your_supabase_url"
    echo "SUPABASE_KEY=your_supabase_key"
    echo "FASTF1_CACHE_DIR=./fastf1_cache"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set up Supabase tables
echo "Setting up Supabase tables..."
python setup_supabase.py

# Fetch F1 calendar data
echo "Fetching F1 calendar data..."
python fetch_calendar.py

# Display calendar data
echo "Displaying F1 calendar data..."
python display_calendar.py

echo "Done!" 