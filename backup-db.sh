#!/bin/bash

# Database Backup Script
# Run this on EC2 to backup the database

BACKUP_DIR="/var/backups/pinte-fichas"
DB_PATH="/var/www/pinte-fichas/backend/db.sqlite3"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_$DATE.sqlite3"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Check if database exists
if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database file not found at $DB_PATH"
    exit 1
fi

# Create backup
echo "Creating backup: $BACKUP_FILE"
cp $DB_PATH $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE
echo "Backup compressed: ${BACKUP_FILE}.gz"

# Keep only last 7 days of backups
echo "Cleaning old backups (keeping last 7 days)..."
find $BACKUP_DIR -name "db_*.sqlite3.gz" -mtime +7 -delete

# List current backups
echo ""
echo "Current backups:"
ls -lh $BACKUP_DIR

echo ""
echo "Backup completed successfully!"
