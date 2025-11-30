#!/usr/bin/env python
"""
Direct Meta WhatsApp template test - specify phone number manually.
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.whatsapp_service import whatsapp_service

def test_direct():
    print("=" * 70)
    print("Direct Meta WhatsApp Template Test")
    print("=" * 70)
    print()
    
    if not whatsapp_service.is_configured():
        print("❌ Meta WhatsApp not configured")
        return
    
    print("✅ Meta configured")
    print(f"   Phone Number ID: {whatsapp_service.meta_phone_number_id[:10]}...")
    print()
    
    # Get phone number from user
    phone = input("Enter phone number (format: 85 98880-6269): ").strip()
    if not phone:
        print("❌ No phone number provided")
        return
    
    print(f"\n📱 Sending to: {phone}")
    formatted = whatsapp_service.format_phone_number(phone)
    print(f"   E.164 format: {formatted}")
    print()
    
    # Test variables for rescheduled template (only 3 variables)
    template_vars = [
        "João Silva",  # {{1}} name
        "28/10/2025",  # {{2}} new date
        "14:30"  # {{3}} new time
    ]
    
    try:
        result = whatsapp_service._meta_send_template(
            formatted,
            '_interview_rescheduled',
            template_vars
        )
        
        if result['success']:
            print("✅ Message sent successfully!")
            print(f"   Message ID: {result['message_sid']}")
            print(f"   Status: {result['status']}")
            print("\n📱 Check WhatsApp to verify delivery!")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_direct()
