#!/usr/bin/env python3
"""
Test script for Supabase database connection
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def test_supabase_connection(database_url):
    """Test connection to Supabase database"""
    
    print("🔍 Testing Supabase Database Connection")
    print("=" * 50)
    
    try:
        # Parse the database URL
        parsed = urlparse(database_url)
        
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path[1:]}")  # Remove leading slash
        print(f"Username: {parsed.username}")
        print(f"Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
        print()
        
        # Test DNS resolution first
        print("🌐 Testing DNS resolution...")
        import socket
        try:
            ip = socket.gethostbyname(parsed.hostname)
            print(f"✅ DNS resolution successful: {parsed.hostname} -> {ip}")
        except socket.gaierror as e:
            print(f"❌ DNS resolution failed: {e}")
            print("   Please check if the hostname is correct in your Supabase project settings.")
            return False
        
        # Test database connection
        print("\n🔌 Testing database connection...")
        
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connection successful!")
        print(f"   PostgreSQL version: {version}")
        
        # Test if we can create tables (check permissions)
        print("\n🔐 Testing database permissions...")
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    test_field VARCHAR(100)
                );
            """)
            cursor.execute("DROP TABLE IF EXISTS test_connection;")
            connection.commit()
            print("✅ Database permissions OK (can create/drop tables)")
        except Exception as e:
            print(f"⚠️  Limited database permissions: {e}")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Supabase database connection test completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPossible issues:")
        print("1. Incorrect hostname or project reference ID")
        print("2. Wrong password")
        print("3. Database not accessible from your IP")
        print("4. Supabase project is paused or deleted")
        print("\nPlease check your Supabase project settings.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_supabase_url_from_user():
    """Get Supabase URL from user input"""
    print("Please enter your Supabase database URL:")
    print("Format: postgresql://postgres:password@db.project-ref.supabase.co:5432/postgres")
    print()
    
    url = input("Database URL: ").strip()
    return url

def main():
    """Main function"""
    print("Supabase Database Connection Tester")
    print("=" * 40)
    print()
    
    # Check if URL is provided as argument
    if len(sys.argv) > 1:
        database_url = sys.argv[1]
    else:
        # Try to get from environment
        database_url = os.getenv('SUPABASE_DATABASE_URL')
        
        if not database_url:
            database_url = get_supabase_url_from_user()
    
    if not database_url:
        print("❌ No database URL provided")
        return 1
    
    # Test the connection
    success = test_supabase_connection(database_url)
    
    if success:
        print("\n📝 To use this database in your Django project:")
        print("1. Update your .env file:")
        print(f"   DATABASE_URL={database_url}")
        print("2. Run migrations:")
        print("   python manage.py migrate")
        print("3. Create a superuser:")
        print("   python manage.py createsuperuser")
        return 0
    else:
        print("\n🔧 Troubleshooting steps:")
        print("1. Check your Supabase project dashboard")
        print("2. Verify the project reference ID in the URL")
        print("3. Confirm your database password")
        print("4. Ensure your IP is allowed (check Supabase network restrictions)")
        print("5. Make sure the project is not paused")
        return 1

if __name__ == "__main__":
    sys.exit(main())
