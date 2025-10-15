#!/usr/bin/env python3
"""
Supabase REST API Client
Uses the Supabase REST API instead of direct PostgreSQL connection
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        self.supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase configuration. Check your .env file.")
        
        # Ensure URL ends with /
        if not self.supabase_url.endswith('/'):
            self.supabase_url += '/'
        
        self.rest_url = f"{self.supabase_url}rest/v1"
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def test_connection(self):
        """Test the Supabase connection"""
        try:
            # Try to access the health endpoint
            response = requests.get(
                f"{self.supabase_url}health",
                headers={'apikey': self.supabase_key}
            )
            
            if response.status_code == 200:
                print("✅ Supabase connection successful!")
                return True
            else:
                print(f"❌ Connection failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def select(self, table, columns="*", filters=None):
        """Select data from a table"""
        url = f"{self.rest_url}/{table}"
        params = {}
        
        if columns != "*":
            params["select"] = columns
            
        if filters:
            for key, value in filters.items():
                params[key] = value
                
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    
    def insert(self, table, data):
        """Insert data into a table"""
        url = f"{self.rest_url}/{table}"
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    
    def update(self, table, data, filters):
        """Update data in a table"""
        url = f"{self.rest_url}/{table}"
        params = filters
        
        response = requests.patch(url, headers=self.headers, json=data, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    
    def delete(self, table, filters):
        """Delete data from a table"""
        url = f"{self.rest_url}/{table}"
        params = filters
        
        response = requests.delete(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

# Example usage
if __name__ == "__main__":
    supabase = SupabaseClient()
    supabase.test_connection()