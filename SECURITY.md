# Security Summary

## Overview

This document outlines the security measures implemented in the Naukri Scraper application and provides guidance for secure usage.

## Security Measures Implemented

### 1. SSRF (Server-Side Request Forgery) Protection

**Location**: `ai_integration.py` - `_validate_webhook_url()` method

**Protection**:
- URL validation before making HTTP requests to webhooks
- Blocks private IP ranges (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
- Blocks localhost addresses (127.0.0.1, localhost, 0.0.0.0)
- Blocks link-local addresses (169.254.x.x, fe80:, ::1)
- Only allows http and https schemes
- Development override available via `ALLOW_LOCAL_WEBHOOKS` flag

**Why**: Prevents attackers from using the webhook feature to scan internal networks or access private services.

**Configuration**:
```bash
# In .env file
# Set to True only for local development
ALLOW_LOCAL_WEBHOOKS=False  # Default: False for production
```

### 2. Credential Management

**Protection**:
- Credentials stored in `.env` file (excluded from version control)
- `.gitignore` prevents accidental commits of sensitive data
- Environment variables used for all secrets
- Password input hidden in CLI prompts

**Best Practices**:
- Never commit `.env` file to version control
- Use strong, unique passwords for Naukri employer accounts
- Rotate credentials regularly
- Use different credentials for development and production

### 3. Webhook Authentication

**Protection**:
- Optional webhook secret for verifying webhook authenticity
- Secret verification in callback endpoint
- Prevents unauthorized webhook callbacks

**Configuration**:
```bash
# In .env file
WEBHOOK_SECRET=your-random-secret-key-here
```

**Usage**:
```python
# Webhook callbacks must include the secret
{
  "candidate_id": 1,
  "call_status": "completed",
  "secret": "your-random-secret-key-here"
}
```

### 4. Database Security

**Protection**:
- SQLite database with file permissions
- Parameterized queries via SQLAlchemy ORM (prevents SQL injection)
- No raw SQL queries that concatenate user input

**Recommendations**:
- Set appropriate file permissions on `naukri_profiles.db`
- For production, consider PostgreSQL with proper authentication
- Regular database backups

### 5. API Security

**Features**:
- CORS configuration for controlled access
- Secret key for Flask sessions
- Request timeout limits
- Rate limiting should be implemented (see recommendations)

**Configuration**:
```bash
# In .env file
API_SECRET_KEY=change-me-in-production
```

### 6. Input Validation

**Protection**:
- Type checking with Pydantic models
- URL validation for webhooks
- Timeout limits on HTTP requests
- File path validation for exports

## Known Security Considerations

### CodeQL Alert: SSRF in webhook URLs

**Status**: Mitigated with validation

**Alert**: CodeQL flags the `requests.post()` call in `send_to_webhook()` as potentially vulnerable to SSRF.

**Mitigation**: 
- Comprehensive URL validation implemented in `_validate_webhook_url()`
- Private IPs, localhost, and unsafe schemes are blocked
- Validation happens before any HTTP request is made
- Development override requires explicit configuration

**False Positive Rationale**:
The CodeQL tool cannot recognize custom validation logic. The SSRF risk is mitigated by:
1. URL parsing and validation
2. Hostname checking against blocklists
3. IP range filtering
4. Scheme validation

## Security Best Practices

### For Deployment

1. **Environment Variables**:
   ```bash
   # Production settings
   HEADLESS_MODE=True
   API_DEBUG=False
   ALLOW_LOCAL_WEBHOOKS=False
   ```

2. **File Permissions**:
   ```bash
   chmod 600 .env
   chmod 600 naukri_profiles.db
   chmod 700 exports/
   ```

3. **HTTPS Only**:
   - Use HTTPS for all webhook URLs in production
   - Configure reverse proxy (nginx/Apache) with SSL/TLS

4. **API Authentication**:
   - Implement additional authentication (JWT, API keys) for production API
   - Consider rate limiting with Flask-Limiter
   - Use a production WSGI server (gunicorn, uwsgi)

5. **Secrets Management**:
   - Use a secrets manager (AWS Secrets Manager, HashiCorp Vault) for production
   - Rotate API keys and passwords regularly
   - Use different credentials per environment

### For Development

1. **Local Testing**:
   ```bash
   # For local webhook testing
   ALLOW_LOCAL_WEBHOOKS=True
   ```

2. **Test Credentials**:
   - Use test/sandbox accounts when available
   - Never use production credentials in development

3. **Code Review**:
   - Review all webhook URLs before sending data
   - Validate input data before processing
   - Test with malicious inputs

## Recommended Additional Security Measures

### 1. Rate Limiting

Implement rate limiting to prevent abuse:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/scrape', methods=['POST'])
@limiter.limit("10 per hour")
def scrape_profiles():
    # ...
```

### 2. API Authentication

Add JWT or API key authentication:

```python
from functools import wraps
from flask import request

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/candidates', methods=['POST'])
@require_api_key
def add_candidate():
    # ...
```

### 3. Audit Logging

Log security-relevant events:

```python
import logging

security_logger = logging.getLogger('security')
security_logger.info(f"API access from {request.remote_addr}")
security_logger.warning(f"Failed webhook validation: {webhook_url}")
```

### 4. Data Encryption

Encrypt sensitive candidate data:

```python
from cryptography.fernet import Fernet

# Encrypt sensitive fields before storing
cipher = Fernet(key)
encrypted_email = cipher.encrypt(email.encode())
```

### 5. HTTPS for API

Use HTTPS for API in production:

```python
# Force HTTPS
from flask_talisman import Talisman

talisman = Talisman(app, force_https=True)
```

## Vulnerability Reporting

If you discover a security vulnerability:

1. **Do Not** open a public issue
2. Email security concerns to: [your-security-email]
3. Include detailed description and steps to reproduce
4. Allow reasonable time for response before public disclosure

## Security Updates

- Review dependencies regularly: `pip list --outdated`
- Update packages with security fixes: `pip install --upgrade [package]`
- Monitor security advisories for dependencies
- Test updates in development before deploying to production

## Compliance Considerations

### Data Privacy

- **GDPR**: If processing EU citizens' data, ensure compliance
  - Right to erasure (implement deletion methods)
  - Data portability (export feature exists)
  - Consent management
  
- **Local Regulations**: Check regulations in your jurisdiction regarding:
  - Job candidate data storage
  - Automated decision making
  - Data retention periods

### Terms of Service

- Comply with Naukri.com Terms of Service
- Respect rate limits and access restrictions
- Obtain necessary permissions before contacting candidates
- Use data only for legitimate recruitment purposes

## Security Checklist for Deployment

- [ ] All credentials in environment variables
- [ ] `.env` file not committed to version control
- [ ] `ALLOW_LOCAL_WEBHOOKS=False` in production
- [ ] `API_DEBUG=False` in production
- [ ] Strong `API_SECRET_KEY` set
- [ ] `WEBHOOK_SECRET` configured
- [ ] HTTPS enabled for API
- [ ] Database file permissions restricted
- [ ] Export directory secured
- [ ] Regular backups configured
- [ ] Monitoring and logging enabled
- [ ] Rate limiting implemented
- [ ] API authentication added
- [ ] Security updates applied

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/latest/faq/security.html)

## Contact

For security concerns: [your-contact-information]

Last Updated: 2024-12-10
