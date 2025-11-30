#!/usr/bin/env python
"""
Test script for Meta WhatsApp Cloud API integration.
Tests configuration and sends a test template message.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.whatsapp_service import whatsapp_service
from apps.candidate.models import Candidate, Interview
from datetime import datetime, timedelta


def test_configuration():
    """Test if Meta WhatsApp is properly configured."""
    print("=" * 70)
    print("Meta WhatsApp Configuration Test")
    print("=" * 70)
    print()
    
    print("1. Configuration Check:")
    print("-" * 70)
    print(f"   Provider: {whatsapp_service.provider}")
    print(f"   API Version: {whatsapp_service.meta_api_version}")
    print(f"   Base URL: {whatsapp_service.meta_base_url}")
    
    if whatsapp_service.meta_phone_number_id:
        print(f"   Phone Number ID: {whatsapp_service.meta_phone_number_id[:10]}...")
    else:
        print("   ❌ Phone Number ID: NOT SET")
    
    if whatsapp_service.meta_access_token:
        print(f"   Access Token: {whatsapp_service.meta_access_token[:20]}...")
    else:
        print("   ❌ Access Token: NOT SET")
    
    print(f"   Template Language: {whatsapp_service.tpl_language}")
    print(f"   Template Scheduled: {whatsapp_service.tpl_scheduled or 'NOT SET'}")
    print(f"   Template Rescheduled: {whatsapp_service.tpl_rescheduled or 'NOT SET'}")
    print(f"   Template Cancelled: {whatsapp_service.tpl_cancelled or 'NOT SET'}")
    print()
    
    if whatsapp_service.is_configured():
        print("   ✅ Meta WhatsApp service is configured")
    else:
        print("   ❌ Meta WhatsApp service is NOT configured")
        print("   - Set META_PHONE_NUMBER_ID and META_PERMANENT_ACCESS_TOKEN in .env")
        return False
    print()
    
    return True


def test_send_message():
    """Send a test template message."""
    print("2. Test Template Message:")
    print("-" * 70)
    
    # Get a candidate with a phone number
    candidate = Candidate.objects.filter(phone_number__isnull=False).exclude(phone_number='').first()
    
    if not candidate:
        print("   ❌ No candidates with phone numbers found")
        print("   Create a candidate first or provide a test phone number")
        return
    
    print(f"   Test candidate: {candidate.full_name}")
    print(f"   Phone: {candidate.phone_number}")
    
    # Format phone for display
    formatted = whatsapp_service.format_phone_number(candidate.phone_number)
    print(f"   Formatted (E.164): {formatted}")
    print()
    
    # Ask for confirmation
    response = input("   Send test rescheduled message to this number? (y/n): ")
    if response.lower() != 'y':
        print("   Test cancelled")
        return
    
    print()
    print("   Sending test message...")
    
    try:
        # Create a test interview or use existing
        tomorrow = datetime.now().date() + timedelta(days=1)
        interview, created = Interview.objects.get_or_create(
            candidate=candidate,
            status='scheduled',
            defaults={
                'title': 'Entrevista Técnica - TESTE',
                'scheduled_date': tomorrow,
                'scheduled_time': datetime.now().time().replace(hour=14, minute=30),
                'interview_type': 'video',
                'duration_minutes': 60,
                'location': 'https://meet.google.com/test-link'
            }
        )
        
        if not created:
            interview.scheduled_date = tomorrow
            interview.scheduled_time = datetime.now().time().replace(hour=14, minute=30)
            interview.save()
        
        # Send rescheduled message
        old_date = datetime.now().date()
        old_time = datetime.now().time().replace(hour=10, minute=0)
        
        result = whatsapp_service.send_interview_rescheduled_message(
            interview,
            old_date=old_date,
            old_time=old_time
        )
        
        print()
        if result['success']:
            print("   ✅ Message sent successfully!")
            print(f"   Message ID: {result.get('message_sid')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Phone used: {result.get('verified_phone')}")
            print()
            print("   Check your WhatsApp to verify delivery!")
        else:
            print("   ❌ Failed to send message")
            print(f"   Error: {result.get('error')}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    if not test_configuration():
        return
    
    print()
    test_send_message()
    
    print()
    print("=" * 70)
    print("Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
