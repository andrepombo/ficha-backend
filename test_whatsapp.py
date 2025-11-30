#!/usr/bin/env python
"""
Test script for WhatsApp integration.
Run this script to test if your Twilio WhatsApp configuration is working.

Usage:
    python test_whatsapp.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.whatsapp_service import whatsapp_service
from apps.candidate.models import Interview, Candidate
from datetime import datetime, timedelta


def test_configuration():
    """Test if WhatsApp service is properly configured."""
    print("=" * 60)
    print("WhatsApp Integration Test")
    print("=" * 60)
    print()
    
    print("1. Checking Configuration...")
    if whatsapp_service.is_configured():
        print("   ✅ WhatsApp service is configured!")
        print(f"   - Account SID: {whatsapp_service.account_sid[:10]}...")
        print(f"   - WhatsApp From: {whatsapp_service.whatsapp_from}")
    else:
        print("   ❌ WhatsApp service is NOT configured!")
        print()
        print("   Please set the following environment variables in your .env file:")
        print("   - TWILIO_ACCOUNT_SID")
        print("   - TWILIO_AUTH_TOKEN")
        print("   - TWILIO_WHATSAPP_FROM")
        print()
        print("   See WHATSAPP_QUICK_START.md for setup instructions.")
        return False
    
    print()
    return True


def test_phone_formatting():
    """Test phone number formatting."""
    print("2. Testing Phone Number Formatting...")
    
    test_numbers = [
        "11 98765-4321",
        "21 91234-5678",
        "85 99999-8888",
    ]
    
    for number in test_numbers:
        formatted = whatsapp_service.format_phone_number(number)
        print(f"   {number} → {formatted}")
    
    print("   ✅ Phone formatting working!")
    print()


def test_with_real_interview():
    """Test with a real interview from the database."""
    print("3. Testing with Database Interview...")
    
    # Try to get the most recent scheduled interview
    interview = Interview.objects.filter(status='scheduled').first()
    
    if not interview:
        print("   ⚠️  No scheduled interviews found in database.")
        print("   Create an interview through the admin or API to test.")
        print()
        return
    
    print(f"   Found interview: {interview.title}")
    print(f"   Candidate: {interview.candidate.full_name}")
    print(f"   Phone: {interview.candidate.phone_number}")
    print(f"   Date: {interview.scheduled_date} at {interview.scheduled_time}")
    print()
    
    # Ask for confirmation
    response = input("   Send test WhatsApp message to this candidate? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print()
        print("   Sending WhatsApp message...")
        result = whatsapp_service.send_interview_scheduled_message(interview)
        
        if result['success']:
            print(f"   ✅ Message sent successfully!")
            print(f"   Message SID: {result['message_sid']}")
            print(f"   Status: {result['status']}")
        else:
            print(f"   ❌ Failed to send message!")
            print(f"   Error: {result['error']}")
    else:
        print("   Skipped sending test message.")
    
    print()


def test_message_templates():
    """Display message template examples."""
    print("4. Message Template Examples...")
    print()
    print("   The following message types are available:")
    print("   - Interview Scheduled (sent when interview is created)")
    print("   - Interview Cancelled (sent when status changes to cancelled)")
    print("   - Interview Rescheduled (sent when interview is rescheduled)")
    print("   - Interview Reminder (available for scheduled tasks)")
    print()
    print("   Messages are formatted in Portuguese with emojis for better engagement.")
    print()


def main():
    """Main test function."""
    try:
        # Test configuration
        if not test_configuration():
            return
        
        # Test phone formatting
        test_phone_formatting()
        
        # Display message templates
        test_message_templates()
        
        # Test with real interview (optional)
        test_with_real_interview()
        
        print("=" * 60)
        print("Test Complete!")
        print("=" * 60)
        print()
        print("Next Steps:")
        print("1. If not configured, add Twilio credentials to .env")
        print("2. Create an interview through the application")
        print("3. Check that WhatsApp message is sent automatically")
        print("4. Monitor Django logs for any errors")
        print()
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
