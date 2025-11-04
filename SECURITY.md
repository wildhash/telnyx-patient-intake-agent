# Security Policy

## Security Considerations

This application handles sensitive healthcare data and should be deployed with appropriate security measures.

### Production Deployment Security Checklist

#### 1. Configuration Security
- [ ] Generate a strong, random `SECRET_KEY` (minimum 32 characters)
- [ ] Never commit `.env` files to version control
- [ ] Store sensitive credentials in a secure secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Rotate API keys regularly
- [ ] Use environment-specific configurations (dev, staging, production)

#### 2. Network Security
- [ ] **REQUIRED**: Use HTTPS for all production endpoints (Telnyx webhooks require HTTPS)
- [ ] Configure SSL/TLS certificates (Let's Encrypt recommended)
- [ ] Implement rate limiting on all public endpoints
- [ ] Use a Web Application Firewall (WAF)
- [ ] Restrict webhook endpoint access to Telnyx IP ranges

#### 3. Authentication & Authorization
- [ ] Implement API authentication (API keys, OAuth2, JWT)
- [ ] Add user authentication for dashboard access
- [ ] Implement role-based access control (RBAC)
- [ ] Use multi-factor authentication (MFA) for admin access
- [ ] Audit log all authentication attempts

#### 4. Data Protection
- [ ] Encrypt database at rest
- [ ] Use encrypted connections for all external services
- [ ] Implement data retention policies
- [ ] Secure backup procedures
- [ ] Regular security audits

#### 5. Webhook Security
**IMPORTANT**: The current implementation does NOT verify Telnyx webhook signatures.

To implement webhook verification:

```python
import telnyx
from flask import request

def verify_telnyx_signature(payload, signature):
    """Verify webhook signature using Telnyx public key"""
    try:
        # Verify using Telnyx SDK
        telnyx.Webhook.construct_event(
            payload,
            signature,
            Config.TELNYX_PUBLIC_KEY
        )
        return True
    except Exception as e:
        logger.error(f"Webhook verification failed: {e}")
        return False

@bp.route('/telnyx', methods=['POST'])
def telnyx_webhook():
    # Get signature from header
    signature = request.headers.get('telnyx-signature-ed25519')
    timestamp = request.headers.get('telnyx-timestamp')
    
    # Verify signature
    if not verify_telnyx_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process webhook...
```

See: https://developers.telnyx.com/docs/v2/development/verifying-webhooks

#### 6. HIPAA Compliance

If handling Protected Health Information (PHI):

- [ ] Conduct a HIPAA risk assessment
- [ ] Sign Business Associate Agreements (BAA) with all vendors
- [ ] Implement audit logging for all PHI access
- [ ] Encrypt PHI in transit and at rest
- [ ] Implement access controls and authentication
- [ ] Regular security training for all staff
- [ ] Incident response plan
- [ ] Data backup and disaster recovery plan

**Note**: Telnyx offers HIPAA-compliant services - contact them for BAA.

#### 7. Application Security
- [ ] Keep all dependencies up to date (`pip list --outdated`)
- [ ] Run security scanners (Bandit, Safety)
- [ ] Implement input validation on all endpoints
- [ ] Use parameterized database queries (already done with SQLAlchemy)
- [ ] Implement CSRF protection for web forms
- [ ] Set security headers (CSP, HSTS, X-Frame-Options, etc.)
- [ ] Disable debug mode in production

#### 8. Infrastructure Security
- [ ] Use a production WSGI server (Gunicorn/uWSGI)
- [ ] Run application as non-root user
- [ ] Use containerization (Docker) for isolation
- [ ] Implement monitoring and alerting
- [ ] Regular security patches and updates
- [ ] Backup verification and testing

### Known Security Limitations

1. **In-Memory Call State**: Call state is stored in-memory and will be lost on server restart. Use Redis for production.

2. **No Webhook Signature Verification**: Webhooks are not verified. Implement signature verification before production use.

3. **No Rate Limiting**: API endpoints lack rate limiting. Implement rate limiting to prevent abuse.

4. **Basic Authentication**: No authentication is implemented. Add authentication before exposing APIs publicly.

5. **SQLite Database**: SQLite is not suitable for production. Migrate to PostgreSQL or MySQL.

### Security Updates

We take security seriously. If you discover a security vulnerability, please email security@example.com instead of using the public issue tracker.

### Security Scanning

Run these tools before deployment:

```bash
# Check for known vulnerabilities in dependencies
pip install safety
safety check

# Static security analysis
pip install bandit
bandit -r . -ll

# Check for outdated packages
pip list --outdated
```

### Recommended Security Headers

Configure your web server (Nginx/Apache) to set these headers:

```nginx
# Nginx example
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;
```

### Monitoring & Incident Response

1. **Logging**: Implement comprehensive logging
2. **Monitoring**: Set up monitoring for unusual activity
3. **Alerting**: Configure alerts for security events
4. **Incident Response**: Have a plan for security incidents
5. **Regular Audits**: Conduct regular security audits

### Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [Telnyx Security](https://telnyx.com/security)
- [Flask Security](https://flask.palletsprojects.com/en/latest/security/)

---

**Remember**: Security is not a one-time setup. It requires ongoing attention and regular updates.
