# Production Environment Setup Guide

## Problem
`.env` file is gitignored (for security), so it doesn't get deployed to production automatically.

## Solution Options

### ✅ Option 1: Manual Setup (Recommended - Most Secure)

**Do this ONCE on your production server:**

```bash
# 1. SSH into your EC2 server
ssh ubuntu@18.216.12.96

# 2. Navigate to backend directory
cd /home/ubuntu/ficha-backend

# 3. Create .env file
nano .env
```

**Paste this content:**

```bash
# Security
SECRET_KEY=your-super-secret-production-key-change-this
DEBUG=False

# Hosts
ALLOWED_HOSTS=fichapinte.com.br,www.fichapinte.com.br,18.216.12.96

# CORS & CSRF
CORS_ALLOWED_ORIGINS=https://fichapinte.com.br,https://www.fichapinte.com.br
CSRF_TRUSTED_ORIGINS=https://fichapinte.com.br,https://www.fichapinte.com.br

# SSL Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# WhatsApp Meta Configuration
META_PHONE_NUMBER_ID=771225619417898
META_PERMANENT_ACCESS_TOKEN=EAARcm7pWJZC4BP4s5LDoqVvNTRhcJgBfJofZCzV6qDXDrKyyzXqeZBHhZA9ik2ESgQQBGFyTdBQX35W2y5t7dX7bYylOBWO32x5JGdP9KhVJNCpPNGpwb82DZCk2jwnZCIV0WQigquj0jPYsb5iHk22MkhkiPMOP0nzDJUGeuGu66p6Wkrf46oHfvPVZAsgdCDCDYwVrZAxtO0B7ZAewQIgsAilJtisr4mrQ6V0r5Jocp
META_API_VERSION=v20.0
META_BASE_URL=https://graph.facebook.com/v20.0
META_WEBHOOK_VERIFY_TOKEN=pintepinturas_webhook_2025

# WhatsApp Templates (add if you have them configured)
# META_TEMPLATE_SCHEDULED=interview_scheduled
# META_TEMPLATE_REMINDER=interview_reminder
# META_TEMPLATE_CANCELLED=interview_cancelled
```

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

```bash
# 4. Restart Docker to apply changes
docker compose down
docker compose up -d --build

# 5. Verify it's working
docker logs ficha-backend --tail 50
```

**Test the webhook:**
```bash
curl "http://localhost:8000/webhooks/whatsapp/?hub.mode=subscribe&hub.verify_token=pintepinturas_webhook_2025&hub.challenge=test123"
# Should return: test123
```

---

### 🔄 Option 2: Automated via GitHub Secrets

If you want the `.env` file to be created automatically on each deployment:

#### Step 1: Add GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `DJANGO_SECRET_KEY` | Generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| `META_PHONE_NUMBER_ID` | `771225619417898` |
| `META_ACCESS_TOKEN` | Your Meta permanent access token |
| `META_WEBHOOK_VERIFY_TOKEN` | `pintepinturas_webhook_2025` |

#### Step 2: Deploy

The updated `.github/workflows/deploy.yml` will automatically create the `.env` file from these secrets on each deployment.

Just push to main:
```bash
git add .
git commit -m "Update deployment workflow for env management"
git push origin main
```

---

## After Setup: Configure Meta Webhook

Once `.env` is in place and Docker is restarted:

1. Go to **https://developers.facebook.com/apps/1227723822737406**
2. Navigate to **WhatsApp → Configuration**
3. Click **Edit** in the Webhook section
4. Enter:
   - **Callback URL**: `https://fichapinte.com.br/webhooks/whatsapp/`
   - **Verify Token**: `pintepinturas_webhook_2025`
5. Click **Verify and Save**
6. Subscribe to fields:
   - ✅ **messages**
   - ✅ **message_status**

## Troubleshooting

### Webhook verification fails
```bash
# Check if Django is running
docker ps | grep ficha-backend

# Check Django logs
docker logs ficha-backend --tail 100

# Test webhook locally on server
curl "http://localhost:8000/webhooks/whatsapp/?hub.mode=subscribe&hub.verify_token=pintepinturas_webhook_2025&hub.challenge=test123"
```

### Environment variables not loading
```bash
# Check if .env exists
ls -la /home/ubuntu/ficha-backend/.env

# Restart Docker
cd /home/ubuntu/ficha-backend
docker compose down
docker compose up -d --build
```

## Security Notes

- ✅ `.env` is gitignored - never commit it
- ✅ Use GitHub Secrets for sensitive data
- ✅ Rotate access tokens periodically
- ✅ Use strong SECRET_KEY in production
- ✅ Keep DEBUG=False in production
