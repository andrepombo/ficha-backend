# WhatsApp Opt-in Implementation Guide

## Overview

This system implements explicit opt-in consent for WhatsApp notifications, complying with Meta's WhatsApp Business Platform requirements and LGPD.

## How It Works

### 1. Candidate Application Flow

When candidates fill out the application form, they see a checkbox:

"Aceito receber notificações sobre entrevistas via WhatsApp"

- Checkbox is optional
- Clear disclosure of what messages they'll receive
- Timestamp recorded when they opt in

### 2. Message Sending Logic

When an interview is created/updated:
1. System checks if candidate.whatsapp_opt_in == True
2. If YES: Sends WhatsApp message
3. If NO: Skips WhatsApp, logs the reason

### 3. Database Fields

- whatsapp_opt_in (Boolean) - Whether candidate agreed
- whatsapp_opt_in_date (DateTime) - When they opted in
- whatsapp_phone (String) - Verified phone format

## For Administrators

### Manually Enable Opt-in

```bash
cd /home/lock221/pinte_fichas/ficha-backend
source venv/bin/activate
python enable_whatsapp_optin.py
```

### Check Opt-in Status

In Django Admin or via shell:
```python
from apps.candidate.models import Candidate
opted_in = Candidate.objects.filter(whatsapp_opt_in=True).count()
```

## Meta WhatsApp Requirements

### Why Opt-in is Required

Meta's WhatsApp Business Platform requires:
1. Explicit opt-in from recipients
2. Pre-approved message templates
3. Clear disclosure of message types

Error #133010 means recipient hasn't opted in or number isn't registered.

## Testing

1. Enable opt-in for a test candidate
2. Create/update an interview
3. Check logs for WhatsApp send attempt

## Compliance

- Explicit consent via checkbox
- Purpose limitation (interview notifications only)
- Audit trail (timestamp of consent)
- Right to withdraw (can opt-out anytime)

## Summary

- Checkbox added to application form
- Opt-in required before sending WhatsApp
- Complies with Meta and LGPD requirements
- Admin tools available for manual opt-in management
