# Security Hardening Documentation

## Overview
This document outlines the security measures implemented in the Ikodio ERP system to protect against common web vulnerabilities and ensure data protection.

## Implementation Date
November 3, 2025

## Security Features Implemented

### 1. Rate Limiting (Throttling) ✅

**Purpose**: Prevent brute force attacks and API abuse

**Implementation**:
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Login attempts: 5 attempts/minute
- Sensitive operations: 10 operations/minute

**Configuration** (`config/settings.py`):
```python
'DEFAULT_THROTTLE_CLASSES': [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle',
],
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',
    'user': '1000/hour',
    'login': '5/minute',
    'sensitive': '10/minute',
}
```

**Custom Throttle Classes** (`apps/core/throttling.py`):
- `LoginRateThrottle` - For login endpoints
- `SensitiveOperationThrottle` - For delete/export operations
- `BurstRateThrottle` - 60 requests/minute
- `SustainedRateThrottle` - 1000 requests/hour

**Usage in Views**:
```python
from apps.core.throttling import LoginRateThrottle

class LoginView(APIView):
    throttle_classes = [LoginRateThrottle]
```

### 2. Security Headers ✅

**Purpose**: Protect against XSS, clickjacking, MIME sniffing, and other attacks

**Middleware**: `SecurityHeadersMiddleware` in `apps/core/middleware.py`

**Headers Added**:
- **Content-Security-Policy**: Prevents XSS attacks
  ```
  default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; ...
  ```

- **X-Frame-Options**: `DENY` - Prevents clickjacking

- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing

- **X-XSS-Protection**: `1; mode=block` - Browser XSS protection

- **Referrer-Policy**: `strict-origin-when-cross-origin` - Controls referrer information

- **Permissions-Policy**: Disables unused browser features
  ```
  geolocation=(), microphone=(), camera=(), payment=()
  ```

- **Strict-Transport-Security** (HSTS): Forces HTTPS in production
  ```
  max-age=31536000; includeSubDomains; preload
  ```

### 3. Request Validation ✅

**Purpose**: Detect and block malicious requests

**Middleware**: `RequestValidationMiddleware` in `apps/core/middleware.py`

**Features**:
- **Request Size Limit**: 10MB maximum
- **Suspicious Pattern Detection**:
  - Path traversal attempts: `../`, `..\\`
  - XSS attempts: `<script>`, `</script>`, `javascript:`
  - Event handlers: `onerror=`, `onload=`
  - SQL injection patterns: `SELECT`, `UNION`, `DROP`, `INSERT`, `--`

**Response**: Returns `403 Forbidden` for suspicious requests

### 4. Audit Logging ✅

**Purpose**: Track all API requests for security monitoring

**Middleware**: `AuditLogMiddleware` in `apps/core/middleware.py`

**Logged Information**:
- HTTP method and path
- User ID (if authenticated)
- Client IP address
- Response status code
- Request duration (milliseconds)

**Log Levels**:
- `INFO`: Successful requests (2xx, 3xx)
- `WARNING`: Failed requests (4xx, 5xx)

**Example Log**:
```
API request: {'method': 'POST', 'path': '/api/v1/auth/login/', 'user_id': None, 'ip_address': '127.0.0.1', 'status_code': 200, 'duration_ms': 45}
```

### 5. IP Whitelisting (Optional) ✅

**Purpose**: Restrict admin access to specific IP addresses

**Middleware**: `IPWhitelistMiddleware` (disabled by default)

**Configuration** (`.env`):
```bash
ADMIN_IP_WHITELIST=127.0.0.1,192.168.1.100,10.0.0.5
```

**Enable in** `config/settings.py`:
```python
MIDDLEWARE = [
    ...
    'apps.core.middleware.IPWhitelistMiddleware',  # Uncomment to enable
]
```

### 6. CORS Configuration ✅

**Purpose**: Secure cross-origin resource sharing

**Settings**:
```python
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Never True in production
CORS_URLS_REGEX = r'^/api/.*$'  # Only API endpoints
```

**Allowed Headers**:
- accept, authorization, content-type
- x-csrftoken, x-requested-with

**Environment Variable** (`.env`):
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://erp.ikodio.com
```

### 7. Password Security ✅

**Purpose**: Ensure strong password hashing and validation

**Password Hashers** (Most secure first):
1. **Argon2** - Memory-hard algorithm (recommended)
2. PBKDF2 with SHA256
3. PBKDF2 with SHA1
4. BCrypt with SHA256

**Password Validators**:
- **UserAttributeSimilarityValidator**: Max 70% similarity to user attributes
- **MinimumLengthValidator**: Minimum 8 characters
- **CommonPasswordValidator**: Prevents common passwords
- **NumericPasswordValidator**: Prevents all-numeric passwords

**Installation**:
```bash
pip install argon2-cffi
```

### 8. Session Security ✅

**Settings**:
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'  # Redis-backed
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_COOKIE_SECURE = True  # HTTPS only (production)
```

### 9. CSRF Protection ✅

**Settings**:
```python
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read for API calls
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True  # HTTPS only (production)
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'https://erp.ikodio.com']
```

### 10. Production Security Settings ✅

**Enabled when DEBUG=False**:
```python
SECURE_SSL_REDIRECT = True  # Force HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

**Additional Settings**:
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## Security Checklist

### Development Environment
- [x] Rate limiting configured
- [x] Security headers enabled
- [x] Request validation active
- [x] Audit logging implemented
- [x] CORS properly configured
- [x] Strong password validation
- [x] Secure session management

### Production Environment (Before Deployment)
- [ ] Set `DEBUG = False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Update `CORS_ALLOWED_ORIGINS` to production domain
- [ ] Enable HTTPS/SSL
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Configure firewall rules
- [ ] Setup monitoring and alerting
- [ ] Regular security audits
- [ ] Implement backup strategy
- [ ] Configure fail2ban or similar
- [ ] Enable IP whitelist for admin (optional)
- [ ] Review all environment variables
- [ ] Setup rate limiting at reverse proxy level (nginx/cloudflare)

## Testing Security Features

### 1. Test Rate Limiting
```bash
# Test login throttling - should block after 5 attempts
for i in {1..10}; do
  curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}'
  echo "\nAttempt $i"
done
```

### 2. Test Security Headers
```bash
# Check headers
curl -I http://127.0.0.1:8000/api/v1/auth/login/

# Should see:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Content-Security-Policy: ...
```

### 3. Test Request Validation
```bash
# Try path traversal - should return 403
curl "http://127.0.0.1:8000/api/v1/users/?path=../../etc/passwd"

# Try XSS - should return 403
curl "http://127.0.0.1:8000/api/v1/search/?q=<script>alert(1)</script>"
```

### 4. Test CORS
```bash
# From different origin - should fail without proper CORS
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Origin: http://evil.com" \
  -H "Content-Type: application/json"
```

## Monitoring & Alerts

### Log Files to Monitor
- `logs/api_requests.log` - All API requests
- `logs/security.log` - Security events
- `logs/django.log` - General application logs

### Suspicious Activity Indicators
- Multiple failed login attempts from same IP
- Requests with suspicious patterns
- Abnormally high request rates
- Admin access from unknown IPs
- Repeated 403 Forbidden responses

### Recommended Monitoring Tools
- **Sentry**: Error tracking and monitoring
- **Prometheus + Grafana**: Metrics and visualization
- **ELK Stack**: Log aggregation and analysis
- **Fail2ban**: Automatic IP banning
- **CloudFlare**: DDoS protection and WAF

## Security Best Practices

### For Developers
1. Never commit `.env` files or secrets
2. Use environment variables for all sensitive data
3. Validate and sanitize all user inputs
4. Use parameterized queries (ORM) to prevent SQL injection
5. Keep dependencies up to date
6. Review code for security issues before deployment
7. Use HTTPS in all environments
8. Implement proper error handling (don't expose stack traces)

### For System Administrators
1. Regular security updates
2. Strong firewall rules
3. Disable unnecessary services
4. Regular backups
5. Monitor logs for suspicious activity
6. Implement intrusion detection
7. Use strong SSH keys
8. Regular penetration testing

## Compliance

### OWASP Top 10 Protection

1. **Injection** ✅ - ORM usage, input validation
2. **Broken Authentication** ✅ - JWT tokens, rate limiting, strong passwords
3. **Sensitive Data Exposure** ✅ - HTTPS, secure cookies, Argon2 hashing
4. **XML External Entities (XXE)** ✅ - JSON API only
5. **Broken Access Control** ✅ - Permission system, RBAC
6. **Security Misconfiguration** ✅ - Secure defaults, headers
7. **Cross-Site Scripting (XSS)** ✅ - CSP headers, input validation
8. **Insecure Deserialization** ✅ - JSON only, validation
9. **Using Components with Known Vulnerabilities** ✅ - Regular updates
10. **Insufficient Logging & Monitoring** ✅ - Audit logging, Sentry

## Incident Response Plan

### If Security Breach Detected:
1. **Immediate Actions**:
   - Isolate affected systems
   - Change all passwords and secrets
   - Revoke all active tokens
   - Enable IP whitelist

2. **Investigation**:
   - Review audit logs
   - Identify entry point
   - Assess damage scope
   - Document findings

3. **Remediation**:
   - Patch vulnerabilities
   - Restore from clean backups
   - Update security rules
   - Notify affected users

4. **Post-Incident**:
   - Conduct security review
   - Update procedures
   - Additional training
   - Implement lessons learned

## Contact

For security issues or vulnerabilities, please contact:
- **Security Team**: security@ikodio.com
- **Emergency**: +62-xxx-xxxx-xxxx

**Do not** publicly disclose security vulnerabilities.

## Version History

- **v1.0.0** (November 3, 2025): Initial security hardening implementation
  - Rate limiting
  - Security headers
  - Request validation
  - Audit logging
  - CORS configuration
  - Password security
  - Session security
  - CSRF protection
