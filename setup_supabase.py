#!/usr/bin/env python3
"""
Script to set up Supabase database tables for the F1 calendar application.
"""

import logging
from config import get_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_f1_calendar_table():
    """
    Create the F1 calendar table in Supabase
    """
    try:
        logger.info("Connecting to Supabase")
        supabase = get_supabase_client()
        
        # SQL for creating the F1 calendar table
        sql = """
        CREATE TABLE IF NOT EXISTS f1_calendar (
            id SERIAL PRIMARY KEY,
            event_name TEXT NOT NULL,
            round INT,
            country TEXT,
            location TEXT,
            circuit_name TEXT,
            event_date DATE,
            event_format TEXT,
            session1_name TEXT,
            session1_date TIMESTAMP WITH TIME ZONE,
            session2_name TEXT,
            session2_date TIMESTAMP WITH TIME ZONE,
            session3_name TEXT,
            session3_date TIMESTAMP WITH TIME ZONE,
            session4_name TEXT,
            session4_date TIMESTAMP WITH TIME ZONE,
            session5_name TEXT,
            session5_date TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create RLS policy for public read access
        ALTER TABLE f1_calendar ENABLE ROW LEVEL SECURITY;
        
        -- Allow public read access
        CREATE POLICY "Allow public read access"
            ON f1_calendar FOR SELECT
            USING (true);
            
        -- Allow authenticated users to insert, update, delete
        CREATE POLICY "Allow authenticated insert"
            ON f1_calendar FOR INSERT
            TO authenticated
            WITH CHECK (true);
            
        CREATE POLICY "Allow authenticated update"
            ON f1_calendar FOR UPDATE
            TO authenticated
            USING (true);
            
        CREATE POLICY "Allow authenticated delete"
            ON f1_calendar FOR DELETE
            TO authenticated
            USING (true);
        """
        
        # Execute the SQL to create the table
        logger.info("Creating f1_calendar table in Supabase")
        response = supabase.rpc("exec_sql", {"query": sql}).execute()
        
        logger.info("Successfully created f1_calendar table")
        return response
    
    except Exception as e:
        logger.error(f"Error creating f1_calendar table: {e}")
        raise

def main():
    """Main function to set up Supabase tables"""
    try:
        # Create F1 calendar table
        create_f1_calendar_table()
        
        logger.info("Supabase setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error in Supabase setup: {e}")

if __name__ == "__main__":
    main() 