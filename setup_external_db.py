#!/usr/bin/env python3
"""
External Database Setup Script
Quick setup for external PostgreSQL databases
"""

import os
import subprocess
import sys

def setup_external_database():
    """Setup external PostgreSQL database connection"""
    print("🌐 External PostgreSQL Database Setup")
    print("=" * 40)
    
    print("\n📋 You need these details from your database provider:")
    print("   - Host (e.g., db.example.com)")
    print("   - Port (usually 5432)")
    print("   - Database Name")
    print("   - Username")
    print("   - Password")
    
    print("\n🚀 Popular Free Providers:")
    print("   1. Supabase (500MB free)")
    print("   2. Railway ($5 credit)")
    print("   3. Neon (3GB free)")
    print("   4. ElephantSQL (20MB free)")
    
    print("\n📝 Connection String Format:")
    print("   postgresql://username:password@host:port/database_name")
    
    print("\n🔧 Setup Steps:")
    print("   1. Get connection string from your provider")
    print("   2. Update .env file with DATABASE_URL")
    print("   3. Run: ./venv/bin/python init_db.py")
    print("   4. Run: ./venv/bin/python app.py")
    
    # Get connection details from user
    print("\n" + "=" * 40)
    host = input("Enter database host: ").strip()
    port = input("Enter port (default 5432): ").strip() or "5432"
    database = input("Enter database name: ").strip()
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    if not all([host, database, username, password]):
        print("❌ All fields are required!")
        return False
    
    # Create connection string
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    # Update .env file
    env_file = '.env'
    lines = []
    
    # Read existing .env file
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Update DATABASE_URL
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            lines[i] = f'DATABASE_URL={connection_string}\n'
            updated = True
            break
    
    if not updated:
        lines.append(f'DATABASE_URL={connection_string}\n')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"\n✅ Database URL updated!")
    print(f"   {connection_string}")
    
    # Test connection
    print("\n🧪 Testing connection...")
    try:
        result = subprocess.run([
            'psql', connection_string, '-c', 'SELECT version();'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Connection successful!")
            print("🗄️  Initializing database...")
            
            # Initialize database
            init_result = subprocess.run([sys.executable, 'init_db.py'], capture_output=True, text=True)
            if init_result.returncode == 0:
                print("✅ Database initialized with sample data!")
                print("\n🚀 Ready to start the application:")
                print("   ./venv/bin/python app.py")
            else:
                print("❌ Failed to initialize database")
                print(init_result.stderr)
        else:
            print("❌ Connection failed!")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("❌ Connection timeout!")
    except FileNotFoundError:
        print("❌ psql not found. Please install PostgreSQL client tools")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return True

if __name__ == "__main__":
    setup_external_database()
