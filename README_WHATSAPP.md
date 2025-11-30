# 📱 WhatsApp Integration for Interview Notifications

## Overview

This integration automatically sends WhatsApp messages to candidates when interviews are scheduled, cancelled, or rescheduled using Twilio's WhatsApp API.

## ✨ Features

- ✅ **Automatic Notifications** - Messages sent automatically when interviews are created or updated
- ✅ **Professional Templates** - Beautifully formatted messages in Portuguese with emojis
- ✅ **Multiple Message Types** - Scheduled, cancelled, rescheduled, and reminder messages
- ✅ **Tracking** - Full tracking of message delivery with Twilio SIDs
- ✅ **Error Handling** - Graceful degradation if Twilio is not configured
- ✅ **Phone Formatting** - Automatic conversion of Brazilian phone numbers to WhatsApp format

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Twilio

Add to your `.env` file:

```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Test Configuration

```bash
python test_whatsapp.py
```

## 📖 Documentation

- **[Quick Start Guide](WHATSAPP_QUICK_START.md)** - Get up and running in 5 minutes
- **[Complete Setup Guide](WHATSAPP_SETUP_GUIDE.md)** - Detailed configuration and troubleshooting
- **[Integration Summary](../WHATSAPP_INTEGRATION_SUMMARY.md)** - Technical implementation details

## 🔧 How It Works

### When an Interview is Created

```python
# In your code or API
interview = Interview.objects.create(
    candidate=candidate,
    title="Entrevista Técnica",
    scheduled_date="2024-01-15",
    scheduled_time="14:00",
    status="scheduled"
)
# WhatsApp is sent automatically! ✅
```

### Message Flow

1. Interview created/updated via API
2. `InterviewViewSet` detects the action
3. WhatsApp service is invoked
4. Message sent via Twilio
5. Interview updated with tracking info
6. Logs recorded for monitoring

## 📱 Message Examples

### Interview Scheduled
```
🎯 *Entrevista Agendada - Pinte Pinturas*

Olá João Silva! 👋

Sua entrevista foi agendada com sucesso! ✅

📋 *Detalhes da Entrevista:*
• *Título:* Entrevista Técnica
• *Tipo:* Vídeo
• *Data:* 15/01/2024
• *Horário:* 14:00
• *Duração:* 60 minutos

⏰ Por favor, chegue com 10 minutos de antecedência.

💼 Boa sorte! Estamos ansiosos para conhecê-lo(a)!

_Pinte Pinturas - Equipe de RH_
```

## 🔍 Monitoring

### Check Logs

```bash
# Django logs will show:
WhatsApp notification sent for interview 123
# or
Failed to send WhatsApp for interview 123: [error details]
```

### Check Database

```python
interview = Interview.objects.get(id=123)
print(f"WhatsApp sent: {interview.whatsapp_sent}")
print(f"Message SID: {interview.whatsapp_message_sid}")
print(f"Sent at: {interview.whatsapp_sent_at}")
```

### Check Twilio Console

Visit https://console.twilio.com/us1/monitor/logs/sms to see all message logs.

## 🧪 Testing

### Sandbox Mode (Free)

1. Join Twilio WhatsApp Sandbox
2. Send join code to +1 415 523 8886
3. Create test interview
4. Verify message received

### Test Script

```bash
python test_whatsapp.py
```

This will:
- Check if Twilio is configured
- Test phone number formatting
- Optionally send a test message

## 🛠️ API Changes

### Interview API Response

```json
{
  "id": 1,
  "candidate_name": "João Silva",
  "title": "Entrevista Técnica",
  "scheduled_date": "2024-01-15",
  "scheduled_time": "14:00:00",
  "status": "scheduled",
  "whatsapp_sent": true,
  "whatsapp_message_sid": "SM1234567890abcdef",
  "whatsapp_sent_at": "2024-01-10T10:30:00Z",
  ...
}
```

## 🔐 Security

- ✅ Credentials in environment variables
- ✅ `.env` excluded from git
- ✅ No hardcoded secrets
- ✅ Secure Twilio authentication

## 💰 Pricing

- **Sandbox:** FREE (testing only)
- **Production:** ~$0.005-$0.01 per message
- **Free Trial:** Twilio provides trial credits

## 🐛 Troubleshooting

### "WhatsApp service not configured"

**Cause:** Environment variables not set

**Solution:**
```bash
# Check .env file has:
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### Messages not delivered

**Cause:** Sandbox not joined (in sandbox mode)

**Solution:** Candidate must send join message to Twilio number

### Invalid phone number

**Cause:** Phone not in correct format

**Solution:** Ensure format is `XX XXXXX-XXXX` (e.g., `11 98765-4321`)

## 📚 Code Structure

```
ficha-backend/
├── apps/candidate/
│   ├── whatsapp_service.py          # WhatsApp service class
│   ├── api_views.py                 # Updated with WhatsApp integration
│   ├── models.py                    # Interview model with WhatsApp fields
│   └── serializers.py               # Updated serializers
├── WHATSAPP_SETUP_GUIDE.md          # Complete setup guide
├── WHATSAPP_QUICK_START.md          # Quick reference
├── README_WHATSAPP.md               # This file
└── test_whatsapp.py                 # Test script
```

## 🎯 Next Steps

1. ✅ Dependencies installed
2. ✅ Database migrated
3. 🔄 Configure Twilio credentials
4. 🔄 Test with sandbox
5. 🔄 Deploy to production

## 💡 Advanced Features

### Scheduled Reminders

Implement with Django Celery:

```python
from celery import shared_task
from datetime import datetime, timedelta

@shared_task
def send_interview_reminders():
    tomorrow = datetime.now().date() + timedelta(days=1)
    interviews = Interview.objects.filter(
        scheduled_date=tomorrow,
        status='scheduled',
        reminder_sent=False
    )
    
    for interview in interviews:
        result = whatsapp_service.send_interview_reminder_message(interview)
        if result['success']:
            interview.reminder_sent = True
            interview.save()
```

### Custom Templates

Modify templates in `whatsapp_service.py`:

```python
message_body = f"""🎯 *Your Custom Template*

Hello {candidate.full_name}!

Your interview details...
"""
```

## 📞 Support

- **Twilio Support:** https://support.twilio.com
- **WhatsApp API Docs:** https://www.twilio.com/docs/whatsapp
- **Django Logs:** Check console output for errors

## 🎉 Success!

Your WhatsApp integration is ready! Create an interview and watch the magic happen! ✨

---

**Made with ❤️ for Pinte Pinturas**
