#!/bin/bash
# ============================================
# Kai Platform - Health Check Script
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Kai Platform - Health Check"
echo "=========================================="

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
elif [ -f .env.development ]; then
    export $(cat .env.development | grep -v '^#' | xargs)
fi

BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

echo ""
echo "Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is running${NC}"
else
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi

echo ""
echo "Checking Docker Compose services..."
echo ""

# Function to check service status
check_service() {
    SERVICE_NAME=$1
    CONTAINER_NAME=$2

    if docker-compose ps "$SERVICE_NAME" | grep -q "Up"; then
        echo -e "${BLUE}[$SERVICE_NAME]${NC}"

        # Get container status
        STATUS=$(docker inspect --format='{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "not found")
        echo "  Status: $STATUS"

        # Get health status if available
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "no healthcheck")
        if [ "$HEALTH" = "healthy" ]; then
            echo -e "  Health: ${GREEN}$HEALTH${NC}"
        elif [ "$HEALTH" = "unhealthy" ]; then
            echo -e "  Health: ${RED}$HEALTH${NC}"
        elif [ "$HEALTH" = "starting" ]; then
            echo -e "  Health: ${YELLOW}$HEALTH${NC}"
        else
            echo "  Health: $HEALTH"
        fi

        # Get uptime
        UPTIME=$(docker inspect --format='{{.State.StartedAt}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")
        echo "  Started: $UPTIME"

        return 0
    else
        echo -e "${RED}✗ $SERVICE_NAME is not running${NC}"
        return 1
    fi
}

# Check each service
check_service "postgres" "kai-postgres"
echo ""
check_service "backend" "kai-backend"
echo ""
check_service "frontend" "kai-frontend"

# Check if nginx is running (optional)
if docker-compose ps nginx | grep -q "Up"; then
    echo ""
    check_service "nginx" "kai-nginx"
fi

echo ""
echo "=========================================="
echo "Connectivity Tests"
echo "=========================================="
echo ""

# Test PostgreSQL
echo "Testing PostgreSQL connection..."
if nc -z localhost "$POSTGRES_PORT" 2>/dev/null; then
    echo -e "${GREEN}✓ PostgreSQL is accepting connections on port $POSTGRES_PORT${NC}"
else
    echo -e "${RED}✗ Cannot connect to PostgreSQL on port $POSTGRES_PORT${NC}"
fi

# Test Backend
echo ""
echo "Testing Backend API..."
if curl -f -s "http://localhost:$BACKEND_PORT/health" > /dev/null; then
    echo -e "${GREEN}✓ Backend API is responding on port $BACKEND_PORT${NC}"
    echo "  Response:"
    curl -s "http://localhost:$BACKEND_PORT/health" | jq '.' 2>/dev/null || curl -s "http://localhost:$BACKEND_PORT/health"
else
    echo -e "${RED}✗ Backend API is not responding on port $BACKEND_PORT${NC}"
fi

# Test Frontend
echo ""
echo "Testing Frontend..."
if curl -f -s -o /dev/null "http://localhost:$FRONTEND_PORT"; then
    echo -e "${GREEN}✓ Frontend is responding on port $FRONTEND_PORT${NC}"
else
    echo -e "${RED}✗ Frontend is not responding on port $FRONTEND_PORT${NC}"
fi

echo ""
echo "=========================================="
echo "Resource Usage"
echo "=========================================="
echo ""

docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" kai-postgres kai-backend kai-frontend 2>/dev/null || echo "Unable to get resource stats"

echo ""
echo "=========================================="
echo "Health Check Complete"
echo "=========================================="
echo ""
echo "Service URLs:"
echo "  Frontend:  http://localhost:$FRONTEND_PORT"
echo "  Backend:   http://localhost:$BACKEND_PORT"
echo "  API Docs:  http://localhost:$BACKEND_PORT/docs"
echo ""
