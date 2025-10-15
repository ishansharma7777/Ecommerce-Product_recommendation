#!/usr/bin/env python3
"""
Supabase Client Module
Provides connection to Supabase using the URL and anon key
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# Load environment variables
load_dotenv()

def get_supabase_engine():
    """
    Create a SQLAlchemy engine for Supabase connection
    Uses the NEXT_PUBLIC_SUPABASE_URL and DATABASE_URL
    """
    # Get Supabase connection details
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    database_url = os.getenv('DATABASE_URL')
    
    if not supabase_url or not database_url:
        raise ValueError("Missing Supabase configuration. Please check .env file.")
    
    # Create SQLAlchemy engine with SSL required
    engine = create_engine(
        database_url,
        connect_args={'sslmode': 'require'},
        pool_pre_ping=True,
        pool_recycle=300
    )
    
    return engine

def test_connection():
    """Test the Supabase connection"""
    try:
        engine = get_supabase_engine()
        connection = engine.connect()
        connection.close()
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()