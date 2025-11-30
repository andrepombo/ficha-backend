#!/usr/bin/env python
"""
Test with your own phone number.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.whatsapp_service import whatsapp_service

# YOUR phone number - the one you used to send "Teste 1"
# Try both 8-digit and 9-digit formats
test_numbers = [
    "85 98880-6269",  # 9-digit
    "85 8880-6269",   # 8-digit
]

print("=" * 70)
print("Testing with your phone number")
print("=" * 70)
print()

for phone in test_numbers:
    print(f"Testing: {phone}")
    formatted = whatsapp_service.format_phone_number(phone)
    print(f"E.164: {formatted}")
    
    template_vars = [
        "Teste Usuario",  # {{1}} name
        "28/10/2025",     # {{2}} date
        "14:30"           # {{3}} time
    ]
    
    try:
        result = whatsapp_service._meta_send_template(
            formatted,
            '_interview_rescheduled',
            template_vars
        )
        
        if result['success']:
            print(f"✅ SUCCESS! Message ID: {result['message_sid']}")
            print(f"   Check your WhatsApp!")
            break
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

print("=" * 70)
