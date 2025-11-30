#!/usr/bin/env python
"""
Check if webhooks are configured to receive incoming messages.
If webhooks aren't set up, Meta receives your messages but your system doesn't know about them.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

phone_id = os.getenv('META_PHONE_NUMBER_ID')
token = os.getenv('META_PERMANENT_ACCESS_TOKEN')
api_version = os.getenv('META_API_VERSION', 'v20.0')

print("=" * 70)
print("Check Webhook Configuration")
print("=" * 70)
print()

print("IMPORTANT: Even though you sent 'Hi', Meta might not have")
print("registered it if webhooks aren't configured.")
print()

# Get app ID from token
debug_url = f"https://graph.facebook.com/{api_version}/debug_token"
params = {'input_token': token, 'access_token': token}
resp = requests.get(debug_url, params=params)

if resp.status_code == 200:
    app_id = resp.json().get('data', {}).get('app_id')
    print(f"App ID: {app_id}")
    print()
    
    # Check webhook subscriptions
    webhook_url = f"https://graph.facebook.com/{api_version}/{app_id}/subscriptions"
    headers = {'Authorization': f'Bearer {token}'}
    webhook_resp = requests.get(webhook_url, headers=headers)
    
    if webhook_resp.status_code == 200:
        subs = webhook_resp.json().get('data', [])
        if subs:
            print("Webhook Subscriptions:")
            for sub in subs:
                print(f"  Object: {sub.get('object')}")
                print(f"  Callback URL: {sub.get('callback_url')}")
                print(f"  Fields: {sub.get('fields', [])}")
                print()
        else:
            print("❌ NO WEBHOOKS CONFIGURED")
            print()
            print("This is likely the problem!")
            print()
            print("Without webhooks:")
            print("- Meta receives your 'Hi' message")
            print("- But doesn't notify your system")
            print("- So the conversation isn't 'active' from API perspective")
            print()
            print("SOLUTION:")
            print("1. Go to developers.facebook.com/apps")
            print("2. Select your app")
            print("3. WhatsApp → Configuration")
            print("4. Set up webhook URL")
            print("5. Subscribe to 'messages' events")
            print()
            print("OR")
            print()
            print("Try sending FROM Meta Business Suite TO your number")
            print("(This doesn't require webhooks)")
    else:
        print(f"Could not check webhooks: {webhook_resp.status_code}")
else:
    print("Could not get app info")

print()
print("=" * 70)
print()
print("ALTERNATE TEST:")
print("Let's try with the 9-digit format (with leading 9):")
print()
print("Your WhatsApp shows: +55 85 8880-6269 (8-digit)")
print("But Brazilian mobile numbers can be: +55 85 98880-6269 (9-digit)")
print()
print("Meta might be expecting the 9-digit format.")
print()
print("=" * 70)
