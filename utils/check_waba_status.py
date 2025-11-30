#!/usr/bin/env python
"""
Check WABA (WhatsApp Business Account) status and configuration.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

phone_id = os.getenv('META_PHONE_NUMBER_ID')
token = os.getenv('META_PERMANENT_ACCESS_TOKEN')
api_version = os.getenv('META_API_VERSION', 'v20.0')

print("=" * 70)
print("WhatsApp Business Account Status Check")
print("=" * 70)
print()

if not phone_id or not token:
    print("❌ Missing credentials")
    exit(1)

# Get phone number details
url = f"https://graph.facebook.com/{api_version}/{phone_id}"
headers = {'Authorization': f'Bearer {token}'}
params = {'fields': 'verified_name,display_phone_number,quality_rating,messaging_limit_tier,account_mode'}

print("1. Phone Number Status:")
print("-" * 70)
resp = requests.get(url, headers=headers, params=params)

if resp.status_code == 200:
    data = resp.json()
    print(f"   Display Number: {data.get('display_phone_number')}")
    print(f"   Verified Name: {data.get('verified_name')}")
    print(f"   Quality Rating: {data.get('quality_rating', 'UNKNOWN')}")
    print(f"   Messaging Tier: {data.get('messaging_limit_tier', 'UNKNOWN')}")
    print(f"   Account Mode: {data.get('account_mode', 'UNKNOWN')}")
    
    # Check if in sandbox/test mode
    if data.get('account_mode') == 'SANDBOX':
        print()
        print("   ⚠️  WARNING: Account is in SANDBOX mode")
        print("   This means you can only message numbers that have joined the sandbox")
        print("   You need to move to LIVE mode for production use")
else:
    print(f"   ❌ Error: {resp.status_code} - {resp.text}")

print()
print("2. Recommendations:")
print("-" * 70)
print("   If account is in SANDBOX:")
print("   - Go to Meta Business Manager → WhatsApp Manager")
print("   - Complete business verification")
print("   - Request to move to LIVE mode")
print()
print("   If account is LIVE but #133010 persists:")
print("   - Wait 5-10 minutes after sending 'Hi' message")
print("   - Verify the exact phone number format matches")
print("   - Check if WhatsApp is installed on that number")
print("   - Try sending from the business number to your number first")
print()
print("=" * 70)
