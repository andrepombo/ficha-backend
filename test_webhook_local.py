#!/usr/bin/env python
"""
Test webhook endpoint locally before configuring in Meta.
"""

import requests
import json

print("=" * 70)
print("Test Webhook Endpoint Locally")
print("=" * 70)
print()

# Your local webhook URL
webhook_url = "http://localhost:8000/webhooks/whatsapp/"

print(f"Testing: {webhook_url}")
print()

# Test 1: Verification (GET request)
print("1. Testing webhook verification (GET)...")
verify_token = input("   Enter your META_WEBHOOK_VERIFY_TOKEN from .env: ").strip()

params = {
    'hub.mode': 'subscribe',
    'hub.verify_token': verify_token,
    'hub.challenge': 'test_challenge_12345'
}

try:
    resp = requests.get(webhook_url, params=params, timeout=5)
    if resp.status_code == 200 and resp.text == 'test_challenge_12345':
        print("   ✅ Verification works!")
    else:
        print(f"   ❌ Verification failed: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   Make sure Django server is running: python manage.py runserver")

print()

# Test 2: Incoming message (POST request)
print("2. Testing incoming message webhook (POST)...")

test_payload = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "123456",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "5585961341133",
                    "phone_number_id": "771225619417898"
                },
                "messages": [{
                    "from": "558588806269",
                    "id": "wamid.test123",
                    "timestamp": "1234567890",
                    "type": "text",
                    "text": {
                        "body": "Test message from webhook test script"
                    }
                }]
            },
            "field": "messages"
        }]
    }]
}

try:
    resp = requests.post(webhook_url, json=test_payload, timeout=5)
    if resp.status_code == 200:
        print("   ✅ Message webhook works!")
        print("   Check Django logs for: 'Received message from 558588806269'")
    else:
        print(f"   ❌ Failed: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 70)
print()
print("If both tests passed:")
print("✅ Your webhook is working locally")
print()
print("Next steps:")
print("1. If testing locally, start ngrok: ngrok http 8000")
print("2. Copy the ngrok HTTPS URL (e.g., https://abc123.ngrok.io)")
print("3. Go to developers.facebook.com/apps")
print("4. Configure webhook with: https://abc123.ngrok.io/webhooks/whatsapp/")
print()
print("If deploying to production:")
print("1. Deploy your Django app to a server with HTTPS")
print("2. Configure webhook with: https://your-domain.com/webhooks/whatsapp/")
print()
print("=" * 70)
