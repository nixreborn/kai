#!/bin/bash
# ============================================
# Kai Platform - Development Startup Script
# ============================================

set -e

echo "=========================================="
echo "Starting Kai Platform - Development Mode"
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

# Check if .env.development exists
if [ ! -f .env.development ]; then
    echo -e "${YELLOW}Warning: .env.development not found. Using .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env.development
        echo -e "${GREEN}Created .env.development from .env.example${NC}"
    else
        echo -e "${RED}Error: Neither .env.development nor .env.example found!${NC}"
        exit 1
    fi
fi

# Use development environment
export $(cat .env.development | grep -v '^#' | xargs)

echo ""
echo "Stopping any existing containers..."
docker-compose down

echo ""
echo "Building Docker images..."
docker-compose build --no-cache

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check service health
echo ""
echo "Checking service health..."

# Check PostgreSQL
if docker-compose ps postgres | grep -q "healthy"; then
    echo -e "${GREEN}✓ PostgreSQL is healthy${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL is starting...${NC}"
fi

# Check Backend
if docker-compose ps backend | grep -q "healthy"; then
    echo -e "${GREEN}✓ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Backend is starting...${NC}"
fi

# Check Frontend
if docker-compose ps frontend | grep -q "healthy"; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Frontend is starting...${NC}"
fi

echo ""
echo "=========================================="
echo "Kai Platform is starting up!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - Frontend:  http://localhost:${FRONTEND_PORT:-3000}"
echo "  - Backend:   http://localhost:${BACKEND_PORT:-8000}"
echo "  - API Docs:  http://localhost:${BACKEND_PORT:-8000}/docs"
echo "  - PostgreSQL: localhost:${POSTGRES_PORT:-5432}"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To view logs for a specific service:"
echo "  docker-compose logs -f [backend|frontend|postgres]"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
echo ""
echo "=========================================="
