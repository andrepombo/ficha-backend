#!/usr/bin/env python
"""
Direct test of WhatsApp sandbox with a specific phone number.
This sends a test message directly without needing a database interview.

Usage:
    python test_sandbox_direct.py "85 99999-8888"
"""

import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

def send_test_message(phone_number):
    """Send a test WhatsApp message to the specified phone number."""
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    whatsapp_from = os.getenv('TWILIO_WHATSAPP_FROM')
    
    if not all([account_sid, auth_token, whatsapp_from]):
        print("❌ Twilio credentials not configured in .env")
        return
    
    # Format phone number
    cleaned = phone_number.replace(' ', '').replace('-', '')
    if not cleaned.startswith('+'):
        cleaned = f'+55{cleaned}'
    whatsapp_to = f'whatsapp:{cleaned}'
    
    print("=" * 60)
    print("WhatsApp Sandbox Direct Test")
    print("=" * 60)
    print(f"From: {whatsapp_from}")
    print(f"To: {whatsapp_to}")
    print()
    
    try:
        client = Client(account_sid, auth_token)
        
        message_body = """🎯 *Teste WhatsApp - Pinte Pinturas*

Olá! 👋

Este é um teste da integração WhatsApp.

Se você recebeu esta mensagem, significa que:
✅ Você entrou no sandbox com sucesso
✅ A integração está funcionando perfeitamente
✅ Mensagens automáticas de entrevistas funcionarão!

🎉 Parabéns! O sistema está pronto para uso.

_Pinte Pinturas - Equipe de RH_"""
        
        message = client.messages.create(
            body=message_body,
            from_=whatsapp_from,
            to=whatsapp_to
        )
        
        print(f"✅ Message sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        print()
        print("=" * 60)
        print("Check your WhatsApp now!")
        print("=" * 60)
        print()
        print("If you received the message:")
        print("  ✅ Sandbox is working perfectly!")
        print("  ✅ Interview notifications will work automatically")
        print()
        print("If you didn't receive it:")
        print("  ⚠️  Wait 10-30 seconds and check again")
        print(f"  🔍 Check message status: python check_message_status.py {message.sid}")
        print()
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_sandbox_direct.py \"XX XXXXX-XXXX\"")
        print("\nExample:")
        print("python test_sandbox_direct.py \"85 99999-8888\"")
        print()
        print("Use the phone number that joined the Twilio sandbox.")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    send_test_message(phone_number)
