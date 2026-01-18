#!/bin/bash

# Configuration
DB_CONTAINER="postgres"
DB_USER="admin"
DB_NAME="masalfabrikasi"
BACKUP_DIR="./storage/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform backup
echo "Starting backup of $DB_NAME to $FILENAME..."
docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME > $FILENAME

if [ $? -eq 0 ]; then
  echo "✅ Backup successful: $FILENAME"
  # Keep only last 7 days of backups
  find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -exec rm {} \;
else
  echo "❌ Backup failed!"
  exit 1
fi
