# Security Guidelines

## SSRF Protection

NaukriScapper implements Server-Side Request Forgery (SSRF) protection for webhook integrations to prevent malicious actors from exploiting the application to make requests to internal systems.

### How It Works

The webhook URL validation mechanism blocks:
- Localhost addresses (localhost, 127.0.0.1, ::1)
- Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Link-local addresses (169.254.0.0/16)
- Invalid URL schemes (only http and https are allowed)

### Configuration

By default, SSRF protection is **enabled** and blocks all local/private addresses.

For **development purposes only**, you can disable this protection:

```bash
export ALLOW_LOCAL_WEBHOOKS=True
```

Or in your `.env` file:
```
ALLOW_LOCAL_WEBHOOKS=True
```

### Production Deployment

⚠️ **WARNING**: Never set `ALLOW_LOCAL_WEBHOOKS=True` in production environments!

This setting bypasses critical security controls and exposes your application to SSRF attacks.

### Webhook URL Examples

**Blocked URLs** (in production):
- http://localhost:8000/webhook
- http://127.0.0.1:5000/callback
- http://192.168.1.100/api
- http://10.0.0.5/endpoint

**Allowed URLs**:
- https://hooks.n8n.cloud/webhook/your-webhook-id
- https://hook.us1.make.com/your-webhook-id
- https://your-domain.com/webhook/callback

## API Security

### Rate Limiting

The scraper implements a default delay of 2 seconds between requests to avoid overwhelming target servers and respect rate limits.

```python
scraper = NaukriScraper(delay=2.0)
```

### Database Security

- Use strong database credentials
- Enable SSL/TLS for database connections in production
- Regularly backup your database
- Use environment variables for sensitive configuration

### Environment Variables

Never commit sensitive data to version control. Use environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/naukri_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Webhook URLs
WEBHOOK_URL=https://your-webhook.com/callback
N8N_WEBHOOK_URL=https://hooks.n8n.cloud/webhook/your-id
MAKE_WEBHOOK_URL=https://hook.us1.make.com/your-id

# Security
ALLOW_LOCAL_WEBHOOKS=False  # Must be False in production
```

## Reporting Security Issues

If you discover a security vulnerability, please email: dwaith.dev@gmail.com

Do not create public GitHub issues for security vulnerabilities.

## Best Practices

1. **Keep dependencies updated**: Regularly update Python packages
2. **Use HTTPS**: Always use HTTPS for webhooks in production
3. **Validate input**: The application validates webhook URLs, but always validate user input
4. **Monitor logs**: Review call logs and webhook responses regularly
5. **Principle of least privilege**: Run the application with minimal required permissions
6. **Secure API endpoints**: Implement authentication for API endpoints in production
7. **Rate limiting**: Implement rate limiting for API endpoints to prevent abuse

## Security Checklist

Before deploying to production:

- [ ] Set `ALLOW_LOCAL_WEBHOOKS=False`
- [ ] Use HTTPS for all webhook URLs
- [ ] Configure strong database credentials
- [ ] Enable database SSL/TLS
- [ ] Set up API authentication
- [ ] Implement rate limiting
- [ ] Review and sanitize all logs
- [ ] Set up monitoring and alerting
- [ ] Regularly update dependencies
- [ ] Conduct security audit

## References

- [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
