#!/usr/bin/env python3
"""
Test script for MongoDB connection
"""

import os
import sys
from urllib.parse import urlparse

def test_mongodb_connection(mongodb_uri):
    """Test connection to MongoDB database"""
    
    print("🔍 Testing MongoDB Connection")
    print("=" * 50)
    
    try:
        # Import MongoDB packages
        try:
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
            print("✅ PyMongo package available")
        except ImportError as e:
            print(f"❌ PyMongo not installed: {e}")
            print("   Run: pip install pymongo dnspython")
            return False
        
        # Parse the MongoDB URI
        parsed = urlparse(mongodb_uri)
        print(f"Host: {parsed.hostname}")
        print(f"Database: {parsed.path[1:] if parsed.path else 'default'}")
        print(f"Username: {parsed.username if parsed.username else 'None'}")
        print(f"Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
        print()
        
        # Test MongoDB connection
        print("🔌 Testing MongoDB connection...")
        
        # Create client with timeout
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get server info
        server_info = client.server_info()
        print(f"   MongoDB version: {server_info['version']}")
        
        # Test database operations
        print("\n🔐 Testing database operations...")
        db_name = parsed.path[1:] if parsed.path else 'personal_site'
        db = client[db_name]
        
        # Test collection creation and basic operations
        test_collection = db.test_connection
        
        # Insert test document
        test_doc = {"test": "connection", "timestamp": "2024"}
        result = test_collection.insert_one(test_doc)
        print(f"✅ Document inserted with ID: {result.inserted_id}")
        
        # Read test document
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ Document read successfully")
        
        # Delete test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Document deleted successfully")
        
        # Close connection
        client.close()
        
        print("\n🎉 MongoDB connection test completed successfully!")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\nPossible issues:")
        print("1. Incorrect MongoDB URI")
        print("2. Network connectivity issues")
        print("3. MongoDB server not running")
        print("4. Authentication failed")
        return False
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB server selection timeout: {e}")
        print("\nPossible issues:")
        print("1. MongoDB server not reachable")
        print("2. Firewall blocking connection")
        print("3. Incorrect hostname or port")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def get_mongodb_uri_from_user():
    """Get MongoDB URI from user input"""
    print("Please enter your MongoDB URI:")
    print("Local: mongodb://localhost:27017/personal_site")
    print("Atlas: mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/personal_site")
    print()
    
    uri = input("MongoDB URI: ").strip()
    return uri

def main():
    """Main function"""
    print("MongoDB Connection Tester")
    print("=" * 30)
    print()
    
    # Check if URI is provided as argument
    if len(sys.argv) > 1:
        mongodb_uri = sys.argv[1]
    else:
        # Try to get from environment
        mongodb_uri = os.getenv('MONGODB_URI')
        
        if not mongodb_uri:
            mongodb_uri = get_mongodb_uri_from_user()
    
    if not mongodb_uri:
        print("❌ No MongoDB URI provided")
        return 1
    
    # Test the connection
    success = test_mongodb_connection(mongodb_uri)
    
    if success:
        print("\n📝 To use this database in your Django project:")
        print("1. Install required packages:")
        print("   pip install djongo pymongo dnspython")
        print("2. Update your .env file:")
        print(f"   MONGODB_URI={mongodb_uri}")
        print("3. Run migrations:")
        print("   python manage.py migrate")
        print("4. Create a superuser:")
        print("   python manage.py createsuperuser")
        return 0
    else:
        print("\n🔧 Troubleshooting steps:")
        print("1. Check your MongoDB Atlas dashboard (if using Atlas)")
        print("2. Verify your username and password")
        print("3. Ensure your IP is whitelisted")
        print("4. Check network connectivity")
        print("5. Verify the cluster is running")
        return 1

if __name__ == "__main__":
    sys.exit(main())
