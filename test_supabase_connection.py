#!/usr/bin/env python
"""
Test script to verify Supabase database connection
Run this after adding your database password to .env
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_site.settings')
django.setup()

from django.db import connection
from django.core.management.color import make_style

style = make_style()

def test_database_connection():
    """Test the database connection"""
    try:
        print(style.HTTP_INFO("🔍 Testing Supabase database connection..."))
        
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(style.SUCCESS(f"✅ Connected to PostgreSQL: {version}"))
            
            # Test if we can create tables (check permissions)
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            print(style.SUCCESS(f"✅ Database: {db_info[0]}, User: {db_info[1]}"))
            
            # Check if we have necessary permissions
            cursor.execute("""
                SELECT has_database_privilege(current_user, current_database(), 'CREATE') as can_create,
                       has_database_privilege(current_user, current_database(), 'CONNECT') as can_connect;
            """)
            permissions = cursor.fetchone()
            
            if permissions[0]:
                print(style.SUCCESS("✅ CREATE permission: Yes"))
            else:
                print(style.ERROR("❌ CREATE permission: No"))
                
            if permissions[1]:
                print(style.SUCCESS("✅ CONNECT permission: Yes"))
            else:
                print(style.ERROR("❌ CONNECT permission: No"))
        
        return True
        
    except Exception as e:
        print(style.ERROR(f"❌ Database connection failed: {e}"))
        print(style.WARNING("\n💡 Troubleshooting tips:"))
        print("1. Check your SUPABASE_DB_PASSWORD in .env file")
        print("2. Verify your Supabase project is active")
        print("3. Check if your IP is allowed in Supabase settings")
        print("4. Ensure the database host is correct")
        return False

def show_current_config():
    """Show current database configuration"""
    print(style.HTTP_INFO("\n📋 Current Database Configuration:"))
    db_config = settings.DATABASES['default']
    
    print(f"Engine: {db_config['ENGINE']}")
    print(f"Host: {db_config['HOST']}")
    print(f"Port: {db_config['PORT']}")
    print(f"Database: {db_config['NAME']}")
    print(f"User: {db_config['USER']}")
    print(f"Password: {'*' * len(db_config['PASSWORD']) if db_config['PASSWORD'] else 'NOT SET'}")

if __name__ == "__main__":
    print(style.HTTP_INFO("🚀 Supabase Connection Test"))
    print("=" * 50)
    
    show_current_config()
    print()
    
    if test_database_connection():
        print(style.SUCCESS("\n🎉 Database connection successful!"))
        print(style.HTTP_INFO("You can now run: python manage.py migrate"))
    else:
        print(style.ERROR("\n💥 Database connection failed!"))
        print(style.WARNING("Please check your configuration and try again."))
