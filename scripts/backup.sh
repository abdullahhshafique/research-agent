#!/bin/bash
# Daily backup script for AI Research Agent
# Add to crontab: 0 2 * * * /path/to/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/ai-research-agent"
PROJECT_DIR="/path/to/ai_research_agent"

mkdir -p $BACKUP_DIR

# Backup SQLite database
cp $PROJECT_DIR/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $PROJECT_DIR media/

# Backup environment
cp $PROJECT_DIR/.env $BACKUP_DIR/env_$DATE

# Keep only last 7 days
find $BACKUP_DIR -name "*.sqlite3" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_*" -mtime +7 -delete

echo "Backup completed: $DATE"