#!/usr/bin/env python
"""
Enable WhatsApp opt-in for a candidate.
Use this to manually opt-in candidates for testing or if they consent via phone/email.
"""

import os
import sys
import django
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import Candidate
from django.utils import timezone

def enable_optin():
    print("=" * 70)
    print("Enable WhatsApp Opt-in for Candidate")
    print("=" * 70)
    print()
    
    # Show candidates
    candidates = Candidate.objects.all().order_by('-applied_date')[:10]
    
    if not candidates:
        print("❌ No candidates found")
        return
    
    print("Recent candidates:")
    for i, c in enumerate(candidates, 1):
        opt_in_status = "✅ Opted-in" if c.whatsapp_opt_in else "❌ Not opted-in"
        print(f"{i}. {c.full_name} - {c.phone_number} - {opt_in_status}")
    
    print()
    choice = input("Enter candidate number (or 'q' to quit): ").strip()
    
    if choice.lower() == 'q':
        return
    
    try:
        idx = int(choice) - 1
        candidate = candidates[idx]
    except (ValueError, IndexError):
        print("❌ Invalid choice")
        return
    
    print()
    print(f"Selected: {candidate.full_name}")
    print(f"Phone: {candidate.phone_number}")
    print(f"Current opt-in status: {'Yes' if candidate.whatsapp_opt_in else 'No'}")
    print()
    
    if candidate.whatsapp_opt_in:
        action = input("Already opted-in. Remove opt-in? (y/n): ").strip().lower()
        if action == 'y':
            candidate.whatsapp_opt_in = False
            candidate.whatsapp_opt_in_date = None
            candidate.save()
            print("✅ Opt-in removed")
    else:
        action = input("Enable WhatsApp opt-in? (y/n): ").strip().lower()
        if action == 'y':
            candidate.whatsapp_opt_in = True
            candidate.whatsapp_opt_in_date = timezone.now()
            candidate.save()
            print("✅ WhatsApp opt-in enabled!")
            print(f"   Opt-in date: {candidate.whatsapp_opt_in_date}")

if __name__ == "__main__":
    try:
        enable_optin()
    except KeyboardInterrupt:
        print("\n\nCancelled")
