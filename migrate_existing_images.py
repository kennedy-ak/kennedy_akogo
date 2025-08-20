#!/usr/bin/env python3
"""
Migration script to move existing blog images to Cloudinary
"""

import os
import sys
import django
import requests
from urllib.parse import urljoin

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_site.settings')
    django.setup()

def migrate_blog_images():
    """Migrate existing blog images to Cloudinary"""
    
    print("🔄 Migrating Blog Images to Cloudinary")
    print("=" * 40)
    
    try:
        from portfolio.models import BlogPost
        from django.conf import settings
        import cloudinary.uploader
        
        # Check if Cloudinary is configured
        if not os.getenv('CLOUDINARY_CLOUD_NAME'):
            print("❌ Cloudinary not configured. Please set environment variables:")
            print("   - CLOUDINARY_CLOUD_NAME")
            print("   - CLOUDINARY_API_KEY")
            print("   - CLOUDINARY_API_SECRET")
            return False
        
        # Get all blog posts with cover images
        blog_posts = BlogPost.objects.exclude(cover_image='').exclude(cover_image__isnull=True)
        
        if not blog_posts.exists():
            print("ℹ️  No blog posts with images found.")
            return True
        
        print(f"📊 Found {blog_posts.count()} blog posts with images")
        print()
        
        migrated = 0
        failed = 0
        
        for post in blog_posts:
            print(f"🔄 Processing: {post.title}")
            
            try:
                # Check if image URL is already from Cloudinary
                if 'cloudinary.com' in str(post.cover_image.url):
                    print("   ✅ Already using Cloudinary - skipping")
                    continue
                
                # Get the current image URL
                current_url = post.cover_image.url
                
                # If it's a relative URL, make it absolute
                if current_url.startswith('/'):
                    base_url = getattr(settings, 'SITE_DOMAIN', 'https://your-site.onrender.com')
                    current_url = urljoin(base_url, current_url)
                
                print(f"   📥 Downloading from: {current_url}")
                
                # Download the current image
                response = requests.get(current_url, timeout=30)
                if response.status_code != 200:
                    print(f"   ❌ Failed to download image: HTTP {response.status_code}")
                    failed += 1
                    continue
                
                # Upload to Cloudinary
                print("   ☁️  Uploading to Cloudinary...")
                
                # Create a meaningful public ID
                public_id = f"blog_covers/{post.slug or post.id}"
                
                result = cloudinary.uploader.upload(
                    response.content,
                    public_id=public_id,
                    folder="blog_covers",
                    resource_type="image",
                    overwrite=True
                )
                
                print(f"   ✅ Uploaded successfully!")
                print(f"   🔗 New URL: {result['secure_url']}")
                
                # Update the blog post with new URL
                # Note: This requires manual intervention as we can't directly
                # set the ImageField to a URL. You'll need to re-upload through admin.
                print(f"   ⚠️  Manual action required:")
                print(f"      1. Go to Django admin")
                print(f"      2. Edit blog post: {post.title}")
                print(f"      3. Replace cover image with new upload")
                print(f"      4. Or use this Cloudinary URL: {result['secure_url']}")
                
                migrated += 1
                
            except Exception as e:
                print(f"   ❌ Failed to migrate: {e}")
                failed += 1
            
            print()
        
        print("📊 Migration Summary")
        print("-" * 20)
        print(f"✅ Successfully processed: {migrated}")
        print(f"❌ Failed: {failed}")
        print(f"📝 Total blog posts: {blog_posts.count()}")
        
        if migrated > 0:
            print("\n📝 Next Steps:")
            print("1. The images have been uploaded to Cloudinary")
            print("2. You need to manually update each blog post in Django admin")
            print("3. Replace the cover image with a new upload")
            print("4. Django will automatically use Cloudinary for new uploads")
        
        return failed == 0
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("   Run: pip install cloudinary django-cloudinary-storage")
        return False
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def list_blog_images():
    """List all blog posts with images"""
    
    print("📋 Blog Posts with Images")
    print("=" * 30)
    
    try:
        from portfolio.models import BlogPost
        
        blog_posts = BlogPost.objects.exclude(cover_image='').exclude(cover_image__isnull=True)
        
        if not blog_posts.exists():
            print("ℹ️  No blog posts with images found.")
            return
        
        for i, post in enumerate(blog_posts, 1):
            print(f"{i}. {post.title}")
            print(f"   Slug: {post.slug}")
            print(f"   Image: {post.cover_image.name}")
            print(f"   URL: {post.cover_image.url}")
            
            # Check if already using Cloudinary
            if 'cloudinary.com' in str(post.cover_image.url):
                print("   Status: ✅ Using Cloudinary")
            else:
                print("   Status: ⚠️  Using local storage")
            print()
        
    except Exception as e:
        print(f"❌ Error listing images: {e}")

def main():
    """Main function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        setup_django()
        list_blog_images()
        return 0
    
    print("🚀 Blog Image Migration Tool")
    print("=" * 35)
    print()
    print("This tool helps migrate existing blog images to Cloudinary")
    print("to prevent them from disappearing on Render deployments.")
    print()
    
    # Check if user wants to proceed
    response = input("Do you want to proceed with migration? (y/N): ").strip().lower()
    if response != 'y':
        print("Migration cancelled.")
        return 0
    
    setup_django()
    
    success = migrate_blog_images()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nRemember to:")
        print("1. Set up Cloudinary environment variables in Render")
        print("2. Redeploy your application")
        print("3. Test uploading new blog images")
        return 0
    else:
        print("\n❌ Migration completed with errors.")
        print("Please check the output above and fix any issues.")
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Blog Image Migration Tool")
        print("Usage:")
        print("  python migrate_existing_images.py          # Run migration")
        print("  python migrate_existing_images.py --list   # List blog images")
        print("  python migrate_existing_images.py --help   # Show this help")
        sys.exit(0)
    
    sys.exit(main())
