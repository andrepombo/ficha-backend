# WhatsApp Integration - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Get Twilio Credentials

1. Sign up at https://www.twilio.com/try-twilio
2. Go to Console: https://console.twilio.com
3. Copy your **Account SID** and **Auth Token**

### 2. Join WhatsApp Sandbox (For Testing)

1. In Twilio Console: **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Send the join code to **+1 415 523 8886** from your WhatsApp
3. Example: Send `join <your-code>` to the number

### 3. Configure Environment Variables

Edit your `.env` file and add:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_secret_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### 4. Run Migrations

```bash
cd /home/lock221/pinte_fichas/ficha-backend
python manage.py migrate
```

### 5. Test It!

Create a new interview through your application and the candidate will receive a WhatsApp message automatically! 🎉

---

## 📱 What Gets Sent

### When Interview is Scheduled
Candidate receives a beautifully formatted message with:
- Interview title, type, date, and time
- Duration and location/meeting link
- Additional instructions
- Professional company branding

### When Interview is Cancelled
Candidate receives a cancellation notification with interview details.

### When Interview is Rescheduled
Candidate receives the new date and time information.

---

## 🔍 Troubleshooting

**Problem:** "WhatsApp service not configured"
- **Solution:** Check that all 3 environment variables are set in `.env`

**Problem:** Messages not being delivered
- **Solution:** In sandbox mode, make sure the candidate has joined the sandbox by sending the join message

**Problem:** Invalid phone number
- **Solution:** Ensure candidate phone numbers are in format: `XX XXXXX-XXXX` (e.g., `11 98765-4321`)

---

## 📊 Tracking

Each interview now tracks:
- `whatsapp_sent`: Whether WhatsApp was sent
- `whatsapp_message_sid`: Twilio message ID
- `whatsapp_sent_at`: When it was sent

View these in the Django admin or through the API.

---

## 💰 Costs

- **Sandbox:** FREE (for testing)
- **Production:** ~$0.005-$0.01 per message
- **Free Trial:** Twilio provides trial credits

---

## 📚 Full Documentation

See `WHATSAPP_SETUP_GUIDE.md` for complete details, advanced features, and production setup.

---

**Need help?** Check the Django logs or Twilio Console for detailed error messages.
