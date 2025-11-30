#!/usr/bin/env python
"""
Check Meta WhatsApp phone number configuration and permissions.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

phone_id = os.getenv('META_PHONE_NUMBER_ID')
token = os.getenv('META_PERMANENT_ACCESS_TOKEN')
api_version = os.getenv('META_API_VERSION', 'v20.0')

print("=" * 70)
print("Meta WhatsApp Phone Number Check")
print("=" * 70)
print()

if not phone_id or not token:
    print("❌ META_PHONE_NUMBER_ID or META_PERMANENT_ACCESS_TOKEN not set")
    exit(1)

print(f"Phone Number ID: {phone_id}")
print(f"API Version: {api_version}")
print()

# Check phone number details
url = f"https://graph.facebook.com/{api_version}/{phone_id}"
headers = {'Authorization': f'Bearer {token}'}

print("Checking phone number details...")
resp = requests.get(url, headers=headers)

if resp.status_code == 200:
    data = resp.json()
    print("✅ Phone number found:")
    print(f"   Display Name: {data.get('display_phone_number')}")
    print(f"   Verified Name: {data.get('verified_name')}")
    print(f"   Quality Rating: {data.get('quality_rating')}")
    print(f"   ID: {data.get('id')}")
else:
    print(f"❌ Error {resp.status_code}: {resp.text}")
    
print()
print("=" * 70)
