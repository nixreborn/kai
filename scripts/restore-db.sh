#!/bin/bash
# ============================================
# Kai Platform - Database Restore Script
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
BACKUP_DIR="./backups"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
elif [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
elif [ -f .env.development ]; then
    export $(cat .env.development | grep -v '^#' | xargs)
else
    echo -e "${RED}Error: No environment file found!${NC}"
    exit 1
fi

echo "=========================================="
echo "Kai Platform - Database Restore"
echo "=========================================="

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}Error: Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

# List available backups
echo ""
echo "Available backups:"
echo ""
ls -lh "$BACKUP_DIR"/kai_db_backup_*.sql.gz 2>/dev/null || {
    echo -e "${RED}No backup files found in $BACKUP_DIR${NC}"
    exit 1
}

echo ""
read -p "Enter the backup filename to restore (or 'latest' for most recent): " BACKUP_INPUT

if [ "$BACKUP_INPUT" = "latest" ]; then
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/kai_db_backup_*.sql.gz | head -1)
elif [ -f "$BACKUP_DIR/$BACKUP_INPUT" ]; then
    BACKUP_FILE="$BACKUP_DIR/$BACKUP_INPUT"
elif [ -f "$BACKUP_INPUT" ]; then
    BACKUP_FILE="$BACKUP_INPUT"
else
    echo -e "${RED}Error: Backup file not found: $BACKUP_INPUT${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}WARNING: This will REPLACE the current database with the backup!${NC}"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Check if postgres container is running
if ! docker-compose ps postgres | grep -q "Up"; then
    echo -e "${RED}Error: PostgreSQL container is not running!${NC}"
    echo "Start it with: docker-compose up -d postgres"
    exit 1
fi

echo ""
echo "Creating backup of current database before restore..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PRE_RESTORE_BACKUP="$BACKUP_DIR/pre_restore_backup_$TIMESTAMP.sql"
docker-compose exec -T postgres pg_dump -U "${POSTGRES_USER:-kai}" -d "${POSTGRES_DB:-kai_db}" > "$PRE_RESTORE_BACKUP"
gzip "$PRE_RESTORE_BACKUP"
echo -e "${GREEN}✓ Pre-restore backup saved to: ${PRE_RESTORE_BACKUP}.gz${NC}"

echo ""
echo "Restoring database from: $BACKUP_FILE"

# Decompress and restore
if zcat "$BACKUP_FILE" | docker-compose exec -T postgres psql -U "${POSTGRES_USER:-kai}" -d "${POSTGRES_DB:-kai_db}"; then
    echo -e "${GREEN}✓ Database restored successfully!${NC}"
    echo ""
    echo "=========================================="
    echo "Restore completed successfully!"
    echo "=========================================="
    echo ""
    echo "Pre-restore backup saved at:"
    echo "  ${PRE_RESTORE_BACKUP}.gz"
else
    echo -e "${RED}✗ Database restore failed!${NC}"
    echo ""
    echo "Attempting to restore from pre-restore backup..."
    zcat "${PRE_RESTORE_BACKUP}.gz" | docker-compose exec -T postgres psql -U "${POSTGRES_USER:-kai}" -d "${POSTGRES_DB:-kai_db}"
    echo -e "${YELLOW}Restored to pre-restore state${NC}"
    exit 1
fi
