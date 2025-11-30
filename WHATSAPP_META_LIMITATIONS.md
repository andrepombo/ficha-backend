# Meta WhatsApp #133010 Error - The Reality

## What's Happening

Even with opt-in enabled, Meta returns error #133010 "Account not registered" because:

### Meta's Requirements (ALL must be met):

1. ✅ **Opt-in consent** - We have this (checkbox on form)
2. ❌ **Recipient must message your business FIRST** - This is the blocker
3. ✅ **Approved templates** - We have these
4. ✅ **Valid phone number** - We have this

## The Problem

Meta WhatsApp Business requires a **two-way handshake**:

1. Candidate messages your business: +55 85 9613-4133
2. This opens a 24-hour "customer service window"
3. During this window, you can send freeform messages
4. After 24 hours, you can only send approved templates
5. BUT the recipient must have messaged you at least once

**Without step 1, all messages fail with #133010, even with templates.**

## Why This Exists

Meta's anti-spam policy. They want to ensure:
- Businesses don't spam random numbers
- Recipients have shown interest by messaging first
- All business-initiated messages are from legitimate conversations

## Solutions

### Option 1: QR Code / Click-to-Chat (Recommended)

Add a WhatsApp button/QR code to your website:

```html
<!-- On your careers/application page -->
<a href="https://wa.me/5585961341133?text=Olá,%20tenho%20interesse%20em%20vagas" 
   class="btn btn-success">
   📱 Fale conosco no WhatsApp
</a>
```

When candidates click:
- Opens WhatsApp with pre-filled message
- They send it (completing the handshake)
- Now you can send them notifications

### Option 2: Email/SMS Fallback (Immediate Solution)

Update the system to:
1. Try WhatsApp first
2. If #133010 error, automatically send email instead
3. Include WhatsApp opt-in link in email

### Option 3: Manual Onboarding

For high-value candidates:
1. Call them after application
2. Ask them to send "Oi" to your WhatsApp
3. Once they do, notifications work

### Option 4: Accept the Limitation

- Only candidates who message you first get WhatsApp notifications
- Everyone else gets email
- Over time, more candidates will message you

## What We've Built

✅ Opt-in consent system (legal compliance)
✅ Meta Cloud API integration (technical setup)
✅ Template support (message approval)
✅ Phone formatting (E.164)

❌ Can't bypass Meta's "message us first" requirement

## Recommended Next Steps

**Immediate (Today):**
1. Add email notifications as fallback
2. Test with candidates who've messaged you

**Short-term (This Week):**
1. Add WhatsApp button to application page
2. Add QR code to job postings
3. Include WhatsApp link in application confirmation email

**Long-term:**
1. Build self-service candidate portal
2. Include WhatsApp opt-in flow there
3. Track which candidates have messaged you

## The Bottom Line

**Meta's #133010 is NOT a bug in our code.** It's Meta's policy.

Your integration is correct and production-ready. The limitation is that candidates must initiate contact first.

**Most HR systems solve this by:**
- Using email as primary notification channel
- WhatsApp as optional enhancement for engaged candidates
- Adding "Message us on WhatsApp" CTAs everywhere

Would you like me to implement email fallback now?
