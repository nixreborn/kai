# Kai Platform - Docker Quick Start

Get the Kai Mental Wellness Platform running in minutes!

## TL;DR

```bash
# Start everything
./scripts/start-dev.sh

# Access services
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Prerequisites

- Docker & Docker Compose installed
- 4GB RAM available
- Ports 3000, 5432, 8000 available

## One-Command Start

### Development Mode

```bash
./scripts/start-dev.sh
```

### Production Mode

```bash
# First, configure .env.production
cp .env.example .env.production
nano .env.production  # Edit with your values

# Then start
./scripts/start-prod.sh
```

## Essential Commands

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Check health
./scripts/health-check.sh

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# Backup database
./scripts/backup-db.sh

# Restore database
./scripts/restore-db.sh
```

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | User interface |
| Backend | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Redoc | http://localhost:8000/redoc | Alternative API docs |
| PostgreSQL | localhost:5432 | Database (kai/kai) |

## Troubleshooting

### Port Already in Use

```bash
# Change ports in .env.development
BACKEND_PORT=8001
FRONTEND_PORT=3001
POSTGRES_PORT=5433
```

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Can't Connect to Services

```bash
# Check all services are running
docker-compose ps

# Verify health
./scripts/health-check.sh

# Restart all
docker-compose restart
```

### Database Issues

```bash
# Check database logs
docker-compose logs postgres

# Access database
docker-compose exec postgres psql -U kai -d kai_db

# Reset database (WARNING: deletes all data!)
docker-compose down -v
docker-compose up -d
```

## File Structure

```
kai/
├── docker-compose.yml          # Main compose configuration
├── .env.development            # Development environment
├── .env.production            # Production environment
├── backend/
│   ├── Dockerfile             # Backend container definition
│   └── .dockerignore          # Excluded files
├── frontend/
│   ├── Dockerfile             # Frontend container definition
│   └── .dockerignore          # Excluded files
├── nginx/
│   ├── nginx.conf             # Nginx main config
│   └── conf.d/
│       └── kai.conf           # Kai platform config
└── scripts/
    ├── start-dev.sh           # Development startup
    ├── start-prod.sh          # Production startup
    ├── health-check.sh        # Health monitoring
    ├── backup-db.sh           # Database backup
    └── restore-db.sh          # Database restore
```

## Common Workflows

### Start Fresh

```bash
docker-compose down -v
./scripts/start-dev.sh
```

### Update Code

```bash
git pull
docker-compose build
docker-compose up -d
```

### View Backend Logs in Real-Time

```bash
docker-compose logs -f backend | grep ERROR
```

### Execute Commands in Container

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# Database shell
docker-compose exec postgres psql -U kai -d kai_db
```

## Development Tips

1. **Code changes**: Backend code auto-reloads (mounted as volume)
2. **Frontend changes**: Run `npm run dev` locally for faster HMR
3. **Database changes**: Use Alembic migrations
4. **Environment changes**: Restart services after .env changes

## Production Checklist

- [ ] Copy `.env.production` and configure
- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY: `openssl rand -hex 32`
- [ ] Update CORS_ORIGINS with your domain
- [ ] Configure SSL certificates (optional)
- [ ] Set DEBUG=false
- [ ] Test with `./scripts/health-check.sh`

## Need More Help?

See the full [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive documentation including:
- Detailed architecture
- Security best practices
- Scaling strategies
- Advanced troubleshooting
- CI/CD pipelines

## Quick Links

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Full Docs: [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Still having issues?** Check logs with `docker-compose logs -f` or run `./scripts/health-check.sh`
