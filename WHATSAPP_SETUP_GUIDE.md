# WhatsApp Integration Setup Guide

This guide will help you set up WhatsApp notifications for interview scheduling using Twilio's WhatsApp API.

## Overview

The system automatically sends WhatsApp messages to candidates when:
- ✅ An interview is scheduled (new interview created)
- 🔄 An interview is rescheduled
- ❌ An interview is cancelled
- ⏰ Interview reminders (can be implemented as a scheduled task)

## Prerequisites

1. A Twilio account (sign up at https://www.twilio.com)
2. WhatsApp Business API access through Twilio
3. Python packages installed (already added to requirements.txt)

## Step 1: Create a Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account
3. Verify your email and phone number

## Step 2: Get Your Twilio Credentials

1. Log in to your Twilio Console: https://console.twilio.com
2. From the dashboard, copy:
   - **Account SID** (starts with "AC...")
   - **Auth Token** (click to reveal)

## Step 3: Set Up WhatsApp

### Option A: Twilio Sandbox (For Testing)

The easiest way to get started is using Twilio's WhatsApp Sandbox:

1. In Twilio Console, go to **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Follow the instructions to join the sandbox:
   - Send a WhatsApp message with the code shown (e.g., "join <your-code>") to the Twilio number
   - The sandbox number is usually: **+1 415 523 8886**
3. Your sandbox WhatsApp number will be: `whatsapp:+14155238886`

**Note:** In sandbox mode, each candidate must join the sandbox before receiving messages. This is only for testing.

### Option B: Production WhatsApp Number (Recommended for Production)

For production use, you need an approved WhatsApp Business number:

1. In Twilio Console, go to **Messaging** → **WhatsApp** → **Senders**
2. Click **New Sender**
3. Follow the approval process (requires business verification)
4. Once approved, you'll get your WhatsApp-enabled phone number

## Step 4: Configure Environment Variables

1. Open your `.env` file in the backend directory
2. Add the following variables:

```bash
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886  # Use your actual WhatsApp number
```

**Example:**
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_secret_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

## Step 5: Install Dependencies

Run the following command in your backend directory:

```bash
pip install -r requirements.txt
```

This will install the Twilio Python SDK.

## Step 6: Run Database Migrations

Create and apply the database migration for the new WhatsApp tracking fields:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 7: Test the Integration

### Test 1: Create a Test Interview

1. Make sure you have a candidate with a valid Brazilian phone number in the format: `XX XXXXX-XXXX`
2. Create a new interview through the API or admin panel
3. Check the candidate's WhatsApp for the notification

### Test 2: Check Logs

Monitor the Django logs to see if WhatsApp messages are being sent:

```bash
python manage.py runserver
```

Look for log messages like:
- `WhatsApp notification sent for interview {id}`
- `Failed to send WhatsApp for interview {id}: {error}`

## Message Templates

The system sends different messages based on the action:

### 1. Interview Scheduled
```
🎯 *Entrevista Agendada - Pinte Pinturas*

Olá [Nome]! 👋

Sua entrevista foi agendada com sucesso! ✅

📋 *Detalhes da Entrevista:*
• *Título:* [Título]
• *Tipo:* [Tipo]
• *Data:* [Data]
• *Horário:* [Horário]
• *Duração:* [Duração] minutos
• *Link/Local:* [Link ou Local]

📝 *Informações adicionais:*
[Descrição]

⏰ Por favor, chegue com 10 minutos de antecedência.

💼 Boa sorte! Estamos ansiosos para conhecê-lo(a)!

_Pinte Pinturas - Equipe de RH_
```

### 2. Interview Cancelled
```
❌ *Entrevista Cancelada - Pinte Pinturas*

Olá [Nome],

Informamos que a entrevista agendada foi cancelada:

📋 *Detalhes:*
• *Título:* [Título]
• *Data:* [Data]
• *Horário:* [Horário]

Entraremos em contato em breve para reagendar.

Agradecemos sua compreensão.

_Pinte Pinturas - Equipe de RH_
```

### 3. Interview Rescheduled
```
🔄 *Entrevista Reagendada - Pinte Pinturas*

Olá [Nome]!

Sua entrevista foi reagendada:

✅ *Nova data:*
• *Data:* [Nova Data]
• *Horário:* [Novo Horário]
• *Título:* [Título]

Agradecemos sua compreensão!

_Pinte Pinturas - Equipe de RH_
```

## Troubleshooting

### Issue: "WhatsApp service not configured"

**Solution:** Check that all three environment variables are set correctly in your `.env` file.

### Issue: "Failed to send WhatsApp message"

**Possible causes:**
1. Invalid phone number format
2. Twilio credentials are incorrect
3. WhatsApp sandbox not joined (in sandbox mode)
4. Insufficient Twilio credits

**Solution:**
- Verify phone number is in correct format: `XX XXXXX-XXXX`
- Check Twilio Console for error logs
- Ensure candidate has joined the sandbox (if using sandbox)
- Check your Twilio account balance

### Issue: Phone number format errors

**Solution:** The system expects Brazilian phone numbers in the format: `XX XXXXX-XXXX`
- Example: `11 98765-4321`
- The service automatically converts this to `+5511987654321` for WhatsApp

### Issue: Messages not being delivered

**Possible causes:**
1. Candidate hasn't opted in to receive WhatsApp messages
2. Phone number is invalid or doesn't have WhatsApp
3. Twilio account limitations

**Solution:**
- In sandbox mode, ensure the candidate has sent the join message
- Verify the phone number has WhatsApp installed
- Check Twilio Console message logs for delivery status

## WhatsApp Tracking Fields

The Interview model now includes these fields to track WhatsApp notifications:

- `whatsapp_sent` (Boolean): Whether a WhatsApp notification was sent
- `whatsapp_message_sid` (String): Twilio message ID for tracking
- `whatsapp_sent_at` (DateTime): When the WhatsApp was sent

You can view these in the Django admin panel or through the API.

## API Response

When creating or updating an interview, the API will attempt to send WhatsApp notifications automatically. The response will include the WhatsApp tracking fields:

```json
{
  "id": 1,
  "candidate_name": "João Silva",
  "title": "Entrevista Técnica",
  "scheduled_date": "2024-01-15",
  "scheduled_time": "14:00:00",
  "whatsapp_sent": true,
  "whatsapp_message_sid": "SM1234567890abcdef",
  "whatsapp_sent_at": "2024-01-10T10:30:00Z",
  ...
}
```

## Cost Considerations

### Twilio Pricing (as of 2024)
- **Sandbox:** Free for testing (limited recipients)
- **WhatsApp Messages:** ~$0.005 - $0.01 per message (varies by country)
- **Free Trial:** Twilio provides trial credits for testing

### Recommendations
1. Start with the sandbox for development and testing
2. Monitor your Twilio usage in the Console
3. Set up billing alerts to avoid unexpected charges
4. Consider implementing rate limiting for production

## Advanced Features (Optional)

### 1. Scheduled Reminders

You can implement automated reminders using Django Celery:

```python
# In a celery task
from apps.candidate.models import Interview
from apps.candidate.whatsapp_service import whatsapp_service
from datetime import datetime, timedelta

def send_interview_reminders():
    """Send reminders 24 hours before interviews"""
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

### 2. Custom Message Templates

You can customize the message templates in `whatsapp_service.py` to match your company's branding and tone.

### 3. Multi-language Support

Add language detection based on candidate preferences and send messages in their preferred language.

## Security Best Practices

1. **Never commit `.env` file** - Keep credentials secure
2. **Use environment variables** - Don't hardcode credentials
3. **Rotate tokens regularly** - Update Twilio auth tokens periodically
4. **Monitor usage** - Set up alerts for unusual activity
5. **Validate phone numbers** - Ensure proper format before sending

## Support

For issues related to:
- **Twilio:** https://support.twilio.com
- **WhatsApp Business API:** https://www.twilio.com/docs/whatsapp
- **This Integration:** Check Django logs and Twilio Console

## Next Steps

1. ✅ Set up Twilio account
2. ✅ Configure environment variables
3. ✅ Run migrations
4. ✅ Test with sandbox
5. 🔄 Apply for production WhatsApp number (if needed)
6. 🔄 Implement scheduled reminders (optional)
7. 🔄 Customize message templates (optional)

---

**Happy messaging! 🎉**
