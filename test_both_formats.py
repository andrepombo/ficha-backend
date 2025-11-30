#!/usr/bin/env python
"""
Test sending to both 8-digit and 9-digit formats.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.whatsapp_service import whatsapp_service

print("=" * 70)
print("Test Both Phone Formats")
print("=" * 70)
print()

formats = [
    ("8-digit (as shown in WhatsApp)", "85 8880-6269"),
    ("9-digit (with leading 9)", "85 98880-6269"),
]

template_vars = [
    "André",
    "28/10/2025",
    "14:30"
]

for label, phone in formats:
    print(f"Testing {label}: {phone}")
    formatted = whatsapp_service.format_phone_number(phone)
    print(f"  E.164: {formatted}")
    
    try:
        result = whatsapp_service._meta_send_template(
            formatted,
            '_interview_rescheduled',
            template_vars
        )
        
        if result['success']:
            print(f"  ✅ SUCCESS!")
            print(f"  Message ID: {result['message_sid']}")
            print(f"  📱 Check your WhatsApp!")
            print()
            print("=" * 70)
            print("FOUND THE RIGHT FORMAT!")
            print(f"Use: {phone}")
            print("=" * 70)
            break
        else:
            error = result.get('error', '')
            if '133010' in str(error):
                print(f"  ❌ #133010 - Not registered")
            else:
                print(f"  ❌ Error: {error}")
    except Exception as e:
        error_str = str(e)
        if '133010' in error_str:
            print(f"  ❌ #133010 - Not registered")
        else:
            print(f"  ❌ Error: {e}")
    
    print()

print("=" * 70)
print()
print("If BOTH failed with #133010:")
print()
print("The issue is that Meta hasn't registered your 'Hi' message.")
print("This happens when:")
print("1. Webhooks aren't configured (Meta receives but doesn't 'activate')")
print("2. Message was sent too long ago (>24h)")
print("3. Phone number mismatch")
print()
print("FINAL SOLUTION:")
print("Ask a friend/colleague to:")
print("1. Send 'Oi' to +55 85 9613-4133 from their phone")
print("2. Then test with their number")
print()
print("This will prove the integration works once someone messages you.")
print("=" * 70)
