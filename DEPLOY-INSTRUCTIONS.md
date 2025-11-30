# Deployment Instructions

## Prerequisites

1. **GitHub Secrets** - Add these to your repository settings:
   - `EC2_HOST`: Your EC2 public IP address
   - `EC2_SSH_USER`: `ubuntu` (default for Ubuntu EC2)
   - `EC2_SSH_KEY`: Your private SSH key content

## Step 1: Create EC2 Instance with Terraform

```bash
cd /home/lock221/pinte_fichas/terraform
terraform init
terraform apply
```

**What this creates:**
- ✅ EC2 instance (Ubuntu 22.04)
- ✅ Docker & Docker Compose installed
- ✅ Security group (ports: 22, 80, 443, 8000, 9000, 9443)
- ✅ Nginx installed
- ✅ Elastic IP

**Save the EC2 IP address from the output!**

## Step 2: Configure GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add the three secrets listed above

## Step 3: Deploy Backend

**Option A: Automatic (Recommended)**
- Push to `main` branch - GitHub Actions will automatically deploy!

**Option B: Manual**
- Go to Actions tab → "Deploy Backend to EC2" → Run workflow

## Step 4: Configure Nginx (One-time setup)

SSH into your EC2 and run:

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Copy nginx config
sudo cp ~/ficha-backend/nginx-docker.conf /etc/nginx/sites-available/ficha-backend

# Enable site
sudo ln -s /etc/nginx/sites-available/ficha-backend /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart
sudo nginx -t
sudo systemctl restart nginx
```

## Done!

Your application will be accessible at:
- **Port 8000**: `http://YOUR_EC2_IP:8000` (direct to Docker)
- **Port 80**: `http://YOUR_EC2_IP` (through Nginx)

## Useful Commands

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# View container logs
cd ~/ficha-backend
sudo docker-compose logs -f backend

# Restart containers
sudo docker-compose restart

# Rebuild containers
sudo docker-compose up -d --build

# Run migrations
sudo docker-compose exec backend python manage.py migrate

# Create superuser
sudo docker-compose exec backend python manage.py createsuperuser
```

## Troubleshooting

### Deployment fails
- Check GitHub Actions logs
- Verify secrets are correctly set
- Ensure EC2 security group allows SSH (port 22)

### Application not accessible
- Check if containers are running: `sudo docker-compose ps`
- Check logs: `sudo docker-compose logs backend`
- Verify security group allows port 8000 and 80

### Nginx 502 error
- Check if Docker container is running on port 8000
- Test direct access: `curl http://localhost:8000`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
