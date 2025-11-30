#!/usr/bin/env python
"""
Test script for Twilio WhatsApp integration.
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from dotenv import load_dotenv
from apps.candidate.whatsapp_service import whatsapp_service
from apps.candidate.models import Candidate

# Load environment variables
load_dotenv()

def test_configuration():
    """Test if Twilio WhatsApp is configured."""
    print("=" * 70)
    print("Twilio WhatsApp - Configuration Test")
    print("=" * 70)
    print()
    
    print("1. Checking configuration...")
    
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    whatsapp_from = os.getenv('TWILIO_WHATSAPP_FROM')
    
    if account_sid:
        print(f"   ✅ TWILIO_ACCOUNT_SID: {account_sid[:10]}...")
    else:
        print("   ❌ TWILIO_ACCOUNT_SID: NOT SET")
    
    if auth_token:
        print(f"   ✅ TWILIO_AUTH_TOKEN: {auth_token[:10]}...")
    else:
        print("   ❌ TWILIO_AUTH_TOKEN: NOT SET")
    
    if whatsapp_from:
        print(f"   ✅ TWILIO_WHATSAPP_FROM: {whatsapp_from}")
    else:
        print("   ❌ TWILIO_WHATSAPP_FROM: NOT SET")
    
    print()
    
    if whatsapp_service.is_configured():
        print("   ✅ Twilio WhatsApp is configured!")
        return True
    else:
        print("   ❌ Twilio WhatsApp is NOT configured!")
        print()
        print("   Please set these environment variables in your .env file:")
        print("   - TWILIO_ACCOUNT_SID")
        print("   - TWILIO_AUTH_TOKEN")
        print("   - TWILIO_WHATSAPP_FROM")
        print()
        print("   Get these from: https://console.twilio.com/")
        return False


def test_phone_formatting():
    """Test phone number formatting."""
    print()
    print("2. Testing phone number formatting...")
    print()
    
    test_numbers = [
        "11 99999-8888",
        "11 9999-8888",
        "(11) 99999-8888",
        "+55 11 99999-8888",
        "5511999998888",
        "85 98880-6269",
        "85 8880-6269",
    ]
    
    for number in test_numbers:
        formatted = whatsapp_service.format_phone_number(number)
        print(f"   {number:20} → {formatted}")


def test_send_message():
    """Test sending a message to a phone number."""
    print()
    print("3. Testing message sending...")
    print()
    
    phone = input("   Enter a test phone number (XX XXXXX-XXXX) or press Enter to skip: ").strip()
    
    if not phone:
        print("   ⏭️  Skipping message send test")
        return
    
    print(f"   Formatted number: {whatsapp_service.format_phone_number(phone)}")
    print()
    print("   Sending test message...")
    
    try:
        from twilio.rest import Client
        
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        message = client.messages.create(
            body='🧪 Teste WhatsApp Twilio - Pinte Pinturas\n\nSe você recebeu esta mensagem, a integração está funcionando!',
            from_=os.getenv('TWILIO_WHATSAPP_FROM'),
            to=whatsapp_service.format_phone_number(phone)
        )
        
        print(f"   ✅ Message sent successfully!")
        print(f"   📬 Message SID: {message.sid}")
        print(f"   📊 Status: {message.status}")
        print()
        print("   Check your WhatsApp to confirm receipt.")
        
    except Exception as e:
        print(f"   ❌ Failed to send message")
        print(f"   Error: {e}")
        print()
        print("   Common issues:")
        print("   - Invalid Twilio credentials")
        print("   - Phone number not joined Twilio sandbox (for sandbox numbers)")
        print("   - Invalid phone number format")
        print("   - Insufficient Twilio account balance")


def test_with_candidate():
    """Test sending message to a candidate from database."""
    print()
    print("4. Testing with candidate from database...")
    print()
    
    # Get candidates with phone numbers
    candidates = Candidate.objects.exclude(phone_number__isnull=True).exclude(phone_number='')[:5]
    
    if not candidates:
        print("   ⚠️  No candidates with phone numbers found in database")
        return
    
    print("   Found candidates:")
    for i, candidate in enumerate(candidates, 1):
        print(f"   {i}. {candidate.full_name} - {candidate.phone_number}")
    
    print()
    choice = input("   Enter candidate number to send test message (or press Enter to skip): ").strip()
    
    if not choice:
        print("   ⏭️  Skipping candidate test")
        return
    
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(candidates):
            print("   ❌ Invalid choice")
            return
        
        candidate = candidates[idx]
        print(f"   Sending test message to {candidate.full_name}...")
        
        message_body = f"""📱 *Teste WhatsApp - Pinte Pinturas*

Olá {candidate.full_name}!

Esta é uma mensagem de teste do sistema de recrutamento.

✅ Se você recebeu esta mensagem, a integração Twilio WhatsApp está funcionando perfeitamente!

_Pinte Pinturas - Equipe de RH_"""
        
        result = whatsapp_service._try_send_message(candidate, message_body)
        
        if result['success']:
            print(f"   ✅ Message sent successfully!")
            print(f"   📬 Message SID: {result['message_sid']}")
            print(f"   📱 Phone format used: {result.get('phone_format_used')}")
            print()
            print("   The working phone format has been saved to the candidate record.")
        else:
            print(f"   ❌ Failed to send message")
            print(f"   Error: {result.get('error')}")
        
    except ValueError:
        print("   ❌ Invalid input")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Run all tests."""
    try:
        # Test configuration
        if not test_configuration():
            return
        
        # Test phone formatting
        test_phone_formatting()
        
        # Test sending message
        test_send_message()
        
        # Test with candidate
        test_with_candidate()
        
        print()
        print("=" * 70)
        print("Test completed!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. If using Twilio Sandbox, make sure recipients join the sandbox first")
        print("2. For production, get an approved WhatsApp Business number from Twilio")
        print("3. Test with a real interview creation in your application")
        print()
        print("For setup instructions, see:")
        print("📖 WHATSAPP_SETUP_GUIDE.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
