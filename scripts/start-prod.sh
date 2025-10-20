#!/bin/bash
# ============================================
# Kai Platform - Production Startup Script
# ============================================

set -e

echo "=========================================="
echo "Starting Kai Platform - Production Mode"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${RED}Error: .env.production not found!${NC}"
    echo "Please create .env.production from .env.example and configure it properly."
    exit 1
fi

# Check for default passwords in production
if grep -q "CHANGE_ME" .env.production; then
    echo -e "${RED}Error: Found default passwords in .env.production!${NC}"
    echo "Please update all CHANGE_ME values in .env.production before running in production."
    exit 1
fi

# Use production environment
export $(cat .env.production | grep -v '^#' | xargs)

echo ""
echo "WARNING: This will start the application in PRODUCTION mode!"
echo "Press Ctrl+C to cancel or wait 5 seconds to continue..."
sleep 5

echo ""
echo "Stopping any existing containers..."
docker-compose down

echo ""
echo "Building Docker images for production..."
docker-compose build --no-cache

echo ""
echo "Starting services in production mode..."
docker-compose --profile production up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check PostgreSQL
if docker-compose ps postgres | grep -q "healthy"; then
    echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not healthy${NC}"
    echo "Check logs with: docker-compose logs postgres"
fi

# Check Backend
if docker-compose ps backend | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${RED}✗ Backend is not healthy${NC}"
    echo "Check logs with: docker-compose logs backend"
fi

# Check Frontend
if docker-compose ps frontend | grep -q "healthy"; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${RED}✗ Frontend is not healthy${NC}"
    echo "Check logs with: docker-compose logs frontend"
fi

# Check Nginx
if docker-compose ps nginx | grep -q "healthy"; then
    echo -e "${GREEN}✓ Nginx is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Nginx may not be configured or is starting...${NC}"
fi

echo ""
echo "=========================================="
echo "Kai Platform is running in PRODUCTION!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - Frontend:  http://localhost:${FRONTEND_PORT:-3000}"
echo "  - Backend:   http://localhost:${BACKEND_PORT:-8000}"
echo "  - API Docs:  http://localhost:${BACKEND_PORT:-8000}/docs"
echo "  - Nginx:     http://localhost:${NGINX_HTTP_PORT:-80}"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop all services:"
echo "  docker-compose --profile production down"
echo ""
echo "=========================================="
