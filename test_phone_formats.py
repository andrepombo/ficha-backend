#!/usr/bin/env python
"""
Test sending WhatsApp message with different phone number formats.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.whatsapp_service import whatsapp_service
import requests

def test_template_send(phone_number, template_name="interview_rescheduled"):
    """Test sending a template message to a specific phone number."""
    
    print(f"\n{'='*70}")
    print(f"Testing phone: {phone_number}")
    print(f"{'='*70}")
    
    # Format the phone number
    formatted = whatsapp_service.format_phone_number(phone_number)
    print(f"Formatted: {formatted}")
    
    # Prepare template variables for rescheduled message
    template_vars = [
        "André",  # {{1}} = name
        "29/10/2025",  # {{2}} = new date
        "14:30"  # {{3}} = new time
    ]
    
    # Build the API request
    url = f"{whatsapp_service.meta_base_url}/{whatsapp_service.meta_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {whatsapp_service.meta_access_token}",
        "Content-Type": "application/json"
    }
    
    body_parameters = [
        {"type": "text", "text": str(v)} for v in template_vars
    ]
    
    payload = {
        "messaging_product": "whatsapp",
        "to": formatted,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "pt_BR"},
            "components": [
                {"type": "body", "parameters": body_parameters}
            ]
        }
    }
    
    print(f"Sending to: {formatted}")
    print(f"Template: {template_name}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id')
            print(f"✅ SUCCESS! Message ID: {message_id}")
            return True
        else:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            error_code = error_data.get('error', {}).get('code', 'N/A')
            print(f"❌ FAILED: ({error_code}) {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Test different phone number formats."""
    
    print("\n" + "="*70)
    print("WhatsApp Phone Format Testing")
    print("="*70)
    
    # Original number from database
    original = "85 98880-6269"
    
    # Try different formats
    formats_to_test = [
        ("With 9 (11 digits)", "85 98880-6269"),
        ("Without 9 (10 digits)", "85 8880-6269"),
        ("With 9 no spaces", "5585988806269"),
        ("Without 9 no spaces", "5585888806269"),
    ]
    
    print("\nWhich format would you like to test?")
    for i, (desc, phone) in enumerate(formats_to_test, 1):
        print(f"{i}. {desc}: {phone}")
    print("5. Enter custom number")
    print("6. Test all formats")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "5":
        custom = input("Enter phone number: ").strip()
        test_template_send(custom)
    elif choice == "6":
        for desc, phone in formats_to_test:
            test_template_send(phone)
            input("\nPress Enter to try next format...")
    elif choice in ["1", "2", "3", "4"]:
        idx = int(choice) - 1
        desc, phone = formats_to_test[idx]
        test_template_send(phone)
    else:
        print("Invalid choice")
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
