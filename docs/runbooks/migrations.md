# Database Migration Rollback Guide

## ⚠️ Emergency Rollback Procedure

If a deployment fails due to database migration issues, follow these steps to revert changes.

### 1. Identify the Current Revision
Check the current Alembic revision in the database:
```bash
docker-compose exec backend alembic current
```

### 2. Rollback to Previous Revision
To undo the last migration (e.g., if you are on `010` and want to go back to `009`):
```bash
docker-compose exec backend alembic downgrade -1
```

To rollback to a specific revision (e.g., `008_add_auth_tokens`):
```bash
docker-compose exec backend alembic downgrade 008_add_auth_tokens
```

### 3. Verify Rollback
Run the verification script to ensure the state is consistent (note: this script expects the *latest* schema, so it might fail if you rolled back features, which is expected):
```bash
# Verify schema state manually if needed
docker-compose exec backend python scripts/verify_migrations.py
```

### 4. Restore Data (If Data Loss Occurred)
If the migration caused data loss (e.g., dropping a column without backup), restore from the latest backup:
```bash
# Stop services
docker-compose down

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U admin -d masalfabrikasi

# Restart services
docker-compose up -d
```

## 📜 Migration History

- **010_add_stripe_events**: Adds `processed_stripe_events` table for webhook idempotency.
- **009_harden_auth_tokens**: Renames `token` to `token_hash`, adds `consumed_at` to auth tokens. (Irreversible data transformation: old tokens are invalidated).
- **008_add_auth_tokens**: Adds `password_reset_tokens` and `email_verification_tokens` tables.
