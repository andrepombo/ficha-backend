#!/usr/bin/env python
"""
Test script to verify interview update triggers WhatsApp notification.
This simulates updating an interview's date/time.

Usage:
    python test_update_interview.py
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import Interview
from apps.candidate.whatsapp_service import whatsapp_service


def test_interview_update():
    """Test updating an interview and sending WhatsApp notification."""
    
    print("=" * 60)
    print("Interview Update WhatsApp Test")
    print("=" * 60)
    print()
    
    # Get a scheduled interview
    interview = Interview.objects.filter(status='scheduled').first()
    
    if not interview:
        print("❌ No scheduled interviews found in database.")
        print("   Create an interview first to test.")
        return
    
    print(f"Found interview: {interview.title}")
    print(f"Candidate: {interview.candidate.full_name}")
    print(f"Current date: {interview.scheduled_date}")
    print(f"Current time: {interview.scheduled_time}")
    print()
    
    # Store old values
    old_date = interview.scheduled_date
    old_time = interview.scheduled_time
    
    # Ask user if they want to test
    response = input("Update this interview and send WhatsApp notification? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("Test cancelled.")
        return
    
    # Update the date to tomorrow
    new_date = datetime.now().date() + timedelta(days=1)
    new_time = datetime.now().time()
    
    print()
    print(f"Updating interview...")
    print(f"New date: {new_date}")
    print(f"New time: {new_time}")
    print()
    
    # Update the interview
    interview.scheduled_date = new_date
    interview.scheduled_time = new_time
    interview.save()
    
    print("✅ Interview updated in database")
    print()
    
    # Send WhatsApp notification
    print("Sending WhatsApp rescheduling notification...")
    result = whatsapp_service.send_interview_rescheduled_message(
        interview,
        old_date=old_date,
        old_time=old_time
    )
    
    if result['success']:
        print(f"✅ WhatsApp message sent successfully!")
        print(f"   Message SID: {result['message_sid']}")
        print(f"   Phone format used: {result.get('phone_format_used')}")
        print()
        print("Check the candidate's WhatsApp for the rescheduling message!")
    else:
        print(f"❌ Failed to send WhatsApp message")
        print(f"   Error: {result.get('error')}")
        print()
        print("Check the error above and verify:")
        print("1. Candidate's phone number has joined the Twilio sandbox")
        print("2. Phone number format is correct")
        print("3. Twilio credentials are configured")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_interview_update()
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
