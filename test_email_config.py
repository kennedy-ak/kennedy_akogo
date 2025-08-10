#!/usr/bin/env python
"""
Test script to verify email configuration
Run this to test if your email settings are working
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_site.settings')
django.setup()

from django.core.mail import send_mail
from django.core.management.color import make_style
from portfolio.newsletter_utils import send_email

style = make_style()

def test_email_configuration():
    """Test the email configuration"""
    print(style.HTTP_INFO("📧 Testing Email Configuration"))
    print("=" * 50)
    
    # Check settings
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER or 'NOT SET'}")
    print(f"EMAIL_HOST_PASSWORD: {'SET' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print()
    
    if not settings.EMAIL_HOST_USER:
        print(style.ERROR("❌ EMAIL_HOST_USER is not configured!"))
        print(style.WARNING("Add EMAIL_HOST_USER=your-gmail@gmail.com to your .env file"))
        return False
    
    if not settings.EMAIL_HOST_PASSWORD:
        print(style.ERROR("❌ EMAIL_HOST_PASSWORD is not configured!"))
        print(style.WARNING("Add EMAIL_HOST_PASSWORD=your-app-password to your .env file"))
        print(style.WARNING("Note: Use Gmail App Password, not your regular password"))
        return False
    
    # Test sending email
    test_email = settings.EMAIL_HOST_USER  # Send to yourself
    
    print(style.HTTP_INFO(f"🧪 Testing email send to: {test_email}"))
    
    try:
        # Test using Django's send_mail
        print("Testing with Django's send_mail...")
        send_mail(
            subject='Test Email from Django',
            message='This is a test email to verify your email configuration is working.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[test_email],
            fail_silently=False,
        )
        print(style.SUCCESS("✅ Django send_mail test passed!"))
        
        # Test using our custom send_email function
        print("Testing with custom send_email function...")
        result = send_email(
            recipient=test_email,
            subject='Test Email from Newsletter System',
            message='This is a test email from your newsletter system. If you receive this, your email configuration is working correctly!'
        )
        
        if result:
            print(style.SUCCESS("✅ Custom send_email test passed!"))
            return True
        else:
            print(style.ERROR("❌ Custom send_email test failed!"))
            return False
            
    except Exception as e:
        print(style.ERROR(f"❌ Email test failed: {e}"))
        print(style.WARNING("\n💡 Common issues:"))
        print("1. Gmail App Password not generated or incorrect")
        print("2. 2-Factor Authentication not enabled on Gmail")
        print("3. 'Less secure app access' disabled (use App Password instead)")
        print("4. Firewall blocking SMTP connections")
        return False

def show_gmail_setup_instructions():
    """Show instructions for setting up Gmail"""
    print(style.HTTP_INFO("\n📋 Gmail Setup Instructions:"))
    print("=" * 50)
    print("1. Enable 2-Factor Authentication on your Gmail account")
    print("2. Go to Google Account settings > Security > App passwords")
    print("3. Generate an App Password for 'Mail'")
    print("4. Use this App Password (not your regular password) in EMAIL_HOST_PASSWORD")
    print("5. Add these to your .env file:")
    print("   EMAIL_HOST_USER=your-email@gmail.com")
    print("   EMAIL_HOST_PASSWORD=your-16-character-app-password")

if __name__ == "__main__":
    success = test_email_configuration()
    
    if success:
        print(style.SUCCESS("\n🎉 Email configuration is working!"))
        print(style.HTTP_INFO("You can now send newsletters successfully."))
    else:
        print(style.ERROR("\n💥 Email configuration failed!"))
        show_gmail_setup_instructions()
