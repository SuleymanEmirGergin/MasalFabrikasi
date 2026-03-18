# Service Level Agreement (SLA)

## 📊 Uptime Commitments

### Standard Plan
- **Uptime**: 99.5% (Monthly)
- **Max Downtime**: ~3.6 hours/month
- **Response Time**: < 2 seconds (p95)

### Premium Plan
- **Uptime**: 99.9% (Monthly)
- **Max Downtime**: ~43 minutes/month
- **Response Time**: < 1 second (p95)

### Enterprise Plan
- **Uptime**: 99.95% (Monthly)
- **Max Downtime**: ~21 minutes/month
- **Response Time**: < 500ms (p95)
- **Dedicated Support**: 24/7

---

## ⏱️ Response Time Targets

### API Endpoints

| Endpoint Type | Standard | Premium | Enterprise |
|--------------|----------|---------|------------|
| Health Check | < 100ms | < 50ms | < 30ms |
| Story List | < 500ms | < 300ms | < 200ms |
| Story Detail | < 300ms | < 200ms | < 150ms |
| Story Generation | < 30s | < 20s | < 15s |
| Image Generation | < 60s | < 45s | < 30s |

### Success Rate

- **Standard**: 99.5% of requests succeed
- **Premium**: 99.9% of requests succeed
- **Enterprise**: 99.95% of requests succeed

---

## 🔧 Maintenance Windows

### Scheduled Maintenance
- **Frequency**: Monthly (first Tuesday)
- **Time**: 02:00 - 04:00 UTC
- **Duration**: Max 2 hours
- **Notification**: 7 days advance notice

### Emergency Maintenance
- **Notification**: 4 hours advance (if possible)
- **Duration**: As needed
- **Credits**: Downtime credited if > 30 minutes

---

## 💰 SLA Credits

### Downtime Credits

| Uptime Achieved | Credit % |
|----------------|----------|
| < 99.95% | 10% |
| < 99.9% | 25% |
| < 99.5% | 50% |
| < 99.0% | 100% |

### How to Claim
1. Submit ticket within 30 days
2. Provide evidence of downtime
3. Credits applied to next invoice

### Exclusions
- Scheduled maintenance
- User's internet/network issues
- Third-party service failures (OpenAI, etc.)
- Force majeure events

---

## 📞 Support Response Times

### Priority Levels

**P1 - Critical** (Service Down):
- **Standard**: 4 hours
- **Premium**: 1 hour
- **Enterprise**: 15 minutes

**P2 - High** (Major Feature Down):
- **Standard**: 8 hours
- **Premium**: 4 hours
- **Enterprise**: 1 hour

**P3 - Medium** (Minor Issue):
- **Standard**: 24 hours
- **Premium**: 12 hours
- **Enterprise**: 4 hours

**P4 - Low** (Question/Enhancement):
- **Standard**: 48 hours
- **Premium**: 24 hours
- **Enterprise**: 8 hours

---

## 🔒 Security Commitments

### Data Protection
- **Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Backups**: Daily automated backups
- **Retention**: 30 days
- **Geographic**: EU data stays in EU

### Compliance
- GDPR compliant
- SOC 2 Type II (in progress)
- ISO 27001 (planned)

### Incident Response
- **Detection**: < 5 minutes
- **Notification**: < 1 hour for data breaches
- **Resolution**: < 24 hours

---

## 📈 Performance Metrics

### Monthly Reports Include

1. **Uptime Percentage**
2. **Average Response Times** (p50, p95, p99)
3. **Error Rates**
4. **Incident Count & Resolution Times**
5. **Feature Availability**

### Real-Time Status

- Status Page: `status.masalfabrikasi.app`
- Subscribeto updates via email/SMS
- API endpoint: `GET /health/detailed`

---

## 🎯 Feature Availability

### Core Features (99.9% uptime)
- Story generation (sync mode)
- Story listing
- User authentication
- Health checks

### Premium Features (99.5% uptime)
- Voice cloning
- Advanced analytics
- Magic canvas
- Character chat

### Experimental Features (Best Effort)
- Beta/alpha features
- No uptime guarantee
- May be disabled anytime

---

## 🔄 Data Recovery

### Recovery Time Objective (RTO)
- **Standard**: 4 hours
- **Premium**: 1 hour
- **Enterprise**: 30 minutes

### Recovery Point Objective (RPO)
- **Standard**: 24 hours (daily backups)
- **Premium**: 12 hours (twice-daily backups)
- **Enterprise**: 1 hour (continuous backup)

---

## 📋 Capacity Limits

### API Rate Limits

| Plan | Requests/Min | Stories/Day | Storage |
|------|--------------|-------------|---------|
| Free | 10 | 10 | 100 MB |
| Standard | 60 | 100 | 1 GB |
| Premium | 300 | 500 | 10 GB |
| Enterprise | Custom | Unlimited | Unlimited |

### Overage Handling
- Soft limit: Warning notification
- Hard limit: 429 Too Many Requests
- Upgrade options available

---

## 📞 Contact

### Support Channels

**Standard**:
- Email: support@masalfabrikasi.app
- Documentation: docs.masalfabrikasi.app

**Premium**:
- Priority email
- Live chat (business hours)

**Enterprise**:
- Dedicated account manager
- Direct phone line
- Slack channel

### Emergency Contact
- **Critical Issues**: +90 XXX XXX XX XX
- **Available**: 24/7 (Enterprise only)

---

*Last Updated: 2026-01-02*
*Effective Date: 2026-01-01*
*Review Date: 2026-07-01*
