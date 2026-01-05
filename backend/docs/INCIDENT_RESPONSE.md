# Incident Response Plan

## 🚨 Incident Severity Levels

### SEV-1: Critical
**Definition**: Complete service outage or data loss
**Examples**:
- API completely down
- Database unreachable
- Data breach detected
- Payment system failure

**Response**:
- **Time to Acknowledge**: < 5 minutes
- **Time to Triage**: < 15 minutes
- **Communication**: Immediate status page update
- **Team**: All hands on deck

---

### SEV-2: High
**Definition**: Major feature broken, significant user impact
**Examples**:
- Story generation failing
- Authentication not working
- High error rate (> 10%)
- Performance severely degraded

**Response**:
- **Time to Acknowledge**: < 15 minutes
- **Time to Triage**: < 30 minutes
- **Communication**: Status page + email to affected users
- **Team**: On-call + backend lead

---

### SEV-3: Medium
**Definition**: Minor feature broken, limited impact
**Examples**:
- Voice cloning not working
- Analytics dashboard slow
- Non-critical API errors

**Response**:
- **Time to Acknowledge**: < 1 hour
- **Time to Triage**: < 2 hours
- **Communication**: Internal only
- **Team**: On-call engineer

---

### SEV-4: Low
**Definition**: Cosmetic issues, no functional impact
**Examples**:
- UI glitches
- Typos
- Performance optimization opportunities

**Response**:
- **Time to Acknowledge**: < 4 hours
- **Communication**: Ticket system
- **Team**: Regular sprint planning

---

## 📋 Incident Response Workflow

### 1. Detection (0-5 min)

**Sources**:
- Automated monitoring alerts
- User reports
- Health check failures
- Error tracking (Sentry)

**Initial Actions**:
```bash
# Check immediate status
curl https://api.masalfabrikasi.app/health/detailed

# Check error logs
docker-compose logs --tail=100 backend | grep ERROR

# Check metrics
curl http://localhost:8000/metrics | grep error
```

**Decision**: Determine severity level

---

### 2. Acknowledgment (5-15 min)

**Actions**:
1. **Acknowledge Alert**:
   - Click "Acknowledge" in PagerDuty
   - Post in #incidents Slack channel

2. **Create Incident**:
   ```
   Title: [SEV-X] Brief description
   Start Time: 2026-01-02 17:00 UTC
   Assignee: On-call engineer
   ```

3. **Initial Communication**:
   - Update status page
   - Notify stakeholders (if SEV-1 or SEV-2)

---

### 3. Triage & Diagnosis (15-30 min)

**Goals**:
- Identify root cause
- Assess full impact
- Form mitigation plan

**Investigation Checklist**:
- [ ] Check recent deployments
- [ ] Review error logs
- [ ] Analyze metrics/graphs
- [ ] Check external dependencies
- [ ] Review recent config changes

**Commands**:
```bash
# Check recent deployments
git log --oneline -10

# Database status
docker-compose exec backend python -c "from app.core.database import engine; print(engine.pool.status())"

# Redis status
redis-cli INFO

# Celery workers
celery -A app.celery_app inspect active
```

---

### 4. Mitigation (30-60 min)

**Priority**: Stop the bleeding first

**Common Mitigations**:

1. **Rollback Deployment**:
   ```bash
   git revert HEAD
   docker-compose up -d --build
   ```

2. **Disable Feature**:
   ```bash
   # Set feature flag
   export FEATURE_EXPERIMENTAL_AI=false
   docker-compose restart backend
   ```

3. **Scale Up**:
   ```bash
   docker-compose up -d --scale backend=3
   ```

4. **Database Recovery**:
   ```bash
   python scripts/backup_database.py restore latest.sql
   ```

5. **Emergency Maintenance**:
   - Enable maintenance mode
   - Fix issue offline
   - Re-enable service

---

### 5. Communication

**Status Page Updates**:

```markdown
[INVESTIGATING] We're investigating reports of slow response times.
Updated: 17:05 UTC

[IDENTIFIED] The issue has been identified as a database connection pool exhaustion.
Updated: 17:15 UTC

[MONITORING] A fix has been deployed. We're monitoring the situation.
Updated: 17:30 UTC

[RESOLVED] The issue has been fully resolved. All systems operational.
Updated: 17:45 UTC
```

**User Communication** (SEV-1/SEV-2):
```
Subject: Service Disruption - [Date]

We experienced a service disruption today from 17:00 to 17:45 UTC.

What happened:
- Story generation was unavailable

Impact:
- ~500 users affected
- No data loss

Resolution:
- Database connection pool increased
- Service fully restored

We apologize for the inconvenience.
```

---

### 6. Resolution Verification

**Checklist**:
- [ ] Error rate back to normal
- [ ] Response times acceptable
- [ ] Health checks passing
- [ ] User reports stopped
- [ ] Monitoring green
- [ ] No new alerts

**Verification Commands**:
```bash
# Check health
curl https://api.masalfabrikasi.app/health/detailed

# Test critical flows
curl -X POST https://api.masalfabrikasi.app/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{"theme": "test", "language": "tr"}'

# Check metrics
curl http://localhost:8000/metrics | grep http_requests_total
```

---

### 7. Post-Mortem (24-48 hours)

**Required for**: SEV-1 and SEV-2 incidents

**Template**:
```markdown
# Post-Mortem: [Incident Title]

## Summary
Brief description of what happened

## Timeline
- 17:00 UTC: Incident started
- 17:05 UTC: Alert triggered
- 17:10 UTC: Investigation began
- 17:30 UTC: Fix deployed
- 17:45 UTC: Incident resolved

## Root Cause
Detailed explanation of what caused the incident

## Impact
- Duration: 45 minutes
- Users affected: ~500
- Requests failed: ~2,000
- Revenue impact: $X

## Resolution
What was done to fix the issue

## Prevention
Action items to prevent recurrence:
1. [ ] Action item 1 (Owner: X, Due: Date)
2. [ ] Action item 2 (Owner: Y, Due: Date)

## Lessons Learned
- What went well
- What could be improved
```

---

## 🎯 Runbooks

### Common Incident Scenarios

#### API Slow Response

```bash
# 1. Check load
docker stats

# 2. Check Redis
redis-cli INFO stats

# 3. Check DB connections
psql -c "SELECT count(*) FROM pg_stat_activity;"

# 4. Check slow queries
psql -c "SELECT query, now() - query_start as duration FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;"

# 5. Restart workers if needed
docker-compose restart celery_worker
```

#### Database Connection Errors

```bash
# 1. Check DB status
docker-compose ps postgres

# 2. Check connection limit
psql -c "SHOW max_connections;"
psql -c "SELECT count(*) FROM pg_stat_activity;"

# 3. Increase pool size (temporary)
# Edit docker-compose.yml -> DATABASE_POOL_SIZE=50
docker-compose up -d backend

# 4. Kill idle connections
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '1 hour';"
```

---

## 📞 Escalation

### When to Escalate

- Issue not resolved within expected timeframe
- Need additional expertise
- Multiple systems affected
- Customer-facing impact not mitigated

### Escalation Path

1. **L1**: On-call engineer (0-30 min)
2. **L2**: Team lead (30-60 min)
3. **L3**: Engineering manager (60-120 min)
4. **L4**: CTO (> 120 min or severe impact)

---

*Last Updated: 2026-01-02*
*Review: Quarterly*
