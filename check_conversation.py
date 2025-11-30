#!/usr/bin/env python
"""
Check if there's an active conversation with a phone number in Meta.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

phone_id = os.getenv('META_PHONE_NUMBER_ID')
token = os.getenv('META_PERMANENT_ACCESS_TOKEN')
api_version = os.getenv('META_API_VERSION', 'v20.0')

print("=" * 70)
print("Check Meta WhatsApp Conversations")
print("=" * 70)
print()

if not phone_id or not token:
    print("❌ Missing credentials")
    exit(1)

# Try to get recent messages/conversations
# Note: This endpoint might not be available depending on permissions
url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
headers = {'Authorization': f'Bearer {token}'}

print("Attempting to check recent activity...")
print()

# Try sending a test message to see the exact error
test_phone = input("Enter phone number to test (e.g., 85 8880-6269): ").strip()

# Format to E.164
cleaned = test_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
if cleaned.startswith('+55'):
    cleaned = cleaned[3:]
elif cleaned.startswith('55'):
    cleaned = cleaned[2:]

e164 = f"+55{cleaned}"

print(f"Testing with: {e164}")
print()

# Try sending with template
payload = {
    "messaging_product": "whatsapp",
    "to": e164,
    "type": "template",
    "template": {
        "name": "_interview_rescheduled",
        "language": {"code": "pt_BR"},
        "components": [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": "Teste"},
                    {"type": "text", "text": "28/10/2025"},
                    {"type": "text", "text": "14:30"}
                ]
            }
        ]
    }
}

import json
resp = requests.post(url, headers=headers, json=payload, timeout=20)

print(f"Response Status: {resp.status_code}")
print()

if resp.status_code >= 400:
    data = resp.json()
    error = data.get('error', {})
    print(f"❌ Error Code: {error.get('code')}")
    print(f"   Error Type: {error.get('type')}")
    print(f"   Message: {error.get('message')}")
    print(f"   Trace ID: {error.get('fbtrace_id')}")
    print()
    
    if error.get('code') == 133010:
        print("💡 Error #133010 means:")
        print("   1. This number hasn't messaged your business yet")
        print("   2. OR the message was sent but Meta hasn't synced it yet (wait 5 min)")
        print("   3. OR there's a phone format mismatch")
        print()
        print("   Try these formats:")
        print(f"   - With 9: +5585988806269")
        print(f"   - Without 9: +558588806269")
else:
    data = resp.json()
    print("✅ Success!")
    print(f"   Message ID: {data.get('messages', [{}])[0].get('id')}")
    print()
    print("   Check your WhatsApp now!")

print()
print("=" * 70)
