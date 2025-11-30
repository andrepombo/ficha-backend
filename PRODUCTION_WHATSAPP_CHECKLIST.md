# WhatsApp Production Setup Checklist

Complete guide for deploying Twilio WhatsApp to production.

## ✅ Pre-Production Checklist

### 1. Twilio Account Setup
- [ ] Twilio account created and verified
- [ ] Account upgraded from trial (if needed)
- [ ] Payment method added
- [ ] Sufficient account balance

### 2. WhatsApp Business Number
- [ ] WhatsApp Business number requested from Twilio
- [ ] Business profile completed (name, description, website, address)
- [ ] Number approved by Twilio (1-3 business days)
- [ ] Number tested with sandbox first

### 3. Environment Configuration
- [ ] Production `.env` file created
- [ ] `TWILIO_ACCOUNT_SID` set to production value
- [ ] `TWILIO_AUTH_TOKEN` set to production value
- [ ] `TWILIO_WHATSAPP_FROM` set to approved number (e.g., `whatsapp:+5585XXXXXXXX`)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured with your domain
- [ ] `SECRET_KEY` set to strong random value

### 4. Code & Database
- [ ] Latest code deployed to production server
- [ ] Database migrations run (`python manage.py migrate`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Application restarted

### 5. Testing
- [ ] Test message sent to your phone
- [ ] Test interview notification created
- [ ] Verify message received on WhatsApp
- [ ] Check Twilio logs for delivery status
- [ ] Test with different phone formats (8-digit, 9-digit)

## 🚀 Production Deployment Steps

### Step 1: Get WhatsApp Business Number

#### Option A: Request New Number from Twilio

1. Go to https://console.twilio.com/
2. Navigate to **Messaging** → **WhatsApp** → **Senders**
3. Click **"Request to add a new sender"**
4. Choose **"Request a Twilio number with WhatsApp"**
5. Select **Brazil (+55)** and choose a number
6. Complete business profile:
   - **Business name**: Pinte Pinturas
   - **Business description**: [Your company description]
   - **Business website**: [Your website URL]
   - **Business address**: [Your business address]
7. Submit for approval
8. Wait for approval email (1-3 business days)

**Cost**: ~$1-2/month for the number + message costs

#### Option B: Use Existing Business Number

1. **WhatsApp** → **Senders** → **"Use an existing number"**
2. Enter your business phone number
3. Verify via SMS code
4. Complete business profile
5. Submit for approval

### Step 2: Update Production Environment Variables

Create or update `/path/to/ficha-backend/.env`:

```bash
# Twilio WhatsApp - PRODUCTION
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_production_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+5585XXXXXXXX  # Your approved number

# Django Production Settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-ip-address
SECRET_KEY=your_very_long_random_secret_key_here
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Step 3: Deploy to Production Server

#### For VPS (DigitalOcean, AWS, Linode, etc.):

```bash
# SSH into your production server
ssh user@your-server-ip

# Navigate to project directory
cd /path/to/ficha-backend

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Update environment variables
nano .env  # or vim .env
# Paste your production values

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart gunicorn
# or
sudo systemctl restart ficha-backend
# or
sudo supervisorctl restart ficha-backend
```

#### For Platform as a Service (Heroku, Railway, Render, etc.):

1. **Set Environment Variables** in platform dashboard:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_FROM`
   - `DEBUG=False`
   - `SECRET_KEY`

2. **Deploy**:
   ```bash
   git push heroku main
   # or
   git push origin main  # Auto-deploys on Railway/Render
   ```

3. **Run Migrations**:
   ```bash
   heroku run python manage.py migrate
   # or via platform dashboard
   ```

### Step 4: Test Production Setup

#### Test 1: Send Test Message

```bash
# On production server
cd /path/to/ficha-backend
source venv/bin/activate
python test_twilio_whatsapp.py
```

Enter your phone number and verify you receive the message.

#### Test 2: Create Test Interview

1. Log into your production application
2. Create a new interview for a test candidate
3. Set status to "scheduled"
4. Verify candidate receives WhatsApp notification
5. Check Twilio logs: https://console.twilio.com/monitor/logs/messages

#### Test 3: Check Delivery Status

1. Go to Twilio Console → Monitor → Logs → Messaging
2. Find recent messages
3. Verify status is "delivered" (not just "sent")
4. Check for any errors

## 💰 Cost Management

### Message Pricing (Brazil)

- **Conversation-based pricing**: ~$0.0047 per conversation
- **Session window**: 24 hours
- **Multiple messages in 24h**: Count as 1 conversation

### Monthly Cost Estimates

| Interviews/Month | Messages Sent | Estimated Cost |
|-----------------|---------------|----------------|
| 100 | 100 | $0.47 |
| 500 | 500 | $2.35 |
| 1,000 | 1,000 | $4.70 |
| 5,000 | 5,000 | $23.50 |
| 10,000 | 10,000 | $47.00 |

**Plus**: Phone number rental (~$1-2/month)

### Cost Optimization Tips

1. **Batch notifications** when possible
2. **Avoid duplicate sends** (system already handles this)
3. **Use templates** for consistent messages (lower cost)
4. **Monitor failed messages** (you pay for them too)
5. **Set up spending alerts** in Twilio Console

## 📊 Monitoring & Maintenance

### Daily Monitoring

1. **Check Twilio Dashboard**
   - https://console.twilio.com/monitor/logs/messages
   - Look for failed messages
   - Check delivery rates (should be >95%)

2. **Check Application Logs**
   ```bash
   tail -f /var/log/ficha-backend/django.log | grep WhatsApp
   ```

3. **Monitor Costs**
   - Twilio Console → Usage → WhatsApp
   - Set up spending alerts

### Weekly Tasks

- [ ] Review failed messages and reasons
- [ ] Check delivery rates by area code
- [ ] Verify all candidates receiving messages
- [ ] Review and optimize message templates

### Monthly Tasks

- [ ] Review total costs vs budget
- [ ] Analyze message volume trends
- [ ] Update phone number formats if needed
- [ ] Review Twilio account balance

## 🔧 Troubleshooting Production Issues

### Issue: Messages Not Being Delivered

**Symptoms**: Status shows "sent" but not "delivered"

**Possible Causes**:
- Recipient's phone is off
- Recipient blocked your number
- Recipient doesn't have WhatsApp
- Invalid phone number format

**Solution**:
1. Check Twilio logs for specific error codes
2. Verify phone number format is correct
3. Test with your own phone first
4. Check if recipient has WhatsApp installed

### Issue: High Failure Rate

**Symptoms**: Many messages showing "failed" status

**Possible Causes**:
- Invalid phone numbers in database
- Phone numbers not in E.164 format
- Twilio account issue
- Rate limiting

**Solution**:
1. Review failed message error codes in Twilio
2. Validate phone numbers before sending
3. Check Twilio account status
4. Implement exponential backoff for retries

### Issue: Unexpected High Costs

**Symptoms**: Bill higher than expected

**Possible Causes**:
- Duplicate messages being sent
- Failed messages still charged
- International messages (outside Brazil)
- Multiple conversations per candidate

**Solution**:
1. Check for duplicate sends in logs
2. Review message volume in Twilio Console
3. Verify all numbers are Brazilian (+55)
4. Implement deduplication logic

### Issue: Sandbox Number Still Being Used

**Symptoms**: Production using `+14155238886`

**Solution**:
1. Check `.env` file has correct `TWILIO_WHATSAPP_FROM`
2. Restart application after updating `.env`
3. Verify environment variables loaded:
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TWILIO_WHATSAPP_FROM'))"
   ```

## 🔒 Security Best Practices

### Environment Variables

- ✅ Never commit `.env` to Git
- ✅ Use different credentials for dev/staging/production
- ✅ Rotate `TWILIO_AUTH_TOKEN` every 90 days
- ✅ Use strong `SECRET_KEY` (50+ random characters)
- ✅ Set `DEBUG=False` in production

### Access Control

- ✅ Limit Twilio Console access to authorized personnel
- ✅ Use Twilio subaccounts for different environments
- ✅ Enable two-factor authentication on Twilio account
- ✅ Monitor Twilio audit logs regularly

### Data Protection

- ✅ Store phone numbers securely (encrypted at rest)
- ✅ Comply with LGPD/GDPR for candidate data
- ✅ Provide opt-out mechanism for candidates
- ✅ Delete candidate data upon request

## 📱 WhatsApp Business Policy Compliance

### Required Practices

- ✅ **Get consent**: Only send to candidates who applied
- ✅ **Provide value**: Messages must be relevant and useful
- ✅ **Identify sender**: Clearly state "Pinte Pinturas"
- ✅ **Respect preferences**: Honor opt-out requests immediately
- ✅ **Don't spam**: Only send necessary notifications

### Message Guidelines

- ✅ Use professional, respectful language
- ✅ Include company name in messages
- ✅ Provide clear call-to-action
- ✅ Keep messages concise and relevant
- ✅ Don't send marketing unless explicitly opted-in

## 🎯 Post-Deployment Checklist

After deploying to production:

- [ ] Test message sent successfully to your phone
- [ ] Test interview notification end-to-end
- [ ] Verified message received on WhatsApp
- [ ] Checked Twilio logs show "delivered" status
- [ ] Confirmed correct phone number format used (8-digit for area 85)
- [ ] Set up Twilio spending alerts
- [ ] Documented production credentials securely
- [ ] Trained team on new system
- [ ] Created runbook for common issues
- [ ] Set up monitoring/alerting

## 📞 Support Resources

### Twilio Support

- **Documentation**: https://www.twilio.com/docs/whatsapp
- **Support Portal**: https://support.twilio.com/
- **Status Page**: https://status.twilio.com/
- **Community Forum**: https://www.twilio.com/community

### Internal Documentation

- `test_twilio_whatsapp.py` - Test script
- `apps/candidate/whatsapp_service.py` - Service implementation
- Application logs - `/var/log/ficha-backend/`

## 🎉 Success Criteria

Your production WhatsApp integration is successful when:

- ✅ Messages delivered with >95% success rate
- ✅ Candidates receiving notifications within seconds
- ✅ No duplicate messages being sent
- ✅ Costs within budget expectations
- ✅ Zero downtime or service interruptions
- ✅ Positive feedback from candidates
- ✅ Team comfortable managing the system

---

**Status**: Production Ready ✅  
**Last Updated**: 2025-10-24  
**Maintained By**: Pinte Pinturas Dev Team
