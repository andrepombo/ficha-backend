#!/usr/bin/env python
"""
Test with Andre's exact number from WhatsApp profile.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.whatsapp_service import whatsapp_service

# Your exact number from WhatsApp profile
phone = "85 8880-6269"

print("=" * 70)
print("Testing with Andre's WhatsApp number")
print("=" * 70)
print()

print(f"Phone: {phone}")
formatted = whatsapp_service.format_phone_number(phone)
print(f"E.164: {formatted}")
print()

template_vars = [
    "André",          # {{1}} name
    "28/10/2025",     # {{2}} date
    "14:30"           # {{3}} time
]

print("Sending template message...")
try:
    result = whatsapp_service._meta_send_template(
        formatted,
        '_interview_rescheduled',
        template_vars
    )
    
    if result['success']:
        print()
        print("✅ SUCCESS! Message sent!")
        print(f"   Message ID: {result['message_sid']}")
        print(f"   Status: {result['status']}")
        print()
        print("📱 Check your WhatsApp now!")
    else:
        print(f"❌ Failed: {result.get('error')}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
