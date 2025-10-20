# Performance Optimization Quick Start

This guide will help you get started with the performance optimizations in the Kai platform.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- PostgreSQL 16 (via Docker)
- Redis 7 (via Docker)

## Quick Start with Docker

### 1. Start All Services

```bash
cd /home/nix/projects/kai
docker compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- FastAPI backend on port 8000
- Next.js frontend on port 3000

### 2. Verify Services

```bash
# Check all services are running
docker compose ps

# Test backend health
curl http://localhost:8000/health

# Test detailed health with performance metrics
curl http://localhost:8000/health/detailed
```

### 3. Run Database Migrations

```bash
# Enter backend container
docker compose exec backend bash

# Run migrations to add performance indexes
alembic upgrade head

# Exit container
exit
```

## Local Development Setup

### 1. Install Dependencies

```bash
cd /home/nix/projects/kai/backend

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"
```

### 2. Start Redis Locally

```bash
# Start Redis with Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install and start Redis locally
# Ubuntu/Debian: sudo apt install redis-server
# macOS: brew install redis && brew services start redis
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and update:
# - DATABASE_URL (your PostgreSQL connection)
# - REDIS_URL (default: redis://localhost:6379/0)
# - SECRET_KEY (generate a secure key)
```

### 4. Run Migrations

```bash
# Apply database migrations
alembic upgrade head
```

### 5. Start Development Server

```bash
# Start with auto-reload
uvicorn src.main:app --reload --port 8000
```

## Testing Performance Improvements

### 1. Benchmark Without Cache

```bash
# First request (cache miss)
time curl http://localhost:8000/api/journal/entries?user_id=test-user

# Note the response time
```

### 2. Benchmark With Cache

```bash
# Second request (cache hit)
time curl http://localhost:8000/api/journal/entries?user_id=test-user

# Should be significantly faster
```

### 3. Check Performance Metrics

```bash
curl http://localhost:8000/health/detailed | jq '.performance'
```

### 4. Monitor Redis

```bash
# Connect to Redis CLI
docker compose exec redis redis-cli

# Check cached keys
KEYS *

# Get cache statistics
INFO stats

# Monitor cache operations in real-time
MONITOR
```

## Performance Features Overview

### Redis Caching

Automatically caches:
- User profiles (1 hour TTL)
- Journal entry lists (5 minutes TTL)
- AI responses (24 hours TTL)
- Conversation history (30 minutes TTL)

### Database Optimization

- Indexed columns for fast lookups
- Composite indexes for common queries
- Connection pooling (5 base + 10 overflow)
- Slow query logging (>100ms)

### API Response Optimization

- Gzip compression (responses >500 bytes)
- Pagination (20 items per page by default)
- Response time headers (`X-Response-Time`)
- Performance middleware tracking

### Monitoring

- Endpoint performance metrics
- Slow query logging
- Cache hit/miss tracking
- Health check with metrics

## Common Operations

### Clear All Cache

```bash
# Via Redis CLI
docker compose exec redis redis-cli FLUSHDB

# Or from Python
from src.cache.redis_client import get_redis_client, RedisCache

cache = RedisCache(await get_redis_client())
await cache.client.flushdb()
```

### Clear Specific User Cache

```bash
# Via Redis CLI
docker compose exec redis redis-cli

# Delete user profile
DEL user:profile:USER_ID

# Delete all journal lists for user
SCAN 0 MATCH journal:list:USER_ID:*
# Then delete each key with DEL
```

### View Slow Queries

Check backend logs:

```bash
docker compose logs backend | grep "Slow query"
```

### Check Cache Hit Rate

```bash
curl http://localhost:8000/health/detailed | jq '.redis'
```

## Load Testing

### Using Apache Bench

```bash
# Install
sudo apt install apache2-utils  # Ubuntu/Debian
brew install httpd  # macOS

# Test health endpoint (simple)
ab -n 1000 -c 10 http://localhost:8000/health

# Test journal list endpoint
ab -n 500 -c 20 http://localhost:8000/api/journal/entries?user_id=test
```

### Using wrk

```bash
# Install
sudo apt install wrk  # Ubuntu/Debian
brew install wrk  # macOS

# Test with 12 threads, 400 connections for 30 seconds
wrk -t12 -c400 -d30s http://localhost:8000/health/detailed

# Test specific endpoint
wrk -t4 -c100 -d10s http://localhost:8000/api/journal/entries?user_id=test
```

## Troubleshooting

### Redis Connection Failed

```bash
# Check if Redis is running
docker compose ps redis

# Check Redis logs
docker compose logs redis

# Test connection
docker compose exec redis redis-cli ping
# Should return: PONG
```

### Database Connection Slow

```bash
# Check database health
docker compose exec postgres pg_isready

# Check for slow queries
docker compose logs backend | grep "Slow query"

# Verify indexes are created
docker compose exec postgres psql -U kai -d kai_db -c "\d journal_entries"
```

### Cache Not Working

```bash
# Check Redis is accessible
curl http://localhost:8000/health/detailed | jq '.redis.status'

# Check for cache keys
docker compose exec redis redis-cli KEYS "*"

# Monitor cache operations
docker compose exec redis redis-cli MONITOR
```

### Performance Not Improving

1. Verify migrations are applied: `alembic current`
2. Check database indexes: `\d+ journal_entries` in psql
3. Monitor cache hit rate in `/health/detailed`
4. Review backend logs for errors
5. Check system resources (CPU, memory)

## Production Deployment

### Environment Variables

```bash
# Production .env settings
DEBUG=false
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/kai_db

# Redis connection pool
REDIS_MAX_CONNECTIONS=20

# Database connection pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### Docker Compose Production

```bash
# Build for production
docker compose build --no-cache

# Start in production mode
docker compose up -d

# Check logs
docker compose logs -f backend
```

### Monitoring Setup

1. Enable production logging
2. Set up metrics collection (Prometheus/Grafana)
3. Configure alerting for slow queries
4. Monitor cache hit rates
5. Track API response times

## Next Steps

- Read the full [Performance Documentation](PERFORMANCE.md)
- Review [Database Optimization Patterns](PERFORMANCE.md#database-query-optimization)
- Learn about [Cache Invalidation Strategies](PERFORMANCE.md#cache-invalidation)
- Set up [Performance Monitoring](PERFORMANCE.md#performance-monitoring)

## Support

For issues or questions:
- Check logs: `docker compose logs backend`
- Review documentation: `/home/nix/projects/kai/docs/`
- Test health endpoint: `curl http://localhost:8000/health/detailed`
