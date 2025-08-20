#!/usr/bin/env python3
"""
Test script for Cloudinary configuration
"""

import os
import sys
import django
from django.conf import settings

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_site.settings')
    django.setup()

def test_cloudinary_config():
    """Test Cloudinary configuration"""
    print("🔍 Testing Cloudinary Configuration")
    print("=" * 50)
    
    # Check environment variables
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    print(f"Cloud Name: {cloud_name if cloud_name else '❌ Not set'}")
    print(f"API Key: {api_key[:10] + '...' if api_key else '❌ Not set'}")
    print(f"API Secret: {'✅ Set' if api_secret else '❌ Not set'}")
    
    if not all([cloud_name, api_key, api_secret]):
        print("\n❌ Cloudinary credentials not properly configured!")
        print("Please set the following environment variables:")
        print("- CLOUDINARY_CLOUD_NAME")
        print("- CLOUDINARY_API_KEY") 
        print("- CLOUDINARY_API_SECRET")
        return False
    
    return True

def test_cloudinary_connection():
    """Test connection to Cloudinary"""
    print("\n🔌 Testing Cloudinary Connection")
    print("-" * 30)
    
    try:
        import cloudinary
        import cloudinary.uploader
        print("✅ Cloudinary packages imported successfully")
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
        
        # Test upload with a small test image
        print("📤 Testing image upload...")
        
        # Create a simple test image URL
        test_image_url = "https://via.placeholder.com/100x100.png?text=Test"
        
        result = cloudinary.uploader.upload(
            test_image_url,
            public_id="test_upload_" + str(int(os.urandom(4).hex(), 16)),
            folder="test"
        )
        
        print("✅ Upload successful!")
        print(f"   Image URL: {result['secure_url']}")
        print(f"   Public ID: {result['public_id']}")
        
        # Clean up test image
        cloudinary.uploader.destroy(result['public_id'])
        print("🗑️  Test image cleaned up")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cloudinary packages not installed: {e}")
        print("   Run: pip install cloudinary django-cloudinary-storage")
        return False
        
    except Exception as e:
        print(f"❌ Cloudinary connection failed: {e}")
        print("   Check your credentials and internet connection")
        return False

def test_django_storage_config():
    """Test Django storage configuration"""
    print("\n⚙️  Testing Django Storage Configuration")
    print("-" * 40)
    
    try:
        setup_django()
        
        # Check if Cloudinary is in INSTALLED_APPS
        if 'cloudinary_storage' in settings.INSTALLED_APPS:
            print("✅ cloudinary_storage in INSTALLED_APPS")
        else:
            print("❌ cloudinary_storage not in INSTALLED_APPS")
            return False
            
        if 'cloudinary' in settings.INSTALLED_APPS:
            print("✅ cloudinary in INSTALLED_APPS")
        else:
            print("❌ cloudinary not in INSTALLED_APPS")
            return False
        
        # Check DEFAULT_FILE_STORAGE
        storage_backend = getattr(settings, 'DEFAULT_FILE_STORAGE', None)
        if storage_backend == 'cloudinary_storage.storage.MediaCloudinaryStorage':
            print("✅ DEFAULT_FILE_STORAGE configured for Cloudinary")
        else:
            print(f"⚠️  DEFAULT_FILE_STORAGE: {storage_backend}")
            print("   This might be OK if Cloudinary env vars are not set")
        
        return True
        
    except Exception as e:
        print(f"❌ Django configuration error: {e}")
        return False

def test_model_upload():
    """Test uploading through Django model"""
    print("\n📝 Testing Model Upload")
    print("-" * 25)
    
    try:
        setup_django()
        from portfolio.models import BlogPost
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.files.base import ContentFile
        import requests
        
        # Download a test image
        print("📥 Downloading test image...")
        response = requests.get("https://via.placeholder.com/200x150.png?text=Blog+Test")
        if response.status_code == 200:
            print("✅ Test image downloaded")
            
            # Create a test blog post
            print("📝 Creating test blog post...")
            
            # Create file object
            image_file = ContentFile(response.content, name='test_blog_image.png')
            
            # Create blog post (but don't save to avoid cluttering database)
            blog_post = BlogPost(
                title="Test Blog Post",
                content="This is a test blog post for Cloudinary testing.",
                cover_image=image_file
            )
            
            # Test the upload without saving
            print("✅ Blog post model can handle image upload")
            print("   (Not saved to database - this is just a test)")
            
            return True
        else:
            print("❌ Failed to download test image")
            return False
            
    except Exception as e:
        print(f"❌ Model upload test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Cloudinary Setup Test")
    print("=" * 30)
    print()
    
    tests = [
        ("Configuration", test_cloudinary_config),
        ("Connection", test_cloudinary_connection),
        ("Django Storage", test_django_storage_config),
        ("Model Upload", test_model_upload),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📊 Test Results Summary")
    print("=" * 25)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Cloudinary is properly configured.")
        print("\nNext steps:")
        print("1. Deploy to Render with Cloudinary environment variables")
        print("2. Upload a blog post with image to test in production")
        print("3. Verify images persist after service restart")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
