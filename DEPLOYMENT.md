# Kai Platform - Deployment Guide

This comprehensive guide covers deploying the Kai Mental Wellness Platform using Docker and Docker Compose.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Environment Configuration](#environment-configuration)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Database Management](#database-management)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)
- [Scaling Considerations](#scaling-considerations)

---

## Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **System Requirements**:
  - Minimum: 4GB RAM, 2 CPU cores, 20GB disk space
  - Recommended: 8GB RAM, 4 CPU cores, 50GB disk space
- **Network Access**:
  - LLM endpoint: `http://192.168.1.7:8000/v1` (or configure your own)

### Installing Docker

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS/Windows:**
Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

---

## Quick Start

### One-Command Development Setup

```bash
# Clone the repository (if not already)
git clone <repository-url>
cd kai

# Start in development mode
./scripts/start-dev.sh
```

This will:
1. Build all Docker images
2. Start PostgreSQL, Backend, and Frontend services
3. Run health checks
4. Display service URLs

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## Architecture Overview

### Docker Services

The platform consists of four main services:

```
┌─────────────────────────────────────────┐
│           Nginx (Optional)              │
│        Reverse Proxy & SSL              │
│            Port: 80/443                 │
└─────────────┬───────────────────────────┘
              │
       ┌──────┴──────┐
       │             │
┌──────▼─────┐ ┌────▼───────┐
│  Frontend  │ │  Backend   │
│  Next.js   │ │  FastAPI   │
│  Port 3000 │ │  Port 8000 │
└────────────┘ └─────┬──────┘
                     │
              ┌──────▼──────┐
              │  PostgreSQL │
              │  Port 5432  │
              └─────────────┘
```

### Service Details

| Service | Technology | Purpose | Port |
|---------|-----------|---------|------|
| **Frontend** | Next.js 15 | User interface | 3000 |
| **Backend** | FastAPI (Python 3.11) | API & AI agents | 8000 |
| **PostgreSQL** | PostgreSQL 16 | Database | 5432 |
| **Nginx** | Nginx Alpine | Reverse proxy (optional) | 80/443 |

---

## Environment Configuration

### Environment Files

The platform uses three environment files:

1. **`.env.example`** - Template with all variables
2. **`.env.development`** - Development configuration
3. **`.env.production`** - Production configuration (create from example)

### Required Environment Variables

#### Database Configuration
```bash
POSTGRES_USER=kai                    # Database username
POSTGRES_PASSWORD=secure_password    # Database password (CHANGE IN PRODUCTION!)
POSTGRES_DB=kai_db                   # Database name
POSTGRES_PORT=5432                   # Database port
```

#### Backend Configuration
```bash
HOST=0.0.0.0
PORT=8000
DEBUG=false                          # Set to false in production
CORS_ORIGINS=http://localhost:3000   # Comma-separated allowed origins
```

#### LLM Configuration
```bash
LLM_BASE_URL=http://192.168.1.7:8000/v1  # Your LLM endpoint
LLM_API_KEY=your-api-key                  # API key if required
LLM_MODEL=default                         # Model name
```

#### Security Configuration
```bash
SECRET_KEY=generate-a-strong-key-here  # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Agent Configuration
```bash
KAI_AGENT_MODEL=default
GUARDRAIL_AGENT_MODEL=default
GENETIC_AGENT_MODEL=default
WELLNESS_AGENT_MODEL=default
```

### Generating Secret Keys

For production, generate a secure secret key:

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate POSTGRES_PASSWORD
openssl rand -base64 32
```

---

## Development Deployment

### Starting Development Environment

```bash
# Option 1: Use the startup script (recommended)
./scripts/start-dev.sh

# Option 2: Manual start
cp .env.example .env.development
docker-compose build
docker-compose up -d
```

### Development Features

- **Hot Reload**: Source code is mounted as volumes for live updates
- **Debug Mode**: Detailed error messages and logging
- **Auto-restart**: Containers restart automatically on failure
- **Source Mapping**: Backend source mounted at `/app/src`

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Stopping Development Environment

```bash
# Stop services (keeps data)
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Copy `.env.production` and configure all values
- [ ] Change all default passwords
- [ ] Generate strong `SECRET_KEY`
- [ ] Update `CORS_ORIGINS` with your domain
- [ ] Configure SSL certificates (if using Nginx)
- [ ] Set `DEBUG=false`
- [ ] Review resource limits in `docker-compose.yml`

### Production Setup

1. **Create Production Environment File:**

```bash
cp .env.example .env.production
nano .env.production  # Edit with your values
```

2. **Update Critical Values:**

```bash
# In .env.production
POSTGRES_PASSWORD=<strong-password>
SECRET_KEY=<generated-key>
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

3. **Start Production Services:**

```bash
./scripts/start-prod.sh
```

Or manually:

```bash
docker-compose --profile production up -d
```

### SSL/HTTPS Setup

#### Option 1: Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

#### Option 2: Self-Signed Certificate (Development/Testing)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

Then uncomment the HTTPS server block in `nginx/conf.d/kai.conf`.

### Production Monitoring

```bash
# Check service health
./scripts/health-check.sh

# Monitor resource usage
docker stats

# Check logs
docker-compose logs -f --tail=50
```

---

## Database Management

### Backup Database

The platform includes automated backup scripts.

```bash
# Create backup
./scripts/backup-db.sh
```

Backups are stored in `./backups/` directory with timestamps:
- Format: `kai_db_backup_YYYYMMDD_HHMMSS.sql.gz`
- Retention: Last 7 days (automatic cleanup)

### Restore Database

```bash
# Restore from backup
./scripts/restore-db.sh

# Follow prompts to select backup file
# Or restore latest:
# Enter 'latest' when prompted
```

**Important:** The restore script creates a pre-restore backup automatically.

### Manual Database Operations

#### Manual Backup

```bash
docker-compose exec postgres pg_dump -U kai -d kai_db > backup.sql
gzip backup.sql
```

#### Manual Restore

```bash
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U kai -d kai_db
```

#### Access PostgreSQL CLI

```bash
docker-compose exec postgres psql -U kai -d kai_db
```

### Database Migrations

Migrations are handled by Alembic (if configured in backend).

```bash
# Run migrations on backend startup
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

---

## Monitoring and Health Checks

### Health Check Script

```bash
./scripts/health-check.sh
```

This script checks:
- Docker service status
- Container health
- Network connectivity
- API endpoints
- Resource usage

### Manual Health Checks

```bash
# Check all services
docker-compose ps

# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# PostgreSQL health
docker-compose exec postgres pg_isready -U kai
```

### Service Endpoints

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `/health` | Backend health check | `curl http://localhost:8000/health` |
| `/docs` | API documentation | http://localhost:8000/docs |
| `/redoc` | Alternative API docs | http://localhost:8000/redoc |
| `/` | Root endpoint | http://localhost:8000/ |

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `bind: address already in use`

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process or change port in .env
BACKEND_PORT=8001
```

#### 2. Container Fails to Start

**Error:** Container exits immediately

**Solution:**
```bash
# Check logs
docker-compose logs backend

# Rebuild without cache
docker-compose build --no-cache backend
docker-compose up -d backend
```

#### 3. Database Connection Issues

**Error:** `could not connect to server`

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify environment variables
docker-compose exec backend env | grep DATABASE
```

#### 4. Frontend Can't Connect to Backend

**Error:** `Network Error` or `CORS Error`

**Solution:**
```bash
# Verify CORS_ORIGINS includes frontend URL
# In .env:
CORS_ORIGINS=http://localhost:3000,http://frontend:3000

# Check backend is healthy
curl http://localhost:8000/health

# Verify frontend environment
docker-compose exec frontend env | grep NEXT_PUBLIC
```

#### 5. Out of Memory

**Error:** `OOMKilled`

**Solution:**
```bash
# Increase Docker memory limit (Docker Desktop)
# Or adjust resource limits in docker-compose.yml

# Check memory usage
docker stats
```

### Debugging Tips

```bash
# Enter container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# View real-time logs
docker-compose logs -f backend

# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend

# Check network connectivity between services
docker-compose exec backend ping postgres
docker-compose exec frontend ping backend
```

### Reset Everything

```bash
# Nuclear option: Remove all containers, volumes, and images
docker-compose down -v
docker system prune -a
rm -rf backend/.venv
./scripts/start-dev.sh
```

---

## Security Best Practices

### Production Security Checklist

- [ ] **Change All Default Passwords**
  - PostgreSQL password
  - Secret key
  - API keys

- [ ] **Use HTTPS**
  - Configure SSL certificates
  - Enable HTTPS in Nginx
  - Redirect HTTP to HTTPS

- [ ] **Secure Environment Variables**
  - Never commit `.env` files to Git
  - Use secrets management (Docker secrets, vault)
  - Rotate keys regularly

- [ ] **Network Security**
  - Use firewall rules
  - Limit exposed ports
  - Use private networks for internal communication

- [ ] **Container Security**
  - Run containers as non-root users (already configured)
  - Keep images updated
  - Scan for vulnerabilities: `docker scan kai-backend`

- [ ] **Database Security**
  - Strong passwords
  - Limit network access
  - Regular backups
  - Enable SSL connections

- [ ] **Application Security**
  - Keep dependencies updated
  - Enable rate limiting
  - Configure proper CORS
  - Implement authentication/authorization

### Secrets Management

#### Using Docker Secrets (Swarm Mode)

```yaml
# docker-compose.yml
secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt

services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
```

#### Using Environment Files

```bash
# .env.production (never commit!)
export POSTGRES_PASSWORD=$(cat secrets/postgres_password)
```

---

## Scaling Considerations

### Horizontal Scaling

#### Backend Scaling

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3
```

Update Nginx configuration for load balancing:

```nginx
upstream backend {
    server backend:8000;
    server backend:8000;
    server backend:8000;
}
```

#### Frontend Scaling

```bash
# Scale frontend to 2 instances
docker-compose up -d --scale frontend=2
```

### Vertical Scaling

Adjust resource limits in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 1G
```

### Database Scaling

For production, consider:

1. **Read Replicas**: PostgreSQL streaming replication
2. **Connection Pooling**: PgBouncer
3. **Managed Database**: AWS RDS, Google Cloud SQL, etc.

Example with PgBouncer:

```yaml
services:
  pgbouncer:
    image: edoburu/pgbouncer
    environment:
      DATABASE_URL: postgres://kai:password@postgres/kai_db
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 1000
```

### Load Balancing

For production, use:
- **Nginx**: Built-in load balancing
- **HAProxy**: Advanced load balancing
- **Cloud Load Balancers**: AWS ALB, GCP Load Balancer

### Caching

Implement caching layers:

1. **Redis**: Session and data caching
2. **CDN**: Static asset delivery
3. **Application Cache**: Backend caching

Example Redis service:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
```

---

## Deployment Workflows

### CI/CD Pipeline Example

**GitHub Actions:**

```yaml
name: Deploy Kai Platform

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build and push images
        run: |
          docker-compose build
          docker-compose push

      - name: Deploy to production
        run: |
          ssh user@server 'cd /app && docker-compose pull && docker-compose up -d'
```

### Blue-Green Deployment

1. Deploy new version to separate environment
2. Run health checks
3. Switch traffic to new version
4. Keep old version for rollback

### Rolling Updates

```bash
# Update backend without downtime
docker-compose up -d --no-deps --build backend

# Update frontend
docker-compose up -d --no-deps --build frontend
```

---

## Backup and Disaster Recovery

### Automated Backup Schedule

Using cron:

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * cd /path/to/kai && ./scripts/backup-db.sh
```

### Disaster Recovery Plan

1. **Regular Backups**: Daily database backups
2. **Off-site Storage**: Copy backups to S3, Google Cloud Storage
3. **Test Restores**: Regularly test backup restoration
4. **Documentation**: Keep deployment docs updated
5. **Monitoring**: Set up alerts for service failures

### Backup to Cloud

```bash
# Backup to S3 (example)
./scripts/backup-db.sh
aws s3 cp backups/ s3://your-bucket/kai-backups/ --recursive

# Backup to Google Cloud Storage
gsutil -m cp -r backups/* gs://your-bucket/kai-backups/
```

---

## Support and Maintenance

### Regular Maintenance Tasks

- **Weekly**: Check logs for errors
- **Monthly**: Update Docker images
- **Quarterly**: Security audit
- **As needed**: Scale resources

### Updating the Platform

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

### Logs Rotation

Configure log rotation to prevent disk space issues:

```bash
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

## Quick Reference

### Essential Commands

```bash
# Start development
./scripts/start-dev.sh

# Start production
./scripts/start-prod.sh

# Health check
./scripts/health-check.sh

# Backup database
./scripts/backup-db.sh

# Restore database
./scripts/restore-db.sh

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart service
docker-compose restart backend

# Rebuild service
docker-compose up -d --build backend
```

### Service URLs

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

---

**Last Updated**: 2025-10-20

For issues or questions, please open an issue in the project repository.
