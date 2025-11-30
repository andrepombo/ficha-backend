#!/bin/bash

# Backend Deployment Script
# Run this on EC2 to deploy/update the backend with Docker

set -e

# Function to handle errors
handle_error() {
    echo "❌ Error on line $1"
    echo "Attempting to start containers anyway..."
    docker compose up -d || docker-compose up -d || true
    exit 1
}

trap 'handle_error $LINENO' ERR

echo "=========================================="
echo "Deploying Backend..."
echo "=========================================="

# Navigate to backend directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Pull latest code (skip if already pulled by CI/CD)
if [ -d .git ]; then
    echo "→ Pulling latest code..."
    git pull || echo "Git pull skipped (may already be up to date)"
fi

# Ensure logo is in media directory
echo "→ Copying logo to media directory..."
sudo mkdir -p media
if [ -f pinte-logo.png ]; then
    sudo cp -f pinte-logo.png media/pinte-logo.png
    echo "   ✓ Logo copied successfully"
else
    echo "   ⚠ Warning: pinte-logo.png not found in root directory"
fi

# Verify logo exists in media
if [ -f media/pinte-logo.png ]; then
    echo "   ✓ Logo verified in media directory"
    ls -lh media/pinte-logo.png
else
    echo "   ✗ Error: Logo not found in media directory!"
fi

# Ensure staticfiles directory exists
sudo mkdir -p staticfiles

# Set proper permissions for Nginx to read files
echo "→ Setting file permissions..."
# Allow Nginx to traverse the home directory
sudo chmod 755 ~ 2>/dev/null || true
sudo chmod 755 . 2>/dev/null || true
# Change ownership of media and staticfiles to current user for Docker build
sudo chown -R $(whoami):$(whoami) media 2>/dev/null || true
sudo chown -R $(whoami):$(whoami) staticfiles 2>/dev/null || true
# Set permissions on media and static directories
sudo chmod -R 755 media 2>/dev/null || true
sudo chmod -R 755 staticfiles 2>/dev/null || true

# Update Nginx configuration
echo "→ Updating Nginx configuration..."
sudo cp nginx-ssl.conf /etc/nginx/sites-available/ficha-backend || echo "Warning: Failed to copy nginx config"
sudo ln -sf /etc/nginx/sites-available/ficha-backend /etc/nginx/sites-enabled/ficha-backend || true
sudo rm -f /etc/nginx/sites-enabled/default || true

# Test Nginx configuration
echo "→ Testing Nginx configuration..."
sudo nginx -t || echo "Warning: Nginx config test failed"

# Reload Nginx
echo "→ Reloading Nginx..."
sudo systemctl reload nginx || echo "Warning: Failed to reload Nginx"

# Stop existing containers
echo "→ Stopping existing containers..."
docker compose down || docker-compose down || true

# Rebuild and restart Docker containers
echo "→ Rebuilding Docker containers..."
docker compose up -d --build || docker-compose up -d --build

# Wait for container to be ready
echo "→ Waiting for container to start..."
sleep 10

# Run migrations inside container
echo "→ Running migrations..."
docker compose exec -T backend python manage.py migrate || docker-compose exec -T backend python manage.py migrate || true

# Collect static files inside container
echo "→ Collecting static files..."
docker compose exec -T backend python manage.py collectstatic --noinput || docker-compose exec -T backend python manage.py collectstatic --noinput || true

# Check status
if docker ps | grep -q ficha-backend; then
    echo "✓ Backend deployed successfully!"
    echo ""
    echo "Container status:"
    docker ps | grep ficha-backend
    echo ""
    echo "Recent logs:"
    docker logs ficha-backend --tail 20
else
    echo "✗ Docker container failed to start"
    echo "Check logs with: docker logs ficha-backend"
    exit 1
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "Your site is now available at:"
echo "  - http://fichapinte.com.br"
echo "  - http://www.fichapinte.com.br"
echo "  - http://18.216.12.96"
echo "=========================================="
