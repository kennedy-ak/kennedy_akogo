#!/usr/bin/env python
"""
Test script to verify deployment configuration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'OPENAI_API_KEY',
        'GROQ_API_KEY',
        'MNOTIFY_API_KEY',
        'ADMIN_PHONE_NUMBER',
        'ADMIN_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Show partial value for security
            if len(value) > 10:
                display_value = value[:5] + "..." + value[-3:]
            else:
                display_value = "***"
            print(f"✅ {var}: {display_value}")
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def test_django_config():
    """Test Django configuration"""
    print("\n🔍 Testing Django Configuration...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_site.settings')
        import django
        django.setup()
        
        from django.conf import settings
        
        # Test database configuration
        db_config = settings.DATABASES['default']
        print(f"✅ Database Engine: {db_config['ENGINE']}")
        print(f"✅ Database Host: {db_config['HOST']}")
        print(f"✅ Database Name: {db_config['NAME']}")
        
        # Test static files configuration
        print(f"✅ Static URL: {settings.STATIC_URL}")
        print(f"✅ Static Root: {settings.STATIC_ROOT}")
        
        # Test security settings
        print(f"✅ Debug Mode: {settings.DEBUG}")
        print(f"✅ Allowed Hosts: {settings.ALLOWED_HOSTS}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return False

def test_dependencies():
    """Test that all required packages are available"""
    print("\n🔍 Testing Dependencies...")
    
    required_packages = [
        'django',
        'psycopg2',
        'whitenoise',
        'gunicorn',
        'dj_database_url',
        'openai',
        'groq',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: Not available")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages are available!")
        return True

def main():
    """Run all tests"""
    print("🚀 Deployment Configuration Test")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_dependencies,
        test_django_config
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All tests passed! Your configuration is ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
