# SSL/TLS Setup Guide for Kai Platform

This guide provides step-by-step instructions for setting up SSL/TLS certificates for the Kai Mental Wellness Platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Option 1: Let's Encrypt (Free, Automated)](#option-1-lets-encrypt-free-automated)
3. [Option 2: Self-Signed Certificates (Development)](#option-2-self-signed-certificates-development)
4. [Option 3: Commercial Certificate](#option-3-commercial-certificate)
5. [Nginx Configuration](#nginx-configuration)
6. [Testing SSL Configuration](#testing-ssl-configuration)
7. [Certificate Renewal](#certificate-renewal)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Domain name pointing to your server (e.g., kai.example.com)
- Root or sudo access to the server
- Nginx installed and running
- Ports 80 and 443 open in firewall

---

## Option 1: Let's Encrypt (Free, Automated)

### Step 1: Install Certbot

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

**CentOS/RHEL:**
```bash
sudo yum install certbot python3-certbot-nginx
```

### Step 2: Obtain Certificate

```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain certificate (standalone mode)
sudo certbot certonly --standalone -d kai.example.com -d www.kai.example.com

# Or use nginx plugin (nginx must be configured first)
sudo certbot --nginx -d kai.example.com -d www.kai.example.com
```

### Step 3: Certificate Locations

Certbot will create certificates at:
```
/etc/letsencrypt/live/kai.example.com/fullchain.pem
/etc/letsencrypt/live/kai.example.com/privkey.pem
/etc/letsencrypt/live/kai.example.com/chain.pem
```

### Step 4: Update Nginx Configuration

Edit `/etc/nginx/conf.d/kai-ssl.conf`:

```nginx
ssl_certificate /etc/letsencrypt/live/kai.example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/kai.example.com/privkey.pem;
ssl_trusted_certificate /etc/letsencrypt/live/kai.example.com/chain.pem;
```

### Step 5: Test and Restart

```bash
# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

### Step 6: Set Up Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job or systemd timer
# Verify it's running:
sudo systemctl status certbot.timer
```

---

## Option 2: Self-Signed Certificates (Development)

**WARNING:** Self-signed certificates should only be used for development/testing, never in production.

### Step 1: Generate Self-Signed Certificate

```bash
# Create directory for certificates
sudo mkdir -p /etc/ssl/private
sudo mkdir -p /etc/ssl/certs

# Generate private key and certificate (valid for 365 days)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/kai.key \
  -out /etc/ssl/certs/kai.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=kai.example.com"
```

### Step 2: Set Permissions

```bash
sudo chmod 600 /etc/ssl/private/kai.key
sudo chmod 644 /etc/ssl/certs/kai.crt
```

### Step 3: Update Nginx Configuration

Use the paths in your nginx configuration:
```nginx
ssl_certificate /etc/ssl/certs/kai.crt;
ssl_certificate_key /etc/ssl/private/kai.key;
```

### Step 4: Trust Certificate (For Testing)

**On Linux:**
```bash
sudo cp /etc/ssl/certs/kai.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

**On macOS:**
```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain /etc/ssl/certs/kai.crt
```

---

## Option 3: Commercial Certificate

### Step 1: Generate Certificate Signing Request (CSR)

```bash
# Generate private key
sudo openssl genrsa -out /etc/ssl/private/kai.key 2048

# Generate CSR
sudo openssl req -new -key /etc/ssl/private/kai.key \
  -out kai.csr
```

You'll be prompted for:
- Country Name (2 letter code)
- State or Province
- Locality (city)
- Organization Name
- Organizational Unit
- Common Name (your domain: kai.example.com)
- Email Address

### Step 2: Submit CSR to Certificate Authority

1. Copy the contents of `kai.csr`
2. Submit to your certificate provider (DigiCert, Comodo, etc.)
3. Complete domain validation
4. Download certificate files

### Step 3: Install Certificate

You'll receive:
- Your certificate (kai.crt)
- Intermediate certificate (intermediate.crt)
- Root certificate (root.crt)

```bash
# Copy certificates
sudo cp kai.crt /etc/ssl/certs/
sudo cp intermediate.crt /etc/ssl/certs/
sudo cp root.crt /etc/ssl/certs/

# Create certificate chain
sudo cat /etc/ssl/certs/kai.crt \
  /etc/ssl/certs/intermediate.crt \
  /etc/ssl/certs/root.crt > /etc/ssl/certs/kai-chain.crt

# Set permissions
sudo chmod 600 /etc/ssl/private/kai.key
sudo chmod 644 /etc/ssl/certs/kai-chain.crt
```

### Step 4: Update Nginx Configuration

```nginx
ssl_certificate /etc/ssl/certs/kai-chain.crt;
ssl_certificate_key /etc/ssl/private/kai.key;
ssl_trusted_certificate /etc/ssl/certs/intermediate.crt;
```

---

## Nginx Configuration

### Generate Diffie-Hellman Parameters

```bash
# This takes several minutes
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
```

### Complete SSL Configuration

Use the provided configuration in `nginx/conf.d/kai-ssl.conf`:

```nginx
# Modern TLS configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers off;

# Session configuration
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;

# Diffie-Hellman parameter
ssl_dhparam /etc/ssl/certs/dhparam.pem;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

### Test and Reload Nginx

```bash
# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

---

## Testing SSL Configuration

### 1. Basic Connection Test

```bash
# Test HTTPS connection
curl -I https://kai.example.com

# Test SSL handshake
openssl s_client -connect kai.example.com:443 -showcerts
```

### 2. SSL Labs Test

Visit: https://www.ssllabs.com/ssltest/

Enter your domain and wait for the comprehensive test to complete.
**Target: A+ rating**

### 3. Security Headers Test

Visit: https://securityheaders.com/

Enter your domain to check security headers.
**Target: A+ rating**

### 4. Certificate Validation

```bash
# Check certificate details
openssl x509 -in /etc/ssl/certs/kai.crt -text -noout

# Verify certificate chain
openssl verify -CAfile /etc/ssl/certs/ca-chain.crt /etc/ssl/certs/kai.crt
```

### 5. Browser Test

1. Visit https://kai.example.com in a browser
2. Click the padlock icon
3. Verify certificate details
4. Check for mixed content warnings

---

## Certificate Renewal

### Let's Encrypt (Automatic)

Certbot automatically renews certificates. To manually renew:

```bash
# Dry run test
sudo certbot renew --dry-run

# Force renewal (if certificate expires in <30 days)
sudo certbot renew

# Force renewal regardless of expiry
sudo certbot renew --force-renewal
```

### Commercial Certificate

1. Check expiry date:
   ```bash
   openssl x509 -in /etc/ssl/certs/kai.crt -noout -dates
   ```

2. Set calendar reminder 30 days before expiry

3. Follow the same process as initial installation

### Certificate Expiry Monitoring

Add to cron for alerts:

```bash
# Create monitoring script
cat > /usr/local/bin/check-ssl-expiry.sh << 'EOF'
#!/bin/bash
DOMAIN="kai.example.com"
DAYS_WARNING=30

EXPIRY_DATE=$(openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | \
  openssl x509 -noout -dates | grep notAfter | cut -d= -f2)

EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt $DAYS_WARNING ]; then
  echo "WARNING: SSL certificate for $DOMAIN expires in $DAYS_LEFT days!"
  # Send alert email
  # echo "Certificate expires soon!" | mail -s "SSL Alert" admin@example.com
fi
EOF

# Make executable
sudo chmod +x /usr/local/bin/check-ssl-expiry.sh

# Add to crontab (check daily at 9 AM)
sudo crontab -e
# Add: 0 9 * * * /usr/local/bin/check-ssl-expiry.sh
```

---

## Troubleshooting

### Certificate Not Trusted

**Symptom:** Browser shows "Not Secure" or certificate error

**Solutions:**
1. Verify certificate chain is complete
2. Check intermediate certificate is included
3. Verify certificate is for correct domain
4. Clear browser cache

### Mixed Content Warnings

**Symptom:** Some resources load over HTTP instead of HTTPS

**Solutions:**
1. Update all resource URLs to use HTTPS
2. Use protocol-relative URLs (`//example.com/resource`)
3. Update Content-Security-Policy to upgrade insecure requests

### OCSP Stapling Not Working

**Test:**
```bash
openssl s_client -connect kai.example.com:443 -status
```

**Solutions:**
1. Verify `ssl_stapling on` in nginx config
2. Check DNS resolver configuration
3. Verify firewall allows outbound OCSP connections

### SSL Handshake Failures

**Symptoms:** Connection timeouts or handshake errors

**Solutions:**
1. Verify certificate and key match:
   ```bash
   openssl x509 -noout -modulus -in /etc/ssl/certs/kai.crt | openssl md5
   openssl rsa -noout -modulus -in /etc/ssl/private/kai.key | openssl md5
   # The output should match
   ```

2. Check nginx error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. Verify SSL protocols:
   ```bash
   nmap --script ssl-enum-ciphers -p 443 kai.example.com
   ```

### Permission Denied Errors

**Symptom:** Nginx fails to start with SSL errors

**Solutions:**
```bash
# Fix certificate permissions
sudo chown root:root /etc/ssl/private/kai.key
sudo chmod 600 /etc/ssl/private/kai.key
sudo chmod 644 /etc/ssl/certs/kai.crt

# Verify nginx can access certificates
sudo -u nginx cat /etc/ssl/private/kai.key > /dev/null
```

### Port 443 Already in Use

**Check what's using the port:**
```bash
sudo lsof -i :443
sudo netstat -tulpn | grep :443
```

**Solution:** Stop conflicting service or reconfigure port

---

## Security Best Practices

1. **Keep private keys secure**
   - Never commit to version control
   - Restrict file permissions (600)
   - Use hardware security modules (HSM) for high-security environments

2. **Monitor certificate expiry**
   - Set up automated monitoring
   - Alert 30 days before expiry

3. **Use strong ciphers**
   - Disable SSLv3, TLS 1.0, TLS 1.1
   - Use modern cipher suites
   - Prefer forward secrecy

4. **Enable HSTS**
   - Start with low max-age during testing
   - Increase to 1 year in production
   - Consider HSTS preloading

5. **Regular testing**
   - Run SSL Labs test monthly
   - Monitor for new vulnerabilities
   - Update TLS configuration as needed

---

## Additional Resources

- Let's Encrypt Documentation: https://letsencrypt.org/docs/
- Mozilla SSL Configuration Generator: https://ssl-config.mozilla.org/
- SSL Labs Testing: https://www.ssllabs.com/ssltest/
- OWASP TLS Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html

---

**Last Updated:** October 2024
