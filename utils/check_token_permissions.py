#!/usr/bin/env python
"""
Check Meta access token permissions.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('META_PERMANENT_ACCESS_TOKEN')

print("=" * 70)
print("Meta Access Token Permissions Check")
print("=" * 70)
print()

if not token:
    print("❌ META_PERMANENT_ACCESS_TOKEN not set")
    exit(1)

# Debug token to see permissions
url = f"https://graph.facebook.com/v20.0/debug_token?input_token={token}&access_token={token}"

print("Checking token permissions...")
resp = requests.get(url)

if resp.status_code == 200:
    data = resp.json().get('data', {})
    print("✅ Token info:")
    print(f"   App ID: {data.get('app_id')}")
    print(f"   Type: {data.get('type')}")
    print(f"   Valid: {data.get('is_valid')}")
    print(f"   Expires: {data.get('expires_at', 'Never')}")
    print()
    print("   Scopes/Permissions:")
    scopes = data.get('scopes', [])
    if scopes:
        for scope in scopes:
            print(f"      - {scope}")
    else:
        print("      (No scopes listed)")
    
    # Check for required scopes
    required = ['whatsapp_business_messaging', 'whatsapp_business_management']
    missing = [s for s in required if s not in scopes]
    
    if missing:
        print()
        print(f"   ⚠️  Missing required scopes: {', '.join(missing)}")
        print("   → Regenerate token with these permissions in Business Manager")
else:
    print(f"❌ Error {resp.status_code}: {resp.text}")

print()
print("=" * 70)
