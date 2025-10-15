#!/usr/bin/env python3
"""
Supabase Connection String Helper
Interactive script to get your Supabase connection string
"""

import os

def get_supabase_connection():
    """Get Supabase connection string from user"""
    print("🚀 Supabase Connection Setup")
    print("=" * 40)
    
    print("\n📋 To get your Supabase connection string:")
    print("1. Go to https://supabase.com")
    print("2. Sign in to your account")
    print("3. Select your project")
    print("4. Go to Settings → Database")
    print("5. Scroll down to 'Connection string'")
    print("6. Copy the 'URI' connection string")
    
    print("\n📝 The connection string looks like:")
    print("postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres")
    
    print("\n" + "=" * 40)
    
    # Get connection string from user
    connection_string = input("Paste your Supabase connection string: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided!")
        return False
    
    if not connection_string.startswith('postgresql://'):
        print("❌ Invalid connection string format!")
        print("   Should start with 'postgresql://'")
        return False
    
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
    
    print(f"\n✅ Connection string saved to .env file!")
    print(f"   {connection_string}")
    
    print("\n🔧 Next steps:")
    print("1. Run: ./venv/bin/python setup_supabase.py")
    print("2. Or manually: ./venv/bin/python init_db.py")
    print("3. Start app: ./venv/bin/python app.py")
    
    return True

if __name__ == "__main__":
    get_supabase_connection()
