#!/bin/bash
# Initial setup script for new EC2 instance
# Run this once after creating the EC2 instance

set -e

echo "=========================================="
echo "Pinte Fichas Backend - Initial Setup"
echo "=========================================="

# Clone repository
echo "→ Cloning repository..."
cd /var/www/pinte-fichas
git clone https://github.com/pintepinturasdev/ficha-backend.git backend
cd backend

# Create .env file (you'll need to fill this with your secrets)
echo "→ Creating .env file template..."
cat > .env << 'EOF'
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,your-ec2-ip

# Database Settings (if using external DB)
# DB_NAME=your_db_name
# DB_USER=your_db_user
# DB_PASSWORD=your_db_password
# DB_HOST=your_db_host
# DB_PORT=5432

# CORS Settings
CORS_ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com
EOF

echo ""
echo "⚠️  IMPORTANT: Edit the .env file with your actual values!"
echo "   Run: nano .env"
echo ""
read -p "Press Enter after you've updated the .env file..."

# Build and start Docker containers
echo "→ Building Docker containers..."
docker compose build

echo "→ Starting containers..."
docker compose up -d

# Wait for startup
echo "→ Waiting for containers to start..."
sleep 30

# Check status
echo "→ Container status:"
docker compose ps

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Your application should be running at:"
echo "  http://$(curl -s ifconfig.me):8000"
echo ""
echo "Next steps:"
echo "1. Configure Nginx to proxy port 80 to port 8000"
echo "2. Set up SSL certificate with certbot"
echo "3. Update DNS to point to this server"
echo ""
