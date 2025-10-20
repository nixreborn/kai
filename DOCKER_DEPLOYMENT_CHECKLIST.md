# Docker Deployment Checklist

Use this checklist to verify your Docker deployment setup and prepare for production.

## Pre-Deployment Verification

### 1. File Structure Check

- [x] `backend/Dockerfile` exists and is valid
- [x] `backend/.dockerignore` exists
- [x] `frontend/Dockerfile` exists
- [x] `frontend/.dockerignore` exists
- [x] `docker-compose.yml` exists in project root
- [x] `scripts/` directory contains all startup scripts
- [x] `nginx/` directory contains configuration files
- [x] Environment files created (`.env.example`, `.env.development`, `.env.production`)

### 2. Script Permissions

Verify all scripts are executable:

```bash
ls -l scripts/
# All .sh files should have -rwxr-xr-x permissions
```

- [x] `start-dev.sh` is executable
- [x] `start-prod.sh` is executable
- [x] `backup-db.sh` is executable
- [x] `restore-db.sh` is executable
- [x] `health-check.sh` is executable

### 3. Docker Configuration Validation

```bash
# Validate docker-compose.yml syntax
docker-compose config

# Should list: postgres, backend, frontend
docker-compose config --services
```

- [ ] docker-compose.yml validates without errors
- [ ] All three services listed (postgres, backend, frontend)
- [ ] No warnings about obsolete attributes

### 4. Build Test (Development)

```bash
# Test backend build
cd backend
docker build -t kai-backend-test .

# Test frontend build
cd ../frontend
docker build -t kai-frontend-test .
```

- [ ] Backend image builds successfully
- [ ] Frontend image builds successfully
- [ ] Build times reasonable (< 5 minutes first build)

---

## Development Environment Setup

### 5. Environment Configuration

```bash
# Check development environment file
cat .env.development
```

Verify these variables are set:
- [ ] POSTGRES_USER and POSTGRES_PASSWORD
- [ ] LLM_BASE_URL points to your LLM endpoint
- [ ] DEBUG=true for development
- [ ] CORS_ORIGINS includes localhost:3000

### 6. First Start

```bash
# Start development environment
./scripts/start-dev.sh
```

Expected output:
- [ ] Docker is detected and running
- [ ] Images build successfully
- [ ] All three containers start
- [ ] Health checks pass
- [ ] Service URLs displayed

### 7. Service Verification

```bash
# Check all services are running
docker-compose ps

# Run health check
./scripts/health-check.sh
```

Verify:
- [ ] All containers show "Up" status
- [ ] All containers show "healthy" status
- [ ] PostgreSQL accepting connections on port 5432
- [ ] Backend API responding on port 8000
- [ ] Frontend responding on port 3000

### 8. Endpoint Testing

```bash
# Test backend health
curl http://localhost:8000/health

# Test backend API docs
curl http://localhost:8000/docs

# Test frontend (should return HTML)
curl http://localhost:3000
```

- [ ] Backend `/health` returns healthy status
- [ ] Backend `/docs` returns Swagger UI HTML
- [ ] Frontend returns Next.js HTML

### 9. Database Connection Test

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U kai -d kai_db -c "SELECT version();"
```

- [ ] Successfully connects to database
- [ ] PostgreSQL version displayed

### 10. Backup/Restore Test

```bash
# Create a test backup
./scripts/backup-db.sh

# Verify backup was created
ls -lh backups/
```

- [ ] Backup created successfully
- [ ] Backup file exists in `backups/` directory
- [ ] Backup is compressed (.gz)
- [ ] File size is reasonable

---

## Production Deployment Preparation

### 11. Production Environment Setup

```bash
# Create production environment file
cp .env.example .env.production
nano .env.production
```

**CRITICAL**: Update these values:
- [ ] POSTGRES_PASSWORD - Strong password (generated with `openssl rand -base64 32`)
- [ ] SECRET_KEY - Strong key (generated with `openssl rand -hex 32`)
- [ ] DEBUG=false
- [ ] CORS_ORIGINS - Your production domain(s)
- [ ] NEXT_PUBLIC_API_URL - Your production API URL
- [ ] All "CHANGE_ME" placeholders replaced

### 12. Production Configuration Validation

```bash
# Verify no default passwords remain
grep "CHANGE_ME" .env.production
# Should return nothing

# Verify DEBUG is false
grep "DEBUG=false" .env.production
```

- [ ] No "CHANGE_ME" placeholders found
- [ ] DEBUG is set to false
- [ ] All required variables have values
- [ ] CORS configured for production domain

### 13. SSL/HTTPS Setup (Production)

If using Nginx reverse proxy:

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Option 1: Let's Encrypt (recommended)
# Follow instructions in DEPLOYMENT.md

# Option 2: Self-signed (testing only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

- [ ] SSL certificates obtained
- [ ] Certificates placed in `nginx/ssl/`
- [ ] HTTPS server block uncommented in `nginx/conf.d/kai.conf`
- [ ] Certificate permissions are secure (600 for key)

### 14. Resource Limits Review

```bash
# Review resource limits in docker-compose.yml
grep -A 5 "resources:" docker-compose.yml
```

Adjust if needed for your server:
- [ ] Backend: 2GB RAM, 2 CPU (default)
- [ ] Frontend: 1GB RAM, 1 CPU (default)
- [ ] Limits appropriate for your server capacity

### 15. Security Audit

- [ ] No secrets in Dockerfiles
- [ ] `.env` files in `.gitignore`
- [ ] All containers run as non-root users
- [ ] Health checks configured for all services
- [ ] Network isolation configured (kai-network)
- [ ] Unnecessary ports not exposed
- [ ] Security headers configured in Nginx

---

## Production Deployment

### 16. Production Start

```bash
# Start production environment
./scripts/start-prod.sh
```

Expected:
- [ ] Script validates environment file exists
- [ ] Script checks for default passwords
- [ ] 5-second confirmation delay works
- [ ] All services build and start
- [ ] Health checks pass
- [ ] Service URLs displayed

### 17. Production Verification

```bash
# Check service health
./scripts/health-check.sh

# Check logs for errors
docker-compose logs --tail=50

# Test endpoints
curl http://localhost:8000/health
curl https://your-domain.com  # If using Nginx + SSL
```

- [ ] All services healthy
- [ ] No errors in logs
- [ ] API endpoints responding
- [ ] Frontend loads correctly
- [ ] SSL certificate valid (if configured)

### 18. Load Testing (Optional but Recommended)

```bash
# Install Apache Bench (if not installed)
# sudo apt-get install apache2-utils

# Test backend
ab -n 100 -c 10 http://localhost:8000/health

# Test frontend
ab -n 100 -c 10 http://localhost:3000/
```

- [ ] Backend handles concurrent requests
- [ ] Frontend handles concurrent requests
- [ ] Response times acceptable
- [ ] No errors under load

---

## Monitoring Setup

### 19. Log Monitoring

```bash
# View real-time logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend
```

- [ ] Logs are readable and informative
- [ ] No repeated errors
- [ ] Log levels appropriate

### 20. Resource Monitoring

```bash
# Check resource usage
docker stats
```

- [ ] CPU usage within limits
- [ ] Memory usage within limits
- [ ] No containers showing OOMKilled
- [ ] Network I/O reasonable

### 21. Automated Backups

```bash
# Setup cron job
crontab -e

# Add:
# 0 2 * * * cd /path/to/kai && ./scripts/backup-db.sh
```

- [ ] Cron job added for daily backups
- [ ] Backup directory has sufficient space
- [ ] Test backup runs successfully
- [ ] Automatic cleanup working (7-day retention)

---

## Post-Deployment

### 22. Documentation Review

- [ ] README.md updated with deployment info
- [ ] DEPLOYMENT.md reviewed and accurate
- [ ] Team members can access documentation
- [ ] Runbook created for common operations

### 23. Disaster Recovery Test

```bash
# Test restore procedure
./scripts/restore-db.sh
```

- [ ] Restore script works correctly
- [ ] Pre-restore backup created automatically
- [ ] Database restored successfully
- [ ] Application works after restore

### 24. Monitoring and Alerts Setup

Production monitoring (choose based on your needs):
- [ ] Uptime monitoring configured (UptimeRobot, Pingdom, etc.)
- [ ] Error tracking setup (Sentry, etc.)
- [ ] Log aggregation configured (optional)
- [ ] Alerts configured for service failures
- [ ] On-call rotation established (if applicable)

### 25. Final Verification

- [ ] All services running in production
- [ ] Health checks passing consistently
- [ ] Backups running automatically
- [ ] Monitoring and alerts working
- [ ] Team has access to necessary credentials
- [ ] Emergency procedures documented
- [ ] Success! 🎉

---

## Rollback Procedure

If something goes wrong:

```bash
# Stop services
docker-compose down

# Restore database from backup
./scripts/restore-db.sh

# Review logs
docker-compose logs

# Fix issues in code or configuration

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Verify
./scripts/health-check.sh
```

---

## Maintenance Schedule

### Daily
- [ ] Check service health
- [ ] Review error logs
- [ ] Verify backups completed

### Weekly
- [ ] Review resource usage
- [ ] Check disk space
- [ ] Test backup restoration
- [ ] Review security logs

### Monthly
- [ ] Update Docker images
- [ ] Review and update dependencies
- [ ] Security audit
- [ ] Performance review

### Quarterly
- [ ] Disaster recovery drill
- [ ] Documentation review
- [ ] Capacity planning
- [ ] Cost optimization review

---

## Quick Reference Commands

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

# Restart service
docker-compose restart backend

# Stop everything
docker-compose down

# Nuclear option (reset everything)
docker-compose down -v
docker system prune -a
```

---

## Support Resources

- **Documentation**: See DEPLOYMENT.md for detailed information
- **Quick Start**: See DOCKER_QUICK_START.md for common tasks
- **Troubleshooting**: See DEPLOYMENT.md Troubleshooting section
- **Docker Docs**: https://docs.docker.com/

---

**Checklist Version**: 1.0
**Last Updated**: October 20, 2025
**Status**: Ready for use
