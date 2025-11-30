#!/usr/bin/env python
"""
Try to initiate a conversation by sending a simple text message (session message).
This might work if you're within 24h of receiving the 'Hi' message.
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

phone_id = os.getenv('META_PHONE_NUMBER_ID')
token = os.getenv('META_PERMANENT_ACCESS_TOKEN')
api_version = os.getenv('META_API_VERSION', 'v20.0')

print("=" * 70)
print("Initiate WhatsApp Conversation")
print("=" * 70)
print()

# Try sending a simple text message (not template)
# This only works if within 24h customer service window
your_number = "85 8880-6269"
cleaned = your_number.replace(' ', '').replace('-', '')
e164 = f"+55{cleaned}"

print(f"Attempting to send session message to: {e164}")
print()

url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Try simple text message first (session window)
payload = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": e164,
    "type": "text",
    "text": {
        "preview_url": False,
        "body": "Olá! Esta é uma mensagem de teste do sistema de notificações da Pinte Pinturas."
    }
}

print("Trying session message (freeform text)...")
resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)

if resp.status_code >= 400:
    error_data = resp.json()
    error = error_data.get('error', {})
    print(f"❌ Session message failed: {error.get('code')} - {error.get('message')}")
    print()
    
    # If session message fails, the 24h window isn't active
    # This confirms you need to wait or try a different approach
    if error.get('code') == 131047:
        print("💡 Error 131047: Message undeliverable")
        print("   This means the 24h session window is not active")
        print()
    elif error.get('code') == 133010:
        print("💡 Error 133010: Account not registered")
        print("   The 'Hi' message you sent hasn't opened a session window")
        print()
    
    print("SOLUTION:")
    print("Since your business is verified, the issue is the conversation handshake.")
    print()
    print("Try this:")
    print("1. Install WhatsApp Business app on your phone")
    print("2. Register it with +55 85 9613-4133")
    print("3. Send a message to your personal number from the app")
    print("4. Or wait - sometimes Meta takes 15-30 min to sync incoming messages")
    print()
    print("Alternative: Use a phone number that has DEFINITELY messaged")
    print("your business number recently (within last 24h)")
else:
    data = resp.json()
    print("✅ SUCCESS! Session message sent!")
    print(f"   Message ID: {data.get('messages', [{}])[0].get('id')}")
    print()
    print("   Now try sending the template message - it should work!")
    print("   Run: python test_andre.py")

print()
print("=" * 70)
