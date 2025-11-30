#!/usr/bin/env python
"""
Add a phone number to your WABA test numbers list.
This allows sending messages without the conversation handshake requirement.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('META_PERMANENT_ACCESS_TOKEN')
api_version = os.getenv('META_API_VERSION', 'v20.0')

print("=" * 70)
print("Add Test Phone Number to WABA")
print("=" * 70)
print()

# You need your WABA ID - let's try to find it
waba_id = input("Enter your WABA ID (from Meta Business Manager): ").strip()

if not waba_id:
    print("❌ WABA ID required")
    print()
    print("To find your WABA ID:")
    print("1. Go to business.facebook.com")
    print("2. WhatsApp Manager → Settings")
    print("3. Look for 'WhatsApp Business Account ID'")
    exit(1)

# Phone number to add as test number
test_phone = input("Enter phone to add as test number (e.g., 85 8880-6269): ").strip()
cleaned = test_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
if not cleaned.startswith('+'):
    if cleaned.startswith('55'):
        cleaned = f"+{cleaned}"
    else:
        cleaned = f"+55{cleaned}"

print()
print(f"Adding {cleaned} as test number to WABA {waba_id}...")
print()

url = f"https://graph.facebook.com/{api_version}/{waba_id}/phone_numbers"
headers = {'Authorization': f'Bearer {token}'}
params = {
    'phone_number': cleaned,
    'verified_name': 'Test Number',
    'certificate': 'test'
}

resp = requests.post(url, headers=headers, params=params)

if resp.status_code in [200, 201]:
    print("✅ Test number added successfully!")
    print()
    print("Now you can send messages to this number without conversation handshake")
    print("Try running: python test_andre.py")
else:
    error = resp.json().get('error', {})
    print(f"❌ Failed: {error.get('message')}")
    print()
    print("This feature might not be available for your account type.")
    print()
    print("ALTERNATIVE SOLUTION:")
    print("Since you can't use WhatsApp Business app with this number,")
    print("you need to:")
    print()
    print("1. Have someone with a DIFFERENT phone number message +55 85 9613-4133")
    print("2. Then you can send notifications to that number")
    print()
    print("OR")
    print()
    print("Accept that WhatsApp will only work for candidates who message you first")
    print("This is Meta's requirement and cannot be bypassed")

print()
print("=" * 70)
