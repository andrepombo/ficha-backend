# Meta WhatsApp Message Templates Setup Guide

## Overview

You need to create message templates in your Meta WhatsApp Business Account to send notifications to candidates about interviews.

**Your WABA ID**: `1118327627052553`  
**Phone Number**: `+55 85 9613-4133`

---

## Required Templates

Based on your application, you need these 3 templates:

1. **interview_scheduled** - When an interview is scheduled
2. **interview_rescheduled** - When an interview is rescheduled
3. **interview_cancelled** - When an interview is cancelled

---

## How to Create Templates

### Step 1: Access Message Templates

Go to one of these URLs:

- **Option A**: https://business.facebook.com/wa/manage/message-templates/
- **Option B**: https://developers.facebook.com/apps/1227723822737406/whatsapp-business/wa-message-templates/

Make sure you select WABA ID: **1118327627052553**

### Step 2: Create Each Template

Click **"Create Template"** and fill in the details for each template below.

---

## Template 1: Interview Scheduled

### Basic Information
- **Template Name**: `interview_scheduled`
- **Category**: `UTILITY`
- **Language**: `Portuguese (BR)` / `pt_BR`

### Header (Optional)
- Type: **Text**
- Content: `📅 Entrevista Agendada`

### Body
```
Olá {{1}}!

Sua entrevista foi agendada com sucesso.

📅 Data: {{2}}
🕐 Horário: {{3}}
📍 Local: {{4}}

Por favor, confirme sua presença respondendo esta mensagem.

Boa sorte!
```

### Footer (Optional)
```
Pinte Pinturas - Recrutamento
```

### Buttons (Optional)
- **Quick Reply**: `Confirmar Presença`
- **Quick Reply**: `Reagendar`

### Variables Explanation
- `{{1}}` = Candidate name
- `{{2}}` = Interview date
- `{{3}}` = Interview time
- `{{4}}` = Interview location

---

## Template 2: Interview Rescheduled

### Basic Information
- **Template Name**: `interview_rescheduled`
- **Category**: `UTILITY`
- **Language**: `Portuguese (BR)` / `pt_BR`

### Header (Optional)
- Type: **Text**
- Content: `🔄 Entrevista Reagendada`

### Body
```
Olá {{1}}!

Sua entrevista foi reagendada.

📅 Nova Data: {{2}}
🕐 Novo Horário: {{3}}
📍 Local: {{4}}

Por favor, confirme sua presença na nova data.

Qualquer dúvida, entre em contato.
```

### Footer (Optional)
```
Pinte Pinturas - Recrutamento
```

### Buttons (Optional)
- **Quick Reply**: `Confirmar Nova Data`
- **Quick Reply**: `Cancelar`

### Variables Explanation
- `{{1}}` = Candidate name
- `{{2}}` = New interview date
- `{{3}}` = New interview time
- `{{4}}` = Interview location

---

## Template 3: Interview Cancelled

### Basic Information
- **Template Name**: `interview_cancelled`
- **Category**: `UTILITY`
- **Language**: `Portuguese (BR)` / `pt_BR`

### Header (Optional)
- Type: **Text**
- Content: `❌ Entrevista Cancelada`

### Body
```
Olá {{1}}!

Informamos que sua entrevista agendada para {{2}} às {{3}} foi cancelada.

{{4}}

Agradecemos seu interesse e desejamos sucesso em sua jornada profissional.
```

### Footer (Optional)
```
Pinte Pinturas - Recrutamento
```

### Variables Explanation
- `{{1}}` = Candidate name
- `{{2}}` = Interview date
- `{{3}}` = Interview time
- `{{4}}` = Cancellation reason (optional message)

---

## Step 3: Submit for Approval

After creating each template:

1. Click **"Submit"**
2. Meta will review it (usually takes **a few minutes to 24 hours**)
3. You'll receive a notification when approved
4. Status will change from `PENDING` → `APPROVED`

---

## Step 4: Update Your Code

Once templates are approved, update your `.env` file:

### Local Development (.env)
```bash
# Meta Template Names (must match exactly what you created)
META_TEMPLATE_SCHEDULED=interview_scheduled
META_TEMPLATE_RESCHEDULED=interview_rescheduled
META_TEMPLATE_CANCELLED=interview_cancelled
```

### Production (.env on EC2)
```bash
# SSH into your server
ssh ubuntu@18.216.12.96

# Edit .env
cd /home/ubuntu/ficha-backend
nano .env

# Add these lines (or update existing ones):
META_TEMPLATE_SCHEDULED=interview_scheduled
META_TEMPLATE_RESCHEDULED=interview_rescheduled
META_TEMPLATE_CANCELLED=interview_cancelled

# Save and restart Docker
docker compose down
docker compose up -d
```

---

## Step 5: Test Your Templates

After templates are approved, test them:

```bash
# On your local machine or EC2
cd /home/lock221/pinte_fichas/ficha-backend

# Test sending a template message
python3 test_meta_whatsapp.py
```

---

## Template Design Tips

### ✅ Best Practices

1. **Keep it concise** - WhatsApp users prefer short messages
2. **Use emojis** - Makes messages more friendly and readable
3. **Clear call-to-action** - Tell users what to do next
4. **Professional tone** - Maintain brand voice
5. **Variables** - Use {{1}}, {{2}}, etc. for dynamic content

### ❌ What to Avoid

1. **Marketing content** - Templates are for UTILITY, not promotions
2. **Too many variables** - Keep it simple (max 3-4 variables)
3. **Spelling errors** - Templates can't be edited after approval
4. **Sensitive data** - Don't include passwords or sensitive info

---

## Template Approval Timeline

- **Typical approval time**: 15 minutes to 24 hours
- **Rejection reasons**: 
  - Marketing content in UTILITY category
  - Spelling/grammar errors
  - Policy violations
  - Too many variables

If rejected, you'll see the reason and can resubmit with corrections.

---

## Checking Template Status

### Via Meta Business Suite
1. Go to: https://business.facebook.com/wa/manage/message-templates/
2. Check the **Status** column for each template

### Via API (using your script)
```bash
cd /home/lock221/pinte_fichas/ficha-backend
python3 check_meta_templates.py
# Enter WABA ID: 1118327627052553
```

---

## Troubleshooting

### Template Not Showing Up
- Wait 5-10 minutes after creation
- Refresh the page
- Check you're viewing the correct WABA

### Template Rejected
- Read the rejection reason carefully
- Fix the issue
- Create a new template (you can't edit rejected ones)
- Resubmit

### Can't Send Template Messages
- Verify template status is `APPROVED`
- Check template name matches exactly in `.env`
- Ensure recipient has messaged you first (for first message)
- Check your access token is valid

---

## Alternative: Simpler Templates

If you want to start with simpler templates (faster approval), use these:

### Simple Interview Scheduled
```
Olá {{1}}!

Sua entrevista foi agendada para {{2}} às {{3}}.

Local: {{4}}

Confirme sua presença.
```

### Simple Interview Cancelled
```
Olá {{1}}!

Sua entrevista de {{2}} foi cancelada.

Obrigado pelo interesse.
```

These are more likely to be approved quickly since they're straightforward.

---

## Next Steps After Templates Are Approved

1. ✅ Update `.env` files (local and production)
2. ✅ Restart your application
3. ✅ Test sending messages
4. ✅ Monitor delivery in Meta Business Suite
5. ✅ Check webhook logs for incoming messages

---

## Support Resources

- **Meta Business Help**: https://www.facebook.com/business/help
- **WhatsApp Business API Docs**: https://developers.facebook.com/docs/whatsapp
- **Template Guidelines**: https://developers.facebook.com/docs/whatsapp/message-templates/guidelines

---

## Summary Checklist

- [ ] Access Meta Business Suite message templates
- [ ] Create `interview_scheduled` template
- [ ] Create `interview_rescheduled` template
- [ ] Create `interview_cancelled` template
- [ ] Wait for approval (check status)
- [ ] Update `.env` with template names
- [ ] Restart application
- [ ] Test sending messages
- [ ] Verify delivery

**Once all templates are approved, your WhatsApp integration will be fully functional!** 🎉
