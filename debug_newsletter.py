#!/usr/bin/env python
"""
Debug script for newsletter functionality
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_site.settings')
django.setup()

from portfolio.models import NewsletterSubscriber, NewsletterCampaign
from portfolio.newsletter_utils import send_newsletter_to_all, send_email
from django.core.management.color import make_style

style = make_style()

def debug_newsletter():
    print(style.HTTP_INFO("🔍 Newsletter Debug Information"))
    print("=" * 60)
    
    # 1. Check email configuration
    print(style.HTTP_INFO("📧 Email Configuration:"))
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print()
    
    # 2. Check subscribers
    print(style.HTTP_INFO("👥 Newsletter Subscribers:"))
    subscribers = NewsletterSubscriber.objects.filter(is_active=True)
    print(f"Total active subscribers: {subscribers.count()}")
    
    if subscribers.count() == 0:
        print(style.ERROR("❌ No active subscribers found!"))
        print(style.WARNING("You need to add subscribers first."))
        return False
    
    for i, sub in enumerate(subscribers[:5], 1):  # Show first 5
        print(f"{i}. {sub.name} - {sub.email}")
    
    if subscribers.count() > 5:
        print(f"... and {subscribers.count() - 5} more")
    print()
    
    # 3. Test single email send
    print(style.HTTP_INFO("🧪 Testing Single Email Send:"))
    test_subscriber = subscribers.first()
    print(f"Sending test email to: {test_subscriber.email}")
    
    result = send_email(
        recipient=test_subscriber.email,
        subject="Test Newsletter Email",
        message=f"Hi {test_subscriber.name},\n\nThis is a test email from your newsletter system.\n\nBest regards,\nKennedy"
    )
    
    if result:
        print(style.SUCCESS("✅ Single email test successful!"))
    else:
        print(style.ERROR("❌ Single email test failed!"))
        return False
    
    # 4. Test newsletter sending function
    print(style.HTTP_INFO("📰 Testing Newsletter Send Function:"))
    try:
        success_count, total_count, campaign = send_newsletter_to_all()
        print(f"Success count: {success_count}")
        print(f"Total count: {total_count}")
        
        if success_count > 0:
            print(style.SUCCESS(f"✅ Newsletter sent to {success_count}/{total_count} subscribers!"))
            return True
        else:
            print(style.ERROR("❌ Newsletter sending failed!"))
            return False
            
    except Exception as e:
        print(style.ERROR(f"❌ Error in newsletter function: {e}"))
        return False

def create_test_subscriber():
    """Create a test subscriber if none exist"""
    print(style.HTTP_INFO("➕ Creating Test Subscriber:"))
    
    test_email = "kennedyakogokweku@gmail.com"  # Your email for testing
    
    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=test_email,
        defaults={
            'name': 'Kennedy Test',
            'is_active': True
        }
    )
    
    if created:
        print(style.SUCCESS(f"✅ Created test subscriber: {subscriber.name} - {subscriber.email}"))
    else:
        print(style.WARNING(f"⚠️ Test subscriber already exists: {subscriber.name} - {subscriber.email}"))
    
    return subscriber

if __name__ == "__main__":
    print(style.HTTP_INFO("🚀 Newsletter Debug Tool"))
    print("=" * 60)
    
    # Check if we have subscribers, if not create a test one
    if NewsletterSubscriber.objects.filter(is_active=True).count() == 0:
        print(style.WARNING("No subscribers found. Creating test subscriber..."))
        create_test_subscriber()
        print()
    
    # Run debug
    success = debug_newsletter()
    
    if success:
        print(style.SUCCESS("\n🎉 Newsletter system is working!"))
    else:
        print(style.ERROR("\n💥 Newsletter system has issues!"))
        print(style.WARNING("Check the error messages above for details."))
