# Disaster Recovery Configuration — IntensiCare

**Date:** 2026-07-09
**Document:** H7 gap closure
**RPO Target:** 1 hour
**RTO Target:** 1 hour

## Architecture

```
┌──────────────────────┐         ┌──────────────────────┐
│   PRIMARY (us-east-1) │  WAL    │    DR (sa-east-1)     │
│   PostgreSQL          │ ──────► │   PostgreSQL (replica)│
│   TimescaleDB         │ shipping│   TimescaleDB         │
│   Redis               │         │   Redis               │
└──────────────────────┘         └──────────────────────┘
```

## PostgreSQL WAL Shipping

### Primary Configuration (postgresql.conf)
```ini
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1024  # MB — retain enough WAL for DR catch-up
archive_mode = on
archive_command = 'test ! -f /wal_archive/%f && cp %p /wal_archive/%f'
```

### Replica Configuration (recovery.conf on DR)
```ini
standby_mode = on
primary_conninfo = 'host=<primary_ip> port=5432 user=replicator password=<secret>'
restore_command = 'cp /wal_archive/%f %p'
recovery_target_timeline = 'latest'
```

### Docker Compose — DR Replica Service
```yaml
# docker-compose.prod.yml addition
services:
  postgres-dr:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_PASSWORD: ${DR_POSTGRES_PASSWORD}
    volumes:
      - pgdata_dr:/var/lib/postgresql/data
      - wal_archive:/wal_archive
    command: |
      -c wal_level=replica
      -c max_wal_senders=5
```

## Redis Replication

```yaml
services:
  redis-dr:
    image: redis:7-alpine
    command: redis-server --replicaof ${PRIMARY_REDIS_HOST} 6379 --requirepass ${REDIS_PASSWORD} --masterauth ${REDIS_PASSWORD}
```

## Recovery Procedure

### Failover to DR
```bash
# 1. Promote DR replica to primary
docker exec postgres-dr psql -U postgres -c "SELECT pg_promote();"

# 2. Update DNS/ALB to point to DR region
aws route53 change-resource-record-sets --hosted-zone-id Z123456 --change-batch file://dns-failover.json

# 3. Verify application health
curl -f https://dr.intensicare.com/health

# 4. Notify on-call
# Send alert via PagerDuty/Opsgenie
```

### Failback to Primary
```bash
# 1. Re-establish WAL shipping from DR → Primary
# 2. Wait for replication lag = 0
# 3. Demote DR, promote Primary
# 4. Update DNS back
```

## Backup Strategy

| Component | Method | Frequency | Retention |
|-----------|--------|-----------|-----------|
| PostgreSQL | pg_dump + WAL | Daily full + continuous WAL | 30 days |
| Redis | RDB snapshot | Hourly | 7 days |
| Application config | Git + encrypted backup | On change | Indefinite |

## DR Testing

- **Frequency:** Quarterly
- **Test type:** Tabletop (Q1, Q3), Live failover (Q2, Q4)
- **Success criteria:** RTO < 1h, RPO < 1h, zero data loss
- **Documentation:** Each test produces a DR_TEST_REPORT.md

## Current Status

⚠️ **NOT YET PROVISIONED** — Requires AWS account with:
- RDS PostgreSQL cross-region read replica
- ElastiCache Redis replication group
- Route53 failover routing policy
- S3 bucket for WAL archive

**Workaround for dev/staging:** Docker Compose DR configuration documented above. Production DR deferred to AWS provisioning (B2 blocker in BLOCKERS.md).
