#!/usr/bin/env python
"""
Check the status of a Twilio WhatsApp message.
This helps debug why messages aren't being delivered.

Usage:
    python check_message_status.py SM43e3ae16048145c3cff0f518ce30fdae
"""

import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

def check_message_status(message_sid):
    """Check the status of a Twilio message."""
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Twilio credentials not found in .env file")
        return
    
    try:
        client = Client(account_sid, auth_token)
        message = client.messages(message_sid).fetch()
        
        print("=" * 60)
        print("Message Status Check")
        print("=" * 60)
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        print(f"To: {message.to}")
        print(f"From: {message.from_}")
        print(f"Date Created: {message.date_created}")
        print(f"Date Updated: {message.date_updated}")
        print(f"Direction: {message.direction}")
        print(f"Price: {message.price} {message.price_unit}")
        
        if message.error_code:
            print(f"\n❌ Error Code: {message.error_code}")
            print(f"Error Message: {message.error_message}")
        
        print("\n" + "=" * 60)
        print("Status Meanings:")
        print("=" * 60)
        print("• queued: Message is waiting to be sent")
        print("• sent: Message sent to WhatsApp")
        print("• delivered: Message delivered to recipient")
        print("• undelivered: Message could not be delivered")
        print("• failed: Message failed to send")
        print("\n")
        
        if message.status == 'queued':
            print("⚠️  Message is QUEUED")
            print("\nMost common reason: Recipient hasn't joined the Twilio Sandbox")
            print("\nTo fix:")
            print("1. Have the recipient send a WhatsApp message to: +1 415 523 8886")
            print("2. The message should be: join <your-sandbox-code>")
            print("3. Find your code at: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
            print("\n")
        elif message.status == 'undelivered' or message.status == 'failed':
            print("❌ Message FAILED to deliver")
            print("\nCheck the error code above for details")
            print("Common issues:")
            print("- Recipient not in sandbox (for sandbox mode)")
            print("- Invalid phone number format")
            print("- Recipient blocked the number")
            print("\n")
        elif message.status == 'delivered':
            print("✅ Message was DELIVERED successfully!")
            print("\n")
        
    except Exception as e:
        print(f"❌ Error checking message status: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_message_status.py <MESSAGE_SID>")
        print("\nExample:")
        print("python check_message_status.py SM43e3ae16048145c3cff0f518ce30fdae")
        sys.exit(1)
    
    message_sid = sys.argv[1]
    check_message_status(message_sid)
