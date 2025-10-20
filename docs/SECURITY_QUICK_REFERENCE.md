# Security Quick Reference - Kai Platform

Quick reference guide for common security operations and configurations.

## Quick Start

### 1. Generate Secrets (First Time Setup)

```bash
cd backend
python scripts/generate_secrets.py > secrets.txt

# Add to .env file
cat secrets.txt >> .env

# Secure the file
chmod 600 .env

# Delete the temp file
shred -u secrets.txt
```

### 2. Install Dependencies

```bash
cd backend
uv sync  # or pip install -e .
```

### 3. Configure Environment

```bash
# Copy example and update
cp .env.example .env

# Edit .env and replace:
# - CHANGE_ME_generate_with_generate_secrets_py
# With actual secret values
```

---

## Common Commands

### Secret Generation

```bash
# Generate all secrets
python scripts/generate_secrets.py

# Generate specific secret
python scripts/generate_secrets.py --single SECRET_KEY

# JSON output (for CI/CD)
python scripts/generate_secrets.py --format json

# Rotate a secret
python scripts/generate_secrets.py --rotate SECRET_KEY
```

### Rate Limiting

**Check rate limit status:**
```bash
# Via Redis CLI
redis-cli KEYS "slowapi:*"

# Clear rate limits (development only!)
redis-cli FLUSHDB
```

**Adjust rate limits** in `backend/src/security/rate_limiter.py`:
```python
class RateLimits:
    LOGIN = "5 per minute"  # Login attempts
    CHAT_MESSAGE = "30 per minute"  # Chat messages
```

### Password Validation

Test password strength:
```python
from src.security.validators import validate_password_strength

result = validate_password_strength("MyPassword123!")
print(f"Valid: {result.is_valid}")
print(f"Strength: {result.strength_score}/5")
print(f"Errors: {result.errors}")
```

### Input Sanitization

```python
from src.security.validators import sanitize_input

clean_text = sanitize_input(user_input, max_length=10000)
```

---

## Configuration Files

### Backend Security Configuration

| File | Purpose |
|------|---------|
| `backend/src/security/secrets.py` | Secret management utilities |
| `backend/src/security/rate_limiter.py` | Rate limiting configuration |
| `backend/src/security/validators.py` | Input validation & sanitization |
| `backend/src/security/middleware.py` | Security headers middleware |
| `backend/scripts/generate_secrets.py` | Secret generation script |

### Nginx Configuration

| File | Purpose |
|------|---------|
| `nginx/nginx.conf` | Base nginx configuration |
| `nginx/conf.d/kai-ssl.conf` | SSL/TLS configuration |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT signing key | Yes |
| `DATABASE_ENCRYPTION_KEY` | DB field encryption | Yes |
| `SESSION_SECRET` | Session signing | Yes |
| `CSRF_SECRET` | CSRF protection | Yes |
| `REDIS_URL` | Redis connection for rate limiting | Production |
| `SSL_ENABLED` | Enable SSL features | Production |

---

## Security Headers Reference

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `X-XSS-Protection` | `1; mode=block` | XSS protection |
| `Strict-Transport-Security` | `max-age=31536000` | Force HTTPS |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer |
| `Permissions-Policy` | Feature restrictions | Restrict browser features |
| `Content-Security-Policy` | Resource restrictions | Prevent XSS/injection |

**Check headers:**
```bash
curl -I https://kai.example.com
```

---

## Rate Limits at a Glance

| Endpoint | Rate Limit | Burst | Purpose |
|----------|------------|-------|---------|
| `/api/auth/login` | 5/min | 3 | Prevent brute force |
| `/api/auth/register` | 3/min | 3 | Prevent spam |
| `/api/auth/refresh` | 10/min | 5 | Token refresh |
| `/api/chat` | 30/min | 10 | Chat messages |
| `/api/journal` (POST) | 20/min | 5 | Create entries |
| `/api/journal` (GET) | 60/min | 10 | Read entries |

---

## SSL/TLS Quick Setup

### Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d kai.example.com

# Auto-renewal is configured automatically
```

### Self-Signed (Development Only)

```bash
# Generate certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/kai.key \
  -out /etc/ssl/certs/kai.crt \
  -subj "/CN=localhost"

# Update nginx config with certificate paths
```

### Test SSL Configuration

```bash
# SSL Labs
# Visit: https://www.ssllabs.com/ssltest/

# Command line
openssl s_client -connect kai.example.com:443 -showcerts

# Check expiry
openssl x509 -in /etc/ssl/certs/kai.crt -noout -dates
```

---

## Password Requirements

- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character
- No common passwords
- No sequential characters

**Example valid password:** `MyS3cure!Pass2024`

---

## Common Security Tasks

### 1. Rotate All Secrets

```bash
# 1. Generate new secrets
python scripts/generate_secrets.py > new_secrets.txt

# 2. Update production environment
# (Use your deployment platform's secret management)

# 3. Deploy updated application

# 4. Monitor for issues during grace period (7 days)

# 5. Remove old secrets after grace period
```

### 2. Block Suspicious IP

**In application (temporary):**
```python
# Add to rate limiter middleware
BLOCKED_IPS = ["1.2.3.4", "5.6.7.8"]
```

**In nginx:**
```nginx
# Add to nginx config
deny 1.2.3.4;
deny 5.6.7.8;
```

**In firewall (permanent):**
```bash
sudo ufw deny from 1.2.3.4
```

### 3. Invalidate All Sessions

```sql
-- Connect to database
DELETE FROM sessions;
```

Or via application:
```python
from src.models.database import Session
from src.models.db_session import get_db

async with get_db() as db:
    await db.execute(delete(Session))
    await db.commit()
```

### 4. Review Access Logs

```bash
# Recent errors
tail -f /var/log/nginx/kai_error.log

# Failed authentication attempts
grep "401" /var/log/nginx/kai_access.log | tail -20

# Rate limit violations
grep "429" /var/log/nginx/kai_access.log | tail -20

# Top IPs by request count
awk '{print $1}' /var/log/nginx/kai_access.log | sort | uniq -c | sort -rn | head -20
```

---

## Testing Security

### 1. Test Rate Limiting

```bash
# Test login rate limit (should fail after 5 attempts)
for i in {1..10}; do
  curl -X POST https://kai.example.com/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}' \
    -w "\nStatus: %{http_code}\n"
done
```

### 2. Test Security Headers

```bash
# Check all security headers
curl -I https://kai.example.com | grep -E "X-|Strict|Content-Security"
```

### 3. Test Input Validation

```python
# Test password validation
import requests

response = requests.post("https://kai.example.com/api/auth/register", json={
    "email": "test@example.com",
    "password": "weak"  # Should fail validation
})

print(response.status_code)  # Should be 400
print(response.json())  # Should show validation errors
```

### 4. Test SSL/TLS

```bash
# Test TLS versions
nmap --script ssl-enum-ciphers -p 443 kai.example.com

# Test certificate
openssl s_client -connect kai.example.com:443 -servername kai.example.com
```

---

## Security Monitoring Checklist

Daily:
- [ ] Check error logs for anomalies
- [ ] Review rate limit violations
- [ ] Monitor failed authentication attempts

Weekly:
- [ ] Review access patterns
- [ ] Check for unusual API usage
- [ ] Review database query logs

Monthly:
- [ ] Run SSL Labs test
- [ ] Update dependencies
- [ ] Review security headers
- [ ] Test rate limiting
- [ ] Audit user accounts

Quarterly:
- [ ] Rotate secrets
- [ ] Security audit
- [ ] Update security policies
- [ ] Review and update documentation

---

## Emergency Contacts

| Role | Contact | When to Contact |
|------|---------|-----------------|
| Security Lead | security@kai.example.com | Security incidents |
| DevOps | devops@kai.example.com | Infrastructure issues |
| On-Call | +1-XXX-XXX-XXXX | Critical incidents (24/7) |

---

## Useful Links

- Full Security Documentation: `docs/SECURITY.md`
- SSL Setup Guide: `docs/SSL_SETUP.md`
- API Documentation: `https://kai.example.com/docs`
- Rate Limiter Source: `backend/src/security/rate_limiter.py`
- Validators Source: `backend/src/security/validators.py`

---

## Quick Troubleshooting

### "Rate limit exceeded"
**Solution:** Wait for the time window to pass, or adjust limits in `rate_limiter.py`

### "Invalid password"
**Solution:** Ensure password meets requirements (12+ chars, mixed case, numbers, special chars)

### "SSL certificate error"
**Solution:** Check certificate expiry, verify certificate chain is complete

### "CORS error"
**Solution:** Add frontend domain to `CORS_ORIGINS` in `.env`

### "Redis connection failed"
**Solution:** Check Redis is running: `redis-cli ping` should return `PONG`

---

**Last Updated:** October 2024
