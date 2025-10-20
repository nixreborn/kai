# Security Documentation - Kai Mental Wellness Platform

This document outlines the security measures, procedures, and best practices implemented in the Kai Mental Wellness Platform.

## Table of Contents

1. [Security Overview](#security-overview)
2. [Secret Management](#secret-management)
3. [Authentication & Authorization](#authentication--authorization)
4. [Rate Limiting](#rate-limiting)
5. [Security Headers](#security-headers)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Input Validation & Sanitization](#input-validation--sanitization)
8. [Security Checklist for Deployment](#security-checklist-for-deployment)
9. [Incident Response Plan](#incident-response-plan)
10. [Security Monitoring](#security-monitoring)

---

## Security Overview

The Kai platform implements defense-in-depth security with multiple layers:

- **Application Layer**: Input validation, authentication, authorization, rate limiting
- **Transport Layer**: TLS 1.2+, strong cipher suites, HSTS
- **Infrastructure Layer**: Security headers, WAF-ready configuration, DDoS protection

### Security Contact

For security issues, please email: security@kai.example.com

---

## Secret Management

### Secret Types

The platform uses several types of secrets:

1. **JWT Secret Key** (`SECRET_KEY`): Signs JWT tokens for authentication
2. **Database Encryption Key** (`DATABASE_ENCRYPTION_KEY`): Encrypts sensitive database fields
3. **Session Secret** (`SESSION_SECRET`): Signs session cookies
4. **CSRF Secret** (`CSRF_SECRET`): Protects against CSRF attacks
5. **API Key Salt** (`API_KEY_SALT`): Salts API key hashes

### Generating Secrets

Use the provided script to generate cryptographically secure secrets:

```bash
# Generate all secrets
cd backend
python scripts/generate_secrets.py

# Generate a specific secret
python scripts/generate_secrets.py --single SECRET_KEY

# Output in different formats
python scripts/generate_secrets.py --format json
python scripts/generate_secrets.py --format yaml
```

### Secret Storage

**Development:**
- Store secrets in `.env` file (never commit to git)
- `.env` is in `.gitignore` by default

**Production:**
- Use a secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.)
- Use environment variables injected by your deployment platform
- Consider using encrypted secrets in CI/CD pipelines

### Secret Rotation Procedures

#### Scheduled Rotation (Every 90 days)

1. **Generate new secrets:**
   ```bash
   python scripts/generate_secrets.py
   ```

2. **Update production environment variables** with new secrets

3. **Deploy with grace period:**
   - Keep both old and new secrets valid for 7 days
   - Monitor for authentication failures
   - Remove old secrets after grace period

4. **Invalidate old sessions:**
   ```bash
   # Optional: Force all users to re-authenticate
   # Run this SQL in production database
   DELETE FROM sessions WHERE created_at < NOW() - INTERVAL '7 days';
   ```

#### Emergency Rotation (Security Incident)

1. **Immediately generate new secrets**
2. **Deploy to production immediately** (no grace period)
3. **Invalidate all sessions** (forces all users to log out)
4. **Notify users** of required re-authentication
5. **Document incident** in security log

### Secret Rotation Script

```python
# Example rotation script
from src.security.secrets import SecretManager, rotate_secret_key

manager = SecretManager()

# Rotate with grace period
new_secret, metadata = manager.rotate_secret(
    current_secret=current_secret,
    expiry_days=90,
    grace_period_days=7
)

# Update environment variables
print(f"New SECRET_KEY: {new_secret}")
print(f"Expires: {metadata.expires_at}")
```

---

## Authentication & Authorization

### Password Requirements

Enforced by `src/security/validators.py`:

- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character
- No common passwords
- No sequential characters

### Password Hashing

- Algorithm: bcrypt with 12 rounds
- Location: `src/auth/auth.py`
- Never stores plain-text passwords

### JWT Tokens

- Algorithm: HS256 (configurable to RS256)
- Expiration: 30 minutes (configurable)
- Refresh tokens: 7 days (configurable)
- Storage: HTTP-only cookies (recommended) or localStorage

### Session Management

- Sessions stored in database
- Automatic cleanup of expired sessions
- Session invalidation on logout
- Token refresh mechanism

---

## Rate Limiting

### Rate Limit Configuration

Configured in `src/security/rate_limiter.py`:

| Endpoint Type | Rate Limit | Burst |
|---------------|------------|-------|
| Login | 5 req/min | 3 |
| Register | 3 req/min | 3 |
| Token Refresh | 10 req/min | 5 |
| Chat Message | 30 req/min | 10 |
| Journal Create | 20 req/min | 5 |
| Journal Read | 60 req/min | 10 |

### Rate Limiting Storage

- **Development**: In-memory storage
- **Production**: Redis-backed storage

Configure Redis URL in `.env`:
```bash
REDIS_URL=redis://localhost:6379
```

### Rate Limit Headers

All rate-limited responses include:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

### Customizing Rate Limits

Edit `src/security/rate_limiter.py`:

```python
class RateLimits:
    # Adjust these values as needed
    LOGIN = "10 per minute"  # Increase login limit
    CHAT_MESSAGE = "60 per minute"  # Increase chat limit
```

---

## Security Headers

### Implemented Headers

All responses include these security headers:

#### X-Content-Type-Options: nosniff
Prevents MIME type sniffing attacks.

#### X-Frame-Options: DENY
Prevents clickjacking by blocking iframe embedding.

#### X-XSS-Protection: 1; mode=block
Enables browser XSS filtering.

#### Referrer-Policy: strict-origin-when-cross-origin
Controls referrer information leakage.

#### Permissions-Policy
Restricts browser features:
```
geolocation=(), microphone=(), camera=()
```

#### Content-Security-Policy (CSP)
Restricts resource loading:
```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self' data:;
connect-src 'self';
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
```

#### Strict-Transport-Security (HSTS)
Forces HTTPS for 1 year:
```
max-age=31536000; includeSubDomains; preload
```

### Customizing Headers

Edit `src/security/middleware.py`:

```python
class SecurityHeadersMiddleware:
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add or modify headers here
        response.headers["Custom-Header"] = "value"

        return response
```

---

## SSL/TLS Configuration

### Certificate Setup

#### Option 1: Let's Encrypt (Recommended)

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d kai.example.com -d www.kai.example.com

# Auto-renewal (certbot sets this up automatically)
certbot renew --dry-run
```

#### Option 2: Commercial Certificate

1. Generate CSR:
   ```bash
   openssl req -new -newkey rsa:2048 -nodes \
     -keyout kai.key -out kai.csr
   ```

2. Submit CSR to certificate authority

3. Install certificate:
   ```bash
   cp kai.crt /etc/ssl/certs/
   cp kai.key /etc/ssl/private/
   chmod 600 /etc/ssl/private/kai.key
   ```

### Generate Diffie-Hellman Parameters

```bash
openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
```

### TLS Configuration

Located in `nginx/conf.d/kai-ssl.conf`:

- **Protocols**: TLS 1.2, TLS 1.3 (no TLS 1.0/1.1)
- **Cipher Suites**: Modern, secure ciphers only
- **OCSP Stapling**: Enabled
- **Session Cache**: 10 minutes
- **Session Tickets**: Disabled (for forward secrecy)

### Testing SSL Configuration

```bash
# Test SSL configuration
curl -I https://kai.example.com

# Test with SSL Labs
# Visit: https://www.ssllabs.com/ssltest/
```

### HTTP to HTTPS Redirect

All HTTP traffic is automatically redirected to HTTPS:

```nginx
server {
    listen 80;
    server_name kai.example.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Input Validation & Sanitization

### Email Validation

```python
from src.security.validators import validate_email_format

is_valid, email_or_error = validate_email_format("user@example.com")
```

### Password Validation

```python
from src.security.validators import validate_password_strength

result = validate_password_strength("MyP@ssw0rd123")
if not result.is_valid:
    print(f"Errors: {result.errors}")
    print(f"Strength: {result.strength_score}/5")
```

### Input Sanitization

```python
from src.security.validators import sanitize_input

# Removes control characters, escapes HTML
clean_text = sanitize_input(user_input, max_length=10000)
```

### Chat Message Validation

```python
from src.security.validators import validate_chat_message

is_valid, error = validate_chat_message(message)
```

### Journal Content Validation

```python
from src.security.validators import validate_journal_content

is_valid, error = validate_journal_content(content, max_length=50000)
```

---

## Security Checklist for Deployment

### Pre-Deployment

- [ ] Generate all production secrets using `generate_secrets.py`
- [ ] Update `.env` with production values
- [ ] Remove or protect API documentation endpoints (`/docs`, `/redoc`)
- [ ] Configure Redis for rate limiting
- [ ] Set up SSL certificates
- [ ] Configure firewall rules
- [ ] Set `DEBUG=false` in production
- [ ] Configure CORS origins to production domain only
- [ ] Review and update `ALLOWED_HOSTS` in nginx
- [ ] Set up database backups
- [ ] Configure log rotation

### Post-Deployment

- [ ] Verify HTTPS is working
- [ ] Test SSL configuration (SSL Labs)
- [ ] Verify security headers (securityheaders.com)
- [ ] Test rate limiting on all endpoints
- [ ] Verify authentication flows
- [ ] Check error handling (no sensitive info in errors)
- [ ] Test password reset flow
- [ ] Monitor logs for unusual activity
- [ ] Set up alerting for security events
- [ ] Document any environment-specific configurations

### Regular Maintenance

- [ ] Rotate secrets every 90 days
- [ ] Update dependencies monthly
- [ ] Review and rotate SSL certificates before expiry
- [ ] Review access logs weekly
- [ ] Update security policies quarterly
- [ ] Conduct security audit annually

---

## Incident Response Plan

### 1. Detection

**Monitoring for:**
- Unusual authentication attempts
- Rate limit violations
- Suspicious API access patterns
- Database anomalies
- Error rate spikes

### 2. Classification

**Severity Levels:**

| Level | Description | Response Time |
|-------|-------------|---------------|
| Critical | Active breach, data exposure | Immediate |
| High | Attempted breach, vulnerability | 1 hour |
| Medium | Suspicious activity | 4 hours |
| Low | Policy violation | 24 hours |

### 3. Response Actions

#### Immediate Actions (Critical)

1. **Isolate affected systems**
   ```bash
   # Block suspicious IP in firewall
   ufw deny from <IP_ADDRESS>
   ```

2. **Rotate all secrets immediately**
   ```bash
   python scripts/generate_secrets.py
   # Deploy new secrets to production
   ```

3. **Invalidate all sessions**
   ```sql
   DELETE FROM sessions;
   ```

4. **Enable additional logging**
   ```bash
   # Increase log level
   export LOG_LEVEL=DEBUG
   ```

5. **Notify security team**

#### Investigation Actions

1. **Collect logs**
   ```bash
   # Application logs
   tail -n 1000 /var/log/kai/app.log > incident_app.log

   # Nginx logs
   tail -n 1000 /var/log/nginx/kai_access.log > incident_access.log
   tail -n 1000 /var/log/nginx/kai_error.log > incident_error.log

   # Database logs
   # Export relevant database query logs
   ```

2. **Identify attack vector**
3. **Assess data exposure**
4. **Document timeline**

#### Recovery Actions

1. **Patch vulnerabilities**
2. **Deploy fixed version**
3. **Restore from clean backup** (if needed)
4. **Monitor for continued attacks**
5. **Update security measures**

### 4. Communication

**Internal:**
- Notify development team
- Update management
- Document in incident log

**External:**
- Notify affected users (if applicable)
- Report to authorities (if required)
- Public disclosure (if appropriate)

### 5. Post-Incident

1. **Conduct post-mortem meeting**
2. **Update security documentation**
3. **Implement preventive measures**
4. **Review and update incident response plan**

---

## Security Monitoring

### Metrics to Monitor

1. **Authentication**
   - Failed login attempts
   - Account lockouts
   - Password reset requests

2. **Rate Limiting**
   - Rate limit violations by endpoint
   - Rate limit violations by IP
   - Burst limit triggers

3. **API Access**
   - Unusual access patterns
   - Access from unexpected geolocations
   - Spike in error rates

4. **Database**
   - Unusual query patterns
   - Slow queries
   - Connection pool exhaustion

### Logging

**Log Locations:**
- Application: `/var/log/kai/app.log`
- Nginx Access: `/var/log/nginx/kai_access.log`
- Nginx Error: `/var/log/nginx/kai_error.log`

**Log Retention:**
- Application logs: 30 days
- Access logs: 90 days
- Security logs: 1 year

### Alerting

**Alert On:**
- Multiple failed authentication attempts (>10 in 5 minutes)
- Rate limit violations (>100 per hour per IP)
- 500 errors (>10 per minute)
- Database connection failures
- SSL certificate expiration (30 days warning)

### Tools

Recommended monitoring tools:
- **Prometheus** + **Grafana**: Metrics and dashboards
- **ELK Stack**: Log aggregation and analysis
- **Sentry**: Error tracking
- **Datadog** / **New Relic**: Application performance monitoring

---

## Additional Resources

### Security Standards

- OWASP Top 10: https://owasp.org/Top10/
- CWE Top 25: https://cwe.mitre.org/top25/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework

### Testing Tools

- **OWASP ZAP**: Web application security scanner
- **Burp Suite**: Security testing platform
- **nmap**: Network scanner
- **sqlmap**: SQL injection testing

### Compliance

If handling protected health information (PHI), ensure HIPAA compliance:
- Implement audit logging
- Encrypt data at rest and in transit
- Establish business associate agreements
- Regular security training

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-10-20 | Initial security documentation |

---

## Contact

For security concerns or questions:
- Email: security@kai.example.com
- Security Portal: https://kai.example.com/security
- Bug Bounty Program: https://kai.example.com/bug-bounty

---

**Last Updated:** October 2024
**Next Review:** January 2025
