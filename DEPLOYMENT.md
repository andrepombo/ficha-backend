# Deployment Guide - Pinte Fichas Backend

## Prerequisites
- AWS account with EC2 access
- Terraform installed locally
- GitHub repository secrets configured

## Step 1: Create EC2 Instance with Terraform

```bash
cd /home/lock221/pinte_fichas/terraform
terraform init
terraform plan
terraform apply
```

This will create:
- EC2 instance with Ubuntu 22.04
- Docker and Docker Compose pre-installed
- Security group with ports: 22, 80, 443, 8000, 9000, 9443
- Elastic IP
- Nginx installed

**Note the EC2 public IP from the Terraform output!**

## Step 2: SSH into EC2 and Run Initial Setup

```bash
# SSH into your EC2 instance
ssh -i /path/to/your-key.pem ubuntu@YOUR_EC2_IP

# Run the setup script
cd /var/www/pinte-fichas
git clone https://github.com/pintepinturasdev/ficha-backend.git backend
cd backend

# Create .env file with your secrets
nano .env
```

### Required .env Variables:
```env
DEBUG=False
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=fichapinte.com.br,YOUR_EC2_IP
CORS_ALLOWED_ORIGINS=http://fichapinte.com.br,https://fichapinte.com.br

# Add any database credentials if using external DB
```

## Step 3: Build and Start Docker Containers

```bash
# Build containers
docker compose build

# Start containers
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f backend
```

Your application should now be running at `http://YOUR_EC2_IP:8000`

## Step 4: Configure Nginx

```bash
# Copy Nginx configuration
sudo cp nginx-docker.conf /etc/nginx/sites-available/ficha-backend

# Enable the site
sudo ln -s /etc/nginx/sites-available/ficha-backend /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

Your application should now be accessible at `http://YOUR_EC2_IP` (port 80)

## Step 5: Configure GitHub Secrets

Add these secrets to your GitHub repository:
- `EC2_HOST`: Your EC2 public IP
- `EC2_USERNAME`: `ubuntu`
- `EC2_SSH_KEY`: Your private SSH key content

## Step 6: Test Deployment

Push a change to the `main` branch - the GitHub Actions workflow will automatically deploy!

## Useful Commands

```bash
# View logs
docker compose logs -f backend

# Restart containers
docker compose restart

# Rebuild containers
docker compose up -d --build

# Stop containers
docker compose down

# Run migrations
docker compose exec backend python manage.py migrate

# Create superuser
docker compose exec backend python manage.py createsuperuser

# Collect static files
docker compose exec backend python manage.py collectstatic
```

## Troubleshooting

### Container won't start
```bash
docker compose logs backend
```

### Database migrations needed
```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

### Port 8000 already in use
```bash
sudo lsof -i :8000
# Kill the process or change the port in docker-compose.yml
```

## Optional: Install Portainer

```bash
docker volume create portainer_data

docker run -d \
  -p 9000:9000 \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

Access Portainer at `http://YOUR_EC2_IP:9000`
