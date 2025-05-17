import os
from dotenv import load_dotenv
from supabase import create_client, Client
import fastf1

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# FastF1 cache configuration
FASTF1_CACHE_DIR = os.getenv("FASTF1_CACHE_DIR", "./fastf1_cache")

# Initialize FastF1 cache
fastf1.Cache.enable_cache(FASTF1_CACHE_DIR)

def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client
    
    Returns:
        Client: Initialized Supabase client
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and KEY must be set in environment variables")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY) 