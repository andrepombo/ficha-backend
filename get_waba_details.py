#!/usr/bin/env python
"""
Get WABA details and check business verification status.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

phone_id = os.getenv('META_PHONE_NUMBER_ID')
token = os.getenv('META_PERMANENT_ACCESS_TOKEN')
api_version = os.getenv('META_API_VERSION', 'v20.0')

print("=" * 70)
print("WABA Details and Verification Status")
print("=" * 70)
print()

# Get phone number to find WABA ID
url = f"https://graph.facebook.com/{api_version}/{phone_id}"
headers = {'Authorization': f'Bearer {token}'}
params = {'fields': 'id,verified_name,display_phone_number,quality_rating,account_mode,is_official_business_account'}

resp = requests.get(url, headers=headers, params=params)

if resp.status_code == 200:
    phone_data = resp.json()
    print("Phone Number Info:")
    print(f"  ID: {phone_data.get('id')}")
    print(f"  Display: {phone_data.get('display_phone_number')}")
    print(f"  Verified Name: {phone_data.get('verified_name')}")
    print(f"  Official Business: {phone_data.get('is_official_business_account', 'Unknown')}")
    print()
    
    # Try to get WABA ID from phone number
    waba_url = f"https://graph.facebook.com/{api_version}/{phone_id}?fields=whatsapp_business_account_id"
    waba_resp = requests.get(waba_url, headers=headers)
    
    if waba_resp.status_code == 200:
        waba_data = waba_resp.json()
        waba_id = waba_data.get('whatsapp_business_account_id')
        
        if waba_id:
            print(f"WABA ID: {waba_id}")
            print()
            
            # Get WABA details
            waba_detail_url = f"https://graph.facebook.com/{api_version}/{waba_id}"
            waba_detail_params = {'fields': 'id,name,timezone_id,message_template_namespace,account_review_status,business_verification_status,messaging_limit_tier'}
            waba_detail_resp = requests.get(waba_detail_url, headers=headers, params=waba_detail_params)
            
            if waba_detail_resp.status_code == 200:
                waba_details = waba_detail_resp.json()
                print("WABA Details:")
                print(f"  Name: {waba_details.get('name')}")
                print(f"  Account Review: {waba_details.get('account_review_status', 'UNKNOWN')}")
                print(f"  Business Verification: {waba_details.get('business_verification_status', 'UNKNOWN')}")
                print(f"  Messaging Tier: {waba_details.get('messaging_limit_tier', 'UNKNOWN')}")
                print()
                
                # Check if verification is needed
                if waba_details.get('business_verification_status') != 'verified':
                    print("⚠️  BUSINESS NOT VERIFIED")
                    print("   This is likely why #133010 persists")
                    print()
                    print("   To fix:")
                    print("   1. Go to business.facebook.com")
                    print("   2. Settings → Security Center → Business Verification")
                    print("   3. Complete verification process")
                    print("   4. Wait for approval (1-3 business days)")
                
                tier = waba_details.get('messaging_limit_tier', 'TIER_NOT_SET')
                if tier in ['TIER_NOT_SET', 'TIER_50']:
                    print("⚠️  LIMITED MESSAGING TIER")
                    print(f"   Current tier: {tier}")
                    print("   You can only message numbers that have messaged you")
                    print("   Tier increases as you send more messages successfully")
            else:
                print(f"Error getting WABA details: {waba_detail_resp.status_code}")
        else:
            print("⚠️  Could not find WABA ID")
    else:
        print(f"Error getting WABA: {waba_resp.status_code}")
else:
    print(f"Error: {resp.status_code} - {resp.text}")

print()
print("=" * 70)
print()
print("NEXT STEPS:")
print("1. If business not verified → Complete verification in Business Manager")
print("2. If tier is limited → You MUST have received a message from the number first")
print("3. Try sending a message FROM your business number TO your personal number")
print("   (Use WhatsApp Business app or Meta Business Suite)")
print()
print("=" * 70)
