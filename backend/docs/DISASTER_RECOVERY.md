# Disaster Recovery Plan (DRP)

## 🚨 Disasters Recovery Senaryoları

### 1. Database Failure

**Senaryo**: PostgreSQL veritabanı erişilemez hale gelir

**Recovery Steps**:
1. **Immediate (< 5 min)**:
   - Health check failure tespit eder
   - Auto-failover başlatılır (replica varsa)
   - Kullanıcılara maintenance modu gösterilir

2. **Restore from Backup (5-30 min)**:
   ```bash
   # En son backup'ı tespit et
   cd backups/
   ls -lt | head -n 1
   
   # Restore et
   python scripts/backup_database.py restore <backup-file>
   
   # Verify
   docker-compose exec backend python -c "from app.core.database import engine; engine.connect()"
   ```

3. **Verification**:
   - Test kullanıcısı ile login
   - Hikaye listeleme çalışıyor mu?
   - Yeni hikaye oluşturma çalışıyor mu?

**Prevention**:
- Günlük otomatik backup (cron)
- Read replica setup
- Point-in-time recovery (PITR) enabled

---

### 2. Redis Failure

**Senaryo**: Redis cache/queue erişilemez

**Impact**: 
- Cache misses (performance düşer ama çalışır)
- Celery job queue çalışmaz
- Rate limiting çalışmaz

**Recovery Steps**:
1. **Restart Redis**:
   ```bash
   docker-compose restart redis
   ```

2. **Verify**:
   ```bash
   redis-cli ping
   # Response: PONG
   ```

3. **Check Celery Workers**:
   ```bash
   celery -A app.celery_app inspect active
   ```

**Prevention**:
- Redis persistence enabled (AOF + RDB)
- Redis Sentinel for auto-failover
- Regular backup of Redis data

---

### 3. API Server Crash

**Senaryo**: FastAPI application crash

**Recovery Steps**:
1. **Auto-restart** (Docker/Kubernetes otomatik yapar)
   
2. **Manual Restart**:
   ```bash
   docker-compose restart backend
   ```

3. **Check Logs**:
   ```bash
   docker-compose logs --tail=100 backend
   ```

4. **Verify Health**:
   ```bash
   curl http://localhost:8000/health/detailed
   ```

**Prevention**:
- Health checks enabled
- Auto-restart policy
- Load balancer multiple instances

---

### 4. Complete Infrastructure Failure

**Senaryo**: Tüm server erişilemez (data center down)

**Recovery Steps** (Secondary Region):
1. **Deploy to Secondary Region** (< 1 hour):
   ```bash
   # Deploy to backup region
   cd infrastructure/
   terraform apply -var="region=eu-central-1"
   ```

2. **Restore Latest Backup**:
   - Database: Latest automated backup
   - Files: Supabase storage (geo-replicated)
   
3. **Update DNS**:
   - Point domain to new IP
   - TTL: 300 seconds for quick propagation

4. **Verify All Services**:
   - API health check
   - Database connectivity
   - Redis connectivity
   - Celery workers running

**RTO (Recovery Time Objective)**: 1 hour
**RPO (Recovery Point Objective)**: 24 hours (daily backups)

---

## 🔄 Backup Strategy

### Automated Backups

**Daily Backups**:
```bash
# Crontab entry
0 2 * * * cd /app/backend && python scripts/backup_database.py >> /var/log/backup.log 2>&1
```

**Backup Retention**:
- Daily: Keep for 7 days
- Weekly: Keep for 4 weeks
- Monthly: Keep for 12 months

**Backup Locations**:
1. Local: `/app/backups/`
2. S3/Cloud Storage: `s3://masal-backups/database/`
3. Offsite: Separate cloud provider

### Backup Testing

**Monthly Restore Test**:
```bash
# 1. Create test database
createdb test_restore

# 2. Restore latest backup
pg_restore -d test_restore backups/latest.sql

# 3. Verify data integrity
psql test_restore -c "SELECT COUNT(*) FROM stories;"

# 4. Cleanup
dropdb test_restore
```

---

## 📊 Monitoring & Alerts

### Critical Alerts (Page Immediately)

1. **API Down**: Health check fails for 2 minutes
2. **Database Unreachable**: Connection failures
3. **Disk Space**: < 10% free space
4. **Error Rate**: > 5% of requests fail

### Warning Alerts (Email/Slack)

1. **High Response Time**: p95 > 5 seconds
2. **Low Disk Space**: < 20% free
3. **Failed Backups**: Backup script fails
4. **High Memory**: > 85% usage

### Alert Channels

- **PagerDuty**: Critical alerts
- **Slack**: Warnings and info
- **Email**: Daily summary

---

## 👥 Contact Information

### On-Call Schedule

- **Primary**: [Name] - [Phone]
- **Secondary**: [Name] - [Phone]
- **Manager**: [Name] - [Phone]

### Escalation Path

1. On-call engineer (0-15 min)
2. Team lead (15-30 min)
3. Engineering manager (30-60 min)
4. CTO (> 60 min)

---

## 📝 Incident Response Checklist

### Phase 1: Detection (0-5 min)
- [ ] Alert received and acknowledged
- [ ] Incident severity assessed
- [ ] Team notified (if critical)

### Phase 2: Triage (5-15 min)
- [ ] Impact identified (users affected, features down)
- [ ] Root cause hypothesis formed
- [ ] Mitigation strategy decided

### Phase 3: Resolution (15-60 min)
- [ ] Mitigation applied
- [ ] Services restored
- [ ] Verification completed
- [ ] Customers notified (if needed)

### Phase 4: Post-Mortem (24-48 hours)
- [ ] Timeline documented
- [ ] Root cause analysis completed
- [ ] Action items identified
- [ ] Prevention measures planned

---

## 🔐 Security Incidents

### Data Breach

1. **Immediate**:
   - Isolate affected systems
   - Change all passwords/keys
   - Notify security team

2. **Investigation**:
   - Audit logs review
   - Scope of breach determined
   - Affected users identified

3. **Notification**:
   - Legal team informed
   - Users notified (GDPR compliance)
   - Authorities notified (if required)

---

## 📈 Recovery Verification

### Post-Recovery Checklist

- [ ] All services responding
- [ ] Health checks passing
- [ ] Error rates normal
- [ ] Performance metrics baseline
- [ ] Data integrity verified
- [ ] Users can access application
- [ ] Background jobs processing
- [ ] Monitoring alerts cleared

### Success Criteria

- RTO met (< target recovery time)
- RPO met (< target data loss)
- No data corruption
- All features functional
- Performance acceptable

---

*Last Updated: 2026-01-02*
*Review Frequency: Quarterly*
*Next Review: 2026-04-02*
