# Security & Privacy Guide

## Security Measures Implemented

### 1. Authentication & Authorization
- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ Refresh token mechanism
- ✅ Role-based access control (RBAC) ready

### 2. API Security
- ✅ Rate limiting (100 requests/minute per IP)
- ✅ Input sanitization
- ✅ File upload validation
- ✅ CORS configuration
- ✅ Security headers (X-Frame-Options, CSP, etc.)

### 3. Data Encryption
- ✅ HTTPS/TLS for all communications
- ✅ Password hashing (bcrypt)
- ⏳ Database encryption at rest (configure in cloud provider)
- ⏳ Sensitive field encryption (PII)

### 4. Monitoring
- ✅ Sentry error tracking
- ✅ Access logs
- ⏳ Security audit logs
- ⏳ Intrusion detection

## GDPR/KVKK Compliance

### Data Collection
We collect:
- User account information (email, username)
- Story content created by users
- Usage analytics
- Device information (app version, OS)

### User Rights
Users have the right to:
1. **Access**: Request copy of their data
2. **Rectification**: Correct inaccurate data
3. **Erasure**: Delete their account and data
4. **Portability**: Export data in JSON format
5. **Opposition**: Opt-out of analytics

### Implementation Checklist

- [ ] Privacy Policy page
- [ ] Terms of Service page
- [ ] Cookie consent (if web version)
- [ ] Data deletion endpoint
- [ ] Data export endpoint
- [ ] Age verification (13+/parental consent)
- [ ] GDPR consent checkboxes

### Data Deletion API

```python
# Backend endpoint for GDPR data deletion
@router.delete("/user/{user_id}/data")
async def delete_user_data(user_id: str, current_user = Depends(get_current_user)):
    # Verify user owns the data
    if current_user != user_id:
        raise HTTPException(403, "Unauthorized")
    
    # Delete all user data
    # - Stories
    # - Characters
    # - Profile
    # - Analytics
    
    return {"message": "All user data deleted"}
```

### Data Export API

```python
@router.get("/user/{user_id}/export")
async def export_user_data(user_id: str, current_user = Depends(get_current_user)):
    # Export all data as JSON
    data = {
        "user": {...},
        "stories": [...],
        "characters": [...],
        "achievements": [...]
    }
    return data
```

## Security Checklist

### Backend
- [x] Use environment variables for secrets
- [x] Implement JWT authentication
- [x] Add rate limiting
- [x] Validate all inputs
- [x] Sanitize user content
- [x] Use parameterized queries (prevent SQL injection)
- [x] Enable CORS selectively
- [ ] Implement API key rotation
- [ ] Set up WAF (Web Application Firewall)
- [ ] Enable audit logging

### Frontend
- [x] Store tokens securely (AsyncStorage with encryption)
- [x] Validate inputs client-side
- [ ] Implement biometric authentication (Face ID, Touch ID)
- [ ] Certificate pinning for API calls
- [ ] Obfuscate code for production builds
- [ ] Implement jailbreak/root detection

### Infrastructure
- [ ] Enable DDoS protection (Cloudflare)
- [ ] Regular security scans (Snyk, OWASP ZAP)
- [ ] Automated backups
- [ ] Disaster recovery plan
- [ ] Penetration testing

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@masal-fabrikasi.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond within 48 hours.

## Security Updates

- Check dependencies regularly: `npm audit`, `pip-audit`
- Subscribe to security advisories
- Apply patches promptly
- Review and rotate secrets quarterly

## Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- GDPR Guide: https://gdpr.eu/
- KVKK (Turkey): https://kvkk.gov.tr/
