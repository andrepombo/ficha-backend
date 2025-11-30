#!/usr/bin/env python
"""
Update candidate phone to 8-digit format and test.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import Candidate

# Find the candidate
candidate = Candidate.objects.filter(phone_number='85 98880-6269').first()

if candidate:
    print(f"Found: {candidate.full_name}")
    print(f"Current phone: {candidate.phone_number}")
    print(f"Current WhatsApp phone: {candidate.whatsapp_phone}")
    print()
    
    # Update to 8-digit format
    candidate.phone_number = '85 8880-6269'
    candidate.whatsapp_phone = '85 8880-6269'
    candidate.save()
    
    print("✅ Updated to 8-digit format:")
    print(f"   New phone: {candidate.phone_number}")
    print(f"   New WhatsApp phone: {candidate.whatsapp_phone}")
else:
    print("❌ Candidate not found")
