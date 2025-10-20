#!/bin/bash
# ============================================
# Kai Platform - Database Backup Script
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

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
echo "Kai Platform - Database Backup"
echo "=========================================="

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/kai_db_backup_$TIMESTAMP.sql"

echo ""
echo "Backing up database to: $BACKUP_FILE"

# Check if postgres container is running
if ! docker-compose ps postgres | grep -q "Up"; then
    echo -e "${RED}Error: PostgreSQL container is not running!${NC}"
    echo "Start it with: docker-compose up -d postgres"
    exit 1
fi

# Perform backup
if docker-compose exec -T postgres pg_dump -U "${POSTGRES_USER:-kai}" -d "${POSTGRES_DB:-kai_db}" > "$BACKUP_FILE"; then
    echo -e "${GREEN}✓ Database backup completed successfully!${NC}"

    # Compress backup
    gzip "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup compressed to: ${BACKUP_FILE}.gz${NC}"

    # Get file size
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo ""
    echo "Backup details:"
    echo "  File: ${BACKUP_FILE}.gz"
    echo "  Size: $SIZE"
    echo "  Time: $TIMESTAMP"

    # Clean up old backups (keep last 7 days)
    echo ""
    echo "Cleaning up old backups (keeping last 7 days)..."
    find "$BACKUP_DIR" -name "kai_db_backup_*.sql.gz" -mtime +7 -delete
    echo -e "${GREEN}✓ Cleanup completed${NC}"
else
    echo -e "${RED}✗ Database backup failed!${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "Backup completed successfully!"
echo "=========================================="
