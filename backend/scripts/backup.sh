#!/bin/bash
# MedFind — Database Backup Script
# Usage: bash backup.sh
# Schedule with cron: 0 2 * * * /path/to/backup.sh

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "Starting MedFind backup — $DATE"

# PostgreSQL backup
if [ -n "$DB_NAME" ]; then
  PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "${DB_HOST:-127.0.0.1}" \
    -U "${DB_USER:-medfind_user}" \
    "$DB_NAME" > "$BACKUP_DIR/postgres_${DATE}.sql"
  echo "PostgreSQL backup saved: postgres_${DATE}.sql"
fi

# MongoDB backup
if [ -n "$MONGODB_NAME" ]; then
  mongodump \
    --uri="${MONGODB_URI:-mongodb://127.0.0.1:27017}" \
    --db="$MONGODB_NAME" \
    --out="$BACKUP_DIR/mongo_${DATE}/"
  echo "MongoDB backup saved: mongo_${DATE}/"
fi

# Compress everything
tar -czf "$BACKUP_DIR/medfind_backup_${DATE}.tar.gz" \
  "$BACKUP_DIR/postgres_${DATE}.sql" \
  "$BACKUP_DIR/mongo_${DATE}/" 2>/dev/null

echo "Archive ready: medfind_backup_${DATE}.tar.gz"
echo "Backup complete!"
