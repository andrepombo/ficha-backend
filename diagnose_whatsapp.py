#!/usr/bin/env python
"""
Diagnostic script to check WhatsApp integration status.
Checks configuration, phone numbers, and recent interview updates.

Usage:
    python diagnose_whatsapp.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import Interview, Candidate
from apps.candidate.whatsapp_service import whatsapp_service


def diagnose():
    """Run diagnostic checks."""
    
    print("=" * 70)
    print("WhatsApp Integration Diagnostic")
    print("=" * 70)
    print()
    
    # 1. Check configuration
    print("1. Configuration Check:")
    print("-" * 70)
    if whatsapp_service.is_configured():
        print("   ✅ WhatsApp service is configured")
        print(f"   - Account SID: {whatsapp_service.account_sid[:10]}...")
        print(f"   - WhatsApp From: {whatsapp_service.whatsapp_from}")
    else:
        print("   ❌ WhatsApp service is NOT configured")
        print("   - Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM in .env")
    print()
    
    # 2. Check recent interviews
    print("2. Recent Scheduled Interviews:")
    print("-" * 70)
    recent_interviews = Interview.objects.filter(status='scheduled').order_by('-updated_at')[:5]
    
    if not recent_interviews:
        print("   ⚠️  No scheduled interviews found")
    else:
        for interview in recent_interviews:
            print(f"   Interview ID: {interview.id}")
            print(f"   - Title: {interview.title}")
            print(f"   - Candidate: {interview.candidate.full_name}")
            print(f"   - Phone: {interview.candidate.phone_number}")
            print(f"   - Date: {interview.scheduled_date} at {interview.scheduled_time}")
            print(f"   - WhatsApp sent: {interview.whatsapp_sent}")
            if interview.whatsapp_sent:
                print(f"   - Message SID: {interview.whatsapp_message_sid}")
                print(f"   - Sent at: {interview.whatsapp_sent_at}")
            print(f"   - Last updated: {interview.updated_at}")
            print()
    
    # 3. Check phone number formats
    print("3. Phone Number Format Check:")
    print("-" * 70)
    candidates_with_phones = Candidate.objects.exclude(phone_number='').exclude(phone_number__isnull=True)[:5]
    
    if not candidates_with_phones:
        print("   ⚠️  No candidates with phone numbers found")
    else:
        for candidate in candidates_with_phones:
            phone = candidate.phone_number
            formatted = whatsapp_service.format_phone_number(phone)
            print(f"   {candidate.full_name}")
            print(f"   - Database: {phone}")
            print(f"   - Formatted: {formatted}")
            print()
    
    # 4. Check sandbox participants (if possible)
    print("4. Recommendations:")
    print("-" * 70)
    print("   To ensure WhatsApp messages are delivered:")
    print("   1. Make sure candidate phone numbers have joined the Twilio sandbox")
    print("   2. Check Django logs when updating interviews for any errors")
    print("   3. Test with: python test_update_interview.py")
    print("   4. Monitor Twilio Console for message delivery status")
    print()
    
    print("5. How to Test:")
    print("-" * 70)
    print("   Option 1: Update via API")
    print("   - Update an interview date/time through your frontend")
    print("   - Check Django console logs for WhatsApp sending confirmation")
    print()
    print("   Option 2: Direct test")
    print("   - Run: python test_update_interview.py")
    print("   - This will update an interview and send WhatsApp directly")
    print()
    
    print("6. Common Issues:")
    print("-" * 70)
    print("   ❌ No message received:")
    print("      - Phone number not in sandbox (Error 63015)")
    print("      - Wrong phone format (try alternative with/without leading 9)")
    print("      - Django server not reloaded after code changes")
    print()
    print("   ❌ perform_update not called:")
    print("      - Make sure you're using PUT/PATCH request to update")
    print("      - Check if frontend is calling the correct API endpoint")
    print("      - Verify Django logs show the update request")
    print()
    
    print("=" * 70)
    print("Diagnostic Complete")
    print("=" * 70)


if __name__ == "__main__":
    try:
        diagnose()
    except Exception as e:
        print(f"❌ Error during diagnostic: {e}")
        import traceback
        traceback.print_exc()
