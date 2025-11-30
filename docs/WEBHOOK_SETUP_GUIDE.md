# WhatsApp Webhook Setup Guide

## Why You Need Webhooks

Without webhooks, when someone sends "Hi" to your WhatsApp business number:
- ✅ Meta receives the message
- ❌ Your system doesn't know about it
- ❌ The conversation isn't "activated" for API purposes
- ❌ You get #133010 error when trying to send messages

**With webhooks configured:**
- ✅ Meta notifies your system of incoming messages
- ✅ Conversations are properly activated
- ✅ You can send messages to people who messaged you
- ✅ No more #133010 errors

## Prerequisites

Your webhook URL must be:
1. **Publicly accessible** (not localhost)
2. **HTTPS** (SSL certificate required)
3. **Responds within 20 seconds**

### Option 1: If you have a public domain (e.g., api.pintepinturas.com)
Use: `https://api.pintepinturas.com/webhooks/whatsapp/`

### Option 2: If running locally, use ngrok for testing
```bash
# Install ngrok
# Download from: https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000

# You'll get a URL like: https://abc123.ngrok.io
# Your webhook URL: https://abc123.ngrok.io/webhooks/whatsapp/
```

## Setup Steps

### 1. Generate Verify Token

```bash
# Generate a random secure token
openssl rand -hex 32
```

Copy the output (e.g., `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

### 2. Add to .env File

```bash
# Add this line to your .env file
META_WEBHOOK_VERIFY_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### 3. Restart Django Server

```bash
# Stop your server (Ctrl+C)
# Then restart
python manage.py runserver 0.0.0.0:8000
```

### 4. Configure in Meta Developer Console

1. Go to **https://developers.facebook.com/apps**

2. Select your app (ID: 1227723822737406)

3. In left menu, click **WhatsApp → Configuration**

4. Find the **Webhook** section

5. Click **Edit** or **Configure Webhooks**

6. Enter:
   - **Callback URL**: `https://your-domain.com/webhooks/whatsapp/`
     (or your ngrok URL if testing)
   
   - **Verify Token**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`
     (the same token you put in .env)

7. Click **Verify and Save**

8. If successful, you'll see "Webhook verified"

9. **Subscribe to webhook fields**:
   - Check ✅ **messages**
   - Check ✅ **message_status** (optional, for delivery tracking)

10. Click **Save**

### 5. Test the Webhook

1. Send a message from your phone to +55 85 9613-4133

2. Check Django logs:
```bash
# You should see:
[INFO] Webhook received: {...}
[INFO] Received message from 558588806269, type: text
[INFO] Text message: Hi
[INFO] Message from 558588806269 registered. They can now receive notifications.
```

3. Now try sending a notification:
```bash
python test_andre.py
```

4. Should work! ✅

## Troubleshooting

### "Webhook verification failed"

**Cause**: Verify token mismatch or URL not accessible

**Fix**:
- Check token in .env matches token in Meta console
- Verify URL is publicly accessible (try opening in browser)
- Check Django server is running
- Check firewall/security groups allow HTTPS traffic

### "Callback URL must be HTTPS"

**Cause**: Using HTTP instead of HTTPS

**Fix**:
- Use ngrok for local testing (provides HTTPS)
- Or deploy to a server with SSL certificate
- Or use services like Heroku, Railway, Render (provide HTTPS)

### "Connection timeout"

**Cause**: Server not responding fast enough

**Fix**:
- Check Django server is running
- Check no errors in Django logs
- Verify firewall allows incoming connections

### Still getting #133010 after webhook setup

**Cause**: Old messages don't count, need new message after webhook configured

**Fix**:
- Send a NEW message from your phone after webhook is configured
- Wait 1-2 minutes for Meta to process
- Then try sending notification

## Production Deployment

For production, you need:

1. **Domain with SSL**:
   - Buy domain (e.g., api.pintepinturas.com)
   - Get SSL certificate (Let's Encrypt is free)
   - Point domain to your server

2. **Deploy Django**:
   - Use Gunicorn + Nginx
   - Or use platform like Railway, Render, Heroku
   - Ensure webhook URL is accessible

3. **Update Meta Console**:
   - Change webhook URL to production domain
   - Re-verify webhook

## Webhook URL Format

Your webhook will be accessible at:
```
https://YOUR_DOMAIN/webhooks/whatsapp/
```

Examples:
- Production: `https://api.pintepinturas.com/webhooks/whatsapp/`
- Staging: `https://staging.pintepinturas.com/webhooks/whatsapp/`
- Local (ngrok): `https://abc123.ngrok.io/webhooks/whatsapp/`

## What the Webhook Receives

When someone messages you:
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "558588806269",
          "type": "text",
          "text": {"body": "Hi"},
          "timestamp": "1234567890"
        }]
      }
    }]
  }]
}
```

When message status changes:
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "statuses": [{
          "id": "wamid.xxx",
          "status": "delivered",
          "timestamp": "1234567890",
          "recipient_id": "558588806269"
        }]
      }
    }]
  }]
}
```

## Next Steps

Once webhooks are working:
1. Messages from candidates will activate conversations
2. #133010 errors will disappear
3. Notifications will send successfully
4. You can track delivery status

## Summary

✅ Webhook endpoint created: `/webhooks/whatsapp/`
✅ Handles verification and incoming messages
✅ Logs all activity for debugging
✅ Ready for Meta configuration

**Configure it in Meta Developer Console and test!**
