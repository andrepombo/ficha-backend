# SSL Setup Guide - Pinte Fichas

This guide covers setting up free SSL certificates using Let's Encrypt for your production deployment.

## Prerequisites

- Domain `fichapinte.com.br` pointing to your EC2 instance IP
- Nginx installed and running
- Port 80 and 443 open in EC2 security group

## Step 1: Install Certbot

SSH into your EC2 instance and run:

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

## Step 2: Stop Nginx Temporarily (if running)

```bash
sudo systemctl stop nginx
```

## Step 3: Obtain SSL Certificate

Run Certbot to get your certificate:

```bash
sudo certbot certonly --standalone -d fichapinte.com.br -d www.fichapinte.com.br
```

You'll be prompted to:
1. Enter your email address (for renewal notifications)
2. Agree to Terms of Service
3. Optionally share your email with EFF

The certificates will be saved to:
- Certificate: `/etc/letsencrypt/live/fichapinte.com.br/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/fichapinte.com.br/privkey.pem`

## Step 4: Deploy SSL-Ready Nginx Configuration

Copy the SSL configuration to Nginx:

```bash
# From your project directory
sudo cp nginx-ssl.conf /etc/nginx/sites-available/ficha-backend

# Create symbolic link
sudo ln -sf /etc/nginx/sites-available/ficha-backend /etc/nginx/sites-enabled/

# Remove default site if present
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t
```

## Step 5: Start Nginx

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Step 6: Update Django Settings

Update your `.env` file on the server with HTTPS settings:

```bash
nano /path/to/your/.env
```

Add these lines:

```env
# SSL/HTTPS Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Update CORS and CSRF to use HTTPS
CORS_ALLOWED_ORIGINS=https://fichapinte.com.br,https://www.fichapinte.com.br
CSRF_TRUSTED_ORIGINS=https://fichapinte.com.br,https://www.fichapinte.com.br
```

## Step 7: Update Django Settings Module

Ensure your Django settings read these environment variables. Add to `core/settings.py`:

```python
# SSL/HTTPS Settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False') == 'True'
SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'False') == 'True'
```

## Step 8: Restart Your Application

```bash
# If using Docker
docker compose restart

# If using systemd service
sudo systemctl restart gunicorn
```

## Step 9: Test SSL Configuration

Visit your site:
- `http://fichapinte.com.br` → Should redirect to HTTPS
- `https://fichapinte.com.br` → Should show secure padlock

Test SSL quality:
- https://www.ssllabs.com/ssltest/analyze.html?d=fichapinte.com.br

## Automatic Certificate Renewal

Certbot automatically sets up a cron job or systemd timer for renewal. Test it:

```bash
# Dry run renewal
sudo certbot renew --dry-run
```

Certificates auto-renew when they have 30 days or less remaining.

## Verify Auto-Renewal is Configured

```bash
# Check systemd timer
sudo systemctl status certbot.timer

# Or check cron
sudo crontab -l | grep certbot
```

## Troubleshooting

### Certificate Not Found Error

If Nginx can't find certificates:
```bash
sudo ls -la /etc/letsencrypt/live/fichapinte.com.br/
```

### Port 80 Already in Use

```bash
sudo lsof -i :80
# Stop the service using port 80 before running certbot
```

### DNS Not Pointing to Server

Verify DNS:
```bash
dig fichapinte.com.br
nslookup fichapinte.com.br
```

### Renewal Fails

Check logs:
```bash
sudo journalctl -u certbot.timer
sudo certbot renew --dry-run -v
```

## Manual Renewal (if needed)

```bash
sudo certbot renew
sudo systemctl reload nginx
```

## Certificate Information

View certificate details:
```bash
sudo certbot certificates
```

## Revoke Certificate (if compromised)

```bash
sudo certbot revoke --cert-path /etc/letsencrypt/live/fichapinte.com.br/cert.pem
```

## Alternative: Using Certbot with Nginx Plugin

If you prefer Certbot to automatically configure Nginx:

```bash
sudo certbot --nginx -d fichapinte.com.br -d www.fichapinte.com.br
```

This will:
- Obtain the certificate
- Automatically modify your Nginx config
- Set up HTTP to HTTPS redirect
- Configure SSL parameters

## Security Best Practices

1. **Keep certificates renewed** - Monitor expiration
2. **Use strong ciphers** - Already configured in `nginx-ssl.conf`
3. **Enable HSTS** - Forces HTTPS (configured)
4. **Regular updates** - Keep Nginx and Certbot updated
5. **Monitor logs** - Check for SSL errors

```bash
# Monitor Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Monitor access logs
sudo tail -f /var/log/nginx/access.log
```

## Cost

Let's Encrypt certificates are **100% FREE** and valid for 90 days with automatic renewal.

## Support

- Let's Encrypt: https://letsencrypt.org/docs/
- Certbot: https://certbot.eff.org/
- SSL Test: https://www.ssllabs.com/ssltest/
