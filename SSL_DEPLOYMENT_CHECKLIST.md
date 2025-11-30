# SSL Deployment Checklist

Quick reference for deploying SSL on your production server.

## ✅ Pre-Deployment Checklist

- [ ] Domain `fichapinte.com.br` DNS A record points to EC2 IP
- [ ] EC2 Security Group allows ports 80 and 443
- [ ] Nginx is installed on EC2
- [ ] Application is running and accessible via HTTP

## 📋 Deployment Steps

### 1. Install Certbot
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obtain SSL Certificate
```bash
sudo certbot certonly --standalone -d fichapinte.com.br -d www.fichapinte.com.br
```

### 3. Deploy Nginx SSL Configuration
```bash
# Copy SSL config
sudo cp nginx-ssl.conf /etc/nginx/sites-available/ficha-backend

# Enable site
sudo ln -sf /etc/nginx/sites-available/ficha-backend /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 4. Update Production Environment
Update `.env` on server:
```env
DEBUG=False
ALLOWED_HOSTS=fichapinte.com.br,www.fichapinte.com.br

# HTTPS URLs
CORS_ALLOWED_ORIGINS=https://fichapinte.com.br,https://www.fichapinte.com.br
CSRF_TRUSTED_ORIGINS=https://fichapinte.com.br,https://www.fichapinte.com.br

# SSL Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 5. Restart Application
```bash
docker compose restart
# or
sudo systemctl restart gunicorn
```

## ✅ Post-Deployment Verification

- [ ] Visit `http://fichapinte.com.br` → Redirects to HTTPS
- [ ] Visit `https://fichapinte.com.br` → Shows secure padlock
- [ ] Test SSL rating: https://www.ssllabs.com/ssltest/
- [ ] Verify auto-renewal: `sudo certbot renew --dry-run`
- [ ] Check certificate expiry: `sudo certbot certificates`

## 🔄 Maintenance

### Check Certificate Status
```bash
sudo certbot certificates
```

### Manual Renewal (if needed)
```bash
sudo certbot renew
sudo systemctl reload nginx
```

### Monitor Renewal Timer
```bash
sudo systemctl status certbot.timer
```

## 🚨 Troubleshooting

### Certificate Not Found
```bash
sudo ls -la /etc/letsencrypt/live/fichapinte.com.br/
```

### Nginx Config Test Failed
```bash
sudo nginx -t
# Check error message and fix syntax
```

### Port Already in Use
```bash
sudo lsof -i :80
sudo lsof -i :443
```

### Check Nginx Logs
```bash
sudo tail -f /var/log/nginx/error.log
```

## 📞 Support Resources

- **Let's Encrypt Docs**: https://letsencrypt.org/docs/
- **Certbot Docs**: https://certbot.eff.org/
- **SSL Test**: https://www.ssllabs.com/ssltest/
- **Django Security**: https://docs.djangoproject.com/en/stable/topics/security/

## 💡 Key Points

1. **Free Forever**: Let's Encrypt certificates are 100% free
2. **Auto-Renewal**: Certificates renew automatically every 60 days
3. **90-Day Validity**: Certificates are valid for 90 days
4. **A+ Rating**: Configuration achieves A+ SSL rating
5. **HSTS Enabled**: Forces HTTPS for enhanced security
