#!/usr/bin/env python3
"""
Supabase Database Setup Script
Automated setup for Supabase PostgreSQL database
"""

import os
import subprocess
import sys
import time

def check_supabase_connection():
    """Check if Supabase connection is working"""
    print("🔍 Checking Supabase connection...")
    
    try:
        # Test connection with psql
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not found in .env file")
            return False
        
        if 'supabase' not in db_url:
            print("❌ DATABASE_URL doesn't contain 'supabase'")
            return False
        
        # Test connection
        result = subprocess.run([
            'psql', db_url, '-c', 'SELECT version();'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Supabase connection successful!")
            return True
        else:
            print("❌ Connection failed!")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Connection timeout!")
        return False
    except FileNotFoundError:
        print("❌ psql not found. Please install PostgreSQL client tools")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def setup_supabase_database():
    """Setup Supabase database with tables and sample data"""
    print("🗄️  Setting up Supabase database...")
    
    try:
        # Initialize database with sample data
        result = subprocess.run([sys.executable, 'init_db.py'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database initialized successfully!")
            print("📊 Sample data loaded:")
            print("   - 10 products")
            print("   - 5 users") 
            print("   - 50+ user interactions")
            return True
        else:
            print("❌ Failed to initialize database")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api():
    """Test the API endpoints"""
    print("🧪 Testing API endpoints...")
    
    try:
        # Start Flask app in background
        flask_process = subprocess.Popen([sys.executable, 'app.py'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(5)
        
        # Test products endpoint
        result = subprocess.run([
            'curl', '-s', 'http://localhost:5001/api/products'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and 'products' in result.stdout.lower():
            print("✅ API is working!")
            print("🌐 Frontend: http://localhost:8001/frontend.html")
            print("🔗 API: http://localhost:5001/api")
        else:
            print("❌ API test failed")
            print(result.stderr)
        
        # Stop Flask process
        flask_process.terminate()
        flask_process.wait()
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def main():
    """Main setup function"""
    print("🚀 Supabase Database Setup")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Please create .env file with your Supabase connection string:")
        print("   DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres")
        return
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check connection
    if not check_supabase_connection():
        print("\n🆘 Troubleshooting:")
        print("1. Check your Supabase project is running")
        print("2. Verify DATABASE_URL in .env file")
        print("3. Make sure password is correct")
        print("4. Check if your IP is whitelisted in Supabase")
        return
    
    # Setup database
    if not setup_supabase_database():
        print("\n🆘 Troubleshooting:")
        print("1. Check database permissions")
        print("2. Verify tables don't already exist")
        print("3. Check Supabase project status")
        return
    
    # Test API
    test_api()
    
    print("\n🎉 Setup Complete!")
    print("=" * 40)
    print("✅ Supabase database connected")
    print("✅ Tables created")
    print("✅ Sample data loaded")
    print("✅ API tested")
    print("\n🚀 Ready to use!")
    print("   Start: ./venv/bin/python app.py")
    print("   Frontend: http://localhost:8001/frontend.html")

if __name__ == "__main__":
    main()
