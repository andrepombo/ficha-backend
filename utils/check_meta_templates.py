#!/usr/bin/env python
"""
Check Meta WhatsApp templates status.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

waba_id = input("Enter your WABA ID (WhatsApp Business Account ID): ").strip()
token = os.getenv('META_PERMANENT_ACCESS_TOKEN')
api_version = os.getenv('META_API_VERSION', 'v20.0')

if not waba_id or not token:
    print("❌ Missing WABA ID or token")
    exit(1)

print("\n" + "=" * 70)
print("Meta WhatsApp Templates Check")
print("=" * 70)
print()

# List templates
url = f"https://graph.facebook.com/{api_version}/{waba_id}/message_templates"
headers = {'Authorization': f'Bearer {token}'}

print("Fetching templates...")
resp = requests.get(url, headers=headers)

if resp.status_code == 200:
    data = resp.json()
    templates = data.get('data', [])
    
    if not templates:
        print("⚠️  No templates found")
    else:
        print(f"✅ Found {len(templates)} template(s):\n")
        for tpl in templates:
            print(f"   Name: {tpl.get('name')}")
            print(f"   Status: {tpl.get('status')}")
            print(f"   Language: {tpl.get('language')}")
            print(f"   Category: {tpl.get('category')}")
            print()
else:
    print(f"❌ Error {resp.status_code}: {resp.text}")

print("=" * 70)
