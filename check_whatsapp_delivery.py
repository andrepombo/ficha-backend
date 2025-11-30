"""
WhatsApp Message Delivery Status Checker (Standalone)

This script checks the actual delivery status of WhatsApp messages sent via Twilio.
Use this to diagnose why messages aren't being received even though they're sent successfully.

Usage:
    python check_whatsapp_delivery.py <message_sid>
    
Example:
    python check_whatsapp_delivery.py SMfb21b17541022e204f5bf78f3e314480
"""

import os
import sys
from twilio.rest import Client
from datetime import datetime


def check_message_status(message_sid):
    """
    Check the delivery status of a WhatsApp message.
    
    Args:
        message_sid: The Twilio Message SID to check
    """
    # Get Twilio credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Error: Twilio credentials not configured")
        print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables")
        return
    
    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
    try:
        # Fetch message details
        message = client.messages(message_sid).fetch()
        
        print("\n" + "="*70)
        print("📱 WHATSAPP MESSAGE DELIVERY STATUS")
        print("="*70)
        print(f"\n📋 Message SID: {message.sid}")
        print(f"📅 Date Created: {message.date_created}")
        print(f"📤 From: {message.from_}")
        print(f"📥 To: {message.to}")
        print(f"📊 Status: {message.status}")
        
        # Status explanation
        status_info = {
            'queued': '⏳ Message is queued and will be sent shortly',
            'sending': '📤 Message is currently being sent',
            'sent': '✅ Message was sent to WhatsApp servers',
            'delivered': '✅ Message was delivered to recipient',
            'read': '✅ Message was read by recipient',
            'failed': '❌ Message failed to send',
            'undelivered': '❌ Message could not be delivered'
        }
        
        print(f"\n💡 Status Meaning: {status_info.get(message.status, 'Unknown status')}")
        
        # Check for errors
        if message.error_code:
            print(f"\n❌ ERROR DETECTED:")
            print(f"   Error Code: {message.error_code}")
            print(f"   Error Message: {message.error_message}")
            
            # Common error codes
            error_explanations = {
                63007: "Recipient is not a valid WhatsApp user or hasn't opted in",
                21211: "Invalid 'To' phone number",
                21408: "Permission to send to this number has not been enabled",
                63016: "Recipient phone number is not a WhatsApp number",
                63015: "Recipient has not joined your Twilio Sandbox (sandbox only)",
            }
            
            if message.error_code in error_explanations:
                print(f"   📖 Explanation: {error_explanations[message.error_code]}")
        
        # Price information
        if message.price:
            print(f"\n💰 Price: {message.price} {message.price_unit}")
        
        # Message body preview
        if message.body:
            preview = message.body[:100] + "..." if len(message.body) > 100 else message.body
            print(f"\n📝 Message Preview:")
            print(f"   {preview}")
        
        # Delivery insights
        print(f"\n🔍 DELIVERY INSIGHTS:")
        
        if message.status == 'sent':
            print("   ⚠️  Message was sent but not yet delivered.")
            print("   This could mean:")
            print("   1. Recipient's phone is offline")
            print("   2. Recipient hasn't opened WhatsApp yet")
            print("   3. Phone number format doesn't match WhatsApp registration")
            print("   4. Recipient blocked your WhatsApp Business number")
            print("\n   💡 Suggestion: Wait a few minutes and check again")
            
        elif message.status == 'delivered':
            print("   ✅ Message was successfully delivered!")
            print("   The recipient should have received it in their WhatsApp.")
            
        elif message.status == 'failed' or message.status == 'undelivered':
            print("   ❌ Message delivery failed.")
            print("   Common reasons:")
            print("   1. Invalid phone number format")
            print("   2. Number is not registered on WhatsApp")
            print("   3. Recipient has blocked your number")
            print("   4. WhatsApp Business API restrictions")
            
        elif message.status == 'queued' or message.status == 'sending':
            print("   ⏳ Message is still being processed.")
            print("   Check again in a few seconds.")
        
        # Phone number format check
        to_number = message.to.replace('whatsapp:', '')
        print(f"\n📞 PHONE NUMBER ANALYSIS:")
        print(f"   Full number: {to_number}")
        
        if to_number.startswith('+55'):
            area_code = to_number[3:5]
            number_part = to_number[5:]
            print(f"   Country: Brazil (+55)")
            print(f"   Area Code: {area_code}")
            print(f"   Number: {number_part}")
            print(f"   Digit Count: {len(number_part)} digits")
            
            if len(number_part) == 9:
                print(f"   Format: 9-digit mobile (modern format)")
            elif len(number_part) == 8:
                print(f"   Format: 8-digit (older format or landline)")
            else:
                print(f"   ⚠️  Unusual digit count - may cause delivery issues")
            
            # Area code 85 specific
            if area_code == '85':
                print(f"\n   ℹ️  Area code 85 (Fortaleza/CE) Note:")
                print(f"   Some numbers in this area use 8-digit format even for mobile.")
                print(f"   If delivery fails, try the alternative format.")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error fetching message status: {e}")
        print(f"Make sure the Message SID is correct: {message_sid}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_whatsapp_delivery.py <message_sid>")
        print("\nExample:")
        print("  python check_whatsapp_delivery.py SMfb21b17541022e204f5bf78f3e314480")
        sys.exit(1)
    
    message_sid = sys.argv[1]
    check_message_status(message_sid)


if __name__ == '__main__':
    main()
