# Topic 10: Complete System Architecture — Production-Grade

## 🎯 Executive Summary

Industry-grade system architecture for the AutoML platform designed for:
- **Scalability:** 10,000+ concurrent users
- **Reliability:** 99.9% uptime SLA
- **Security:** Multi-layer fraud detection + DDoS protection
- **Cost-Efficiency:** Optimized for <$500/mo at 1000 DAU
- **Global Performance:** <200ms API response time worldwide

---

## 📐 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERNET / USERS                            │
│                    (Web, Mobile, API Clients)                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Cloudflare CDN        │
                    │  - Static Assets        │
                    │  - DDoS Protection      │
                    │  - SSL/TLS              │
                    │  - Global Edge Cache    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  NGINX Load Balancer    │
                    │  - SSL Termination      │
                    │  - Layer 1 Rate Limit   │
                    │  - Health Checks        │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
    ┌────▼────┐            ┌────▼────┐            ┌────▼────┐
    │ FastAPI │            │ FastAPI │            │ FastAPI │
    │Instance1│            │Instance2│            │Instance3│
    │REST+WS  │            │REST+WS  │            │REST+WS  │
    └────┬────┘            └────┬────┘            └────┬────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
    ┌────▼────┐            ┌────▼────┐            ┌────▼────┐
    │  Redis  │            │PostgreSQL│            │ Celery  │
    │ Cluster │            │Primary+  │            │ Queue   │
    │Rate Lim │            │Replica   │            │Workers  │
    └─────────┘            └──────────┘            └────┬────┘
                                                         │
                           ┌─────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐      ┌────▼────┐
    │Worker 1 │       │Worker 3 │      │Worker 5 │
    │High Pri │       │Normal   │      │Overflow │
    │Pro/Ent  │       │Free     │      │Dynamic  │
    └────┬────┘       └────┬────┘      └────┬────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │Cloudflare R2│
                    │Datasets +   │
                    │Models       │
                    └─────────────┘
```

---

## 🏗️ Detailed Component Architecture

### **1. Client Layer**

```
┌────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Web App    │  │  Mobile App  │  │  Python SDK  │   │
│  │ React + TS   │  │React Native  │  │API Client    │   │
│  │              │  │              │  │              │   │
│  │ - Dashboard  │  │ - Touch UI   │  │ - Notebooks  │   │
│  │ - Workflows  │  │ - Push Notif │  │ - Scripts    │   │
│  │ - Real-time  │  │ - Offline    │  │ - CI/CD      │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Technologies:**
- **Web:** React 18 + TypeScript + TanStack Query + Zustand
- **Mobile:** React Native + Expo
- **SDK:** Python requests + WebSocket client

**Features:**
- Progressive Web App (offline support)
- Real-time updates (WebSocket)
- Optimistic UI updates
- Mobile-first responsive design

---

### **2. CDN & Edge Layer**

```
┌────────────────────────────────────────────────────────────┐
│                   CLOUDFLARE CDN                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Edge Locations: 300+ cities worldwide                    │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Static Cache │  │ DDoS Shield  │  │  SSL/TLS     │   │
│  │              │  │              │  │              │   │
│  │ - JS Bundle  │  │ - Layer 3/4  │  │ - Auto Cert  │   │
│  │ - CSS        │  │ - Layer 7    │  │ - TLS 1.3    │   │
│  │ - Images     │  │ - Bot Detect │  │ - HSTS       │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Benefits:**
- **Performance:** <50ms latency worldwide
- **Security:** DDoS protection (up to 100 Gbps)
- **Cost:** $20/mo (Pro plan)
- **Bandwidth:** Unlimited

**Configuration:**
- Cache static assets: 1 year TTL
- Cache API responses: 1 minute TTL (for GET endpoints)
- Auto-minify JS/CSS/HTML
- Brotli compression

---

### **3. Load Balancer Layer**

```
┌────────────────────────────────────────────────────────────┐
│                   NGINX LOAD BALANCER                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Algorithm: Least Connections + Health Checks             │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │SSL Terminate │  │ Rate Limit 1 │  │Health Checks │   │
│  │              │  │              │  │              │   │
│  │ - TLS 1.3    │  │ - IP-based   │  │ - /health    │   │
│  │ - Let's Enc  │  │ - 1000 req/s │  │ - Every 10s  │   │
│  │ - HSTS       │  │ - Geo Block  │  │ - Auto Remove│   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
│  Upstream Servers (Round Robin):                          │
│  - api1.automl.internal:8000                              │
│  - api2.automl.internal:8000                              │
│  - api3.automl.internal:8000                              │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Configuration:**
```nginx
upstream api_backend {
    least_conn;
    server api1:8000 max_fails=3 fail_timeout=30s;
    server api2:8000 max_fails=3 fail_timeout=30s;
    server api3:8000 max_fails=3 fail_timeout=30s;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
limit_req zone=api burst=200 nodelay;

# Health checks
location /health {
    access_log off;
    return 200 "healthy\n";
}
```

---

### **4. Application Layer (FastAPI)**

```
┌────────────────────────────────────────────────────────────┐
│                   FASTAPI INSTANCES (x3)                   │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Each Instance (Stateless):                               │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │  FastAPI + Uvicorn (ASGI)                        │    │
│  │                                                   │    │
│  │  Middleware Stack:                                │    │
│  │  1. CORS Middleware                               │    │
│  │  2. JWT Authentication                            │    │
│  │  3. Rate Limiting (Redis)                         │    │
│  │  4. Request Validation (Pydantic)                 │    │
│  │  5. Error Handling (Sentry)                       │    │
│  │  6. Logging (Datadog)                             │    │
│  │                                                   │    │
│  │  Endpoints:                                       │    │
│  │  - /api/v1/auth/*                                 │    │
│  │  - /api/v1/datasets/*                             │    │
│  │  - /api/v1/workflows/*                            │    │
│  │  - /api/v1/jobs/*                                 │    │
│  │  - /api/v1/models/*                               │    │
│  │  - /api/v1/credits/*                              │    │
│  │  - /ws (WebSocket)                                │    │
│  │                                                   │    │
│  │  Workers: 4 per instance (Uvicorn workers)       │    │
│  │  Memory: 2 GB per instance                        │    │
│  │  CPU: 2 vCPU per instance                         │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Deployment:**
- **Platform:** Railway / Render / Fly.io
- **Container:** Docker (Python 3.11-slim)
- **Scaling:** Auto-scale 3-10 instances based on CPU >70%
- **Health:** `/health` endpoint with DB connection check

**Connection Pooling:**
```python
# PostgreSQL connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

# Redis connection pool
redis_pool = redis.ConnectionPool(
    host='redis',
    port=6379,
    max_connections=50
)
```

---

### **5. Database Layer (PostgreSQL)**

```
┌────────────────────────────────────────────────────────────┐
│                  POSTGRESQL (Neon)                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────┐    ┌──────────────────────┐    │
│  │   PRIMARY DATABASE   │    │   READ REPLICA       │    │
│  │   (Writes Only)      │───▶│   (Reads Only)       │    │
│  │                      │    │                      │    │
│  │  - Users             │    │  - Dashboard Queries │    │
│  │  - Credit Txns       │    │  - List Endpoints    │    │
│  │  - Jobs              │    │  - Analytics         │    │
│  │  - Datasets          │    │  - Admin Panels      │    │
│  │                      │    │                      │    │
│  │  Replication Lag:    │    │  Replication Lag:    │    │
│  │  < 100ms             │    │  < 100ms             │    │
│  └──────────────────────┘    └──────────────────────┘    │
│                                                            │
│  Size: 10 GB (hot data)                                   │
│  Backup: Daily snapshots (30 day retention)               │
│  Connection Limit: 100 concurrent                         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Configuration:**
- **Instance:** Neon Serverless Postgres
- **CPU:** 2 vCPU
- **RAM:** 4 GB
- **Storage:** 10 GB (auto-scale to 100 GB)
- **Backup:** Automated daily + point-in-time recovery
- **Cost:** $25/mo (primary) + $30/mo (replica) = $55/mo

**Read/Write Split:**
```python
# Write operations → Primary
@app.post("/api/jobs")
async def create_job():
    with primary_db.session() as session:
        session.add(job)
        session.commit()

# Read operations → Replica
@app.get("/api/jobs")
async def list_jobs():
    with replica_db.session() as session:
        jobs = session.query(Job).all()
    return jobs
```

---

### **6. Cache & Rate Limiting (Redis)**

```
┌────────────────────────────────────────────────────────────┐
│                     REDIS CLUSTER                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Use Cases:                                                │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Rate Limits  │  │  Sessions    │  │  Pub/Sub     │   │
│  │              │  │              │  │              │   │
│  │ - Token      │  │ - JWT Tokens │  │ - WebSocket  │   │
│  │   Bucket     │  │ - User Data  │  │   Events     │   │
│  │ - IP Limits  │  │ - Temp Data  │  │ - Job Status │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐                      │
│  │  Job Queue   │  │  Cache       │                      │
│  │              │  │              │                      │
│  │ - Pending    │  │ - User Info  │                      │
│  │ - Running    │  │ - Datasets   │                      │
│  │ - Failed     │  │ - Models     │                      │
│  └──────────────┘  └──────────────┘                      │
│                                                            │
│  Memory: 2 GB                                             │
│  Persistence: AOF (Append-Only File)                      │
│  Eviction: LRU (Least Recently Used)                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Configuration:**
- **Platform:** Upstash / Railway Redis
- **Memory:** 2 GB
- **Persistence:** AOF (every second)
- **Max Connections:** 500
- **Cost:** $10/mo

**Key Patterns:**
```
Rate Limits:
  rate_limit:{user_id}:job_create:minute → {count, expires_at}
  rate_limit:{user_id}:ad_claim:day → {count, expires_at}

Sessions:
  session:{jti} → {user_id, created_at} (TTL: 7 days)
  
Job Queue:
  queue:high_priority → [job_id_1, job_id_2, ...]
  queue:normal_priority → [job_id_3, job_id_4, ...]

WebSocket Pub/Sub:
  channel:job:{job_id} → {event_type, data}
  channel:user:{user_id} → {event_type, data}

Cache:
  cache:user:{user_id} → {user_data} (TTL: 5 min)
  cache:dataset:{dataset_id}:stats → {stats_data} (TTL: 1 hour)
```

---

### **7. Message Queue & Workers (Celery)**

```
┌────────────────────────────────────────────────────────────┐
│                    CELERY ARCHITECTURE                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                  ┌──────────────┐                         │
│                  │ Celery Broker│                         │
│                  │ (Redis)      │                         │
│                  └──────┬───────┘                         │
│                         │                                  │
│          ┌──────────────┼──────────────┐                  │
│          │              │              │                  │
│     ┌────▼────┐    ┌────▼────┐   ┌────▼────┐            │
│     │ Worker1 │    │ Worker3 │   │ Worker5 │            │
│     │ High Pri│    │ Normal  │   │Overflow │            │
│     │Pro/Ent  │    │ Free    │   │Dynamic  │            │
│     └────┬────┘    └────┬────┘   └────┬────┘            │
│          │              │              │                  │
│          └──────────────┼──────────────┘                  │
│                         │                                  │
│                    ┌────▼────┐                            │
│                    │ML Tasks │                            │
│                    │- Train  │                            │
│                    │- Stats  │                            │
│                    │- HPO    │                            │
│                    └─────────┘                            │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Worker Pool Configuration:**

| Worker | Priority | Queues | Concurrency | Memory | Tier |
|--------|----------|--------|-------------|--------|------|
| 1 & 2  | High     | `high_priority` | 2 jobs | 8 GB | Pro/Ent |
| 3 & 4  | Normal   | `normal_priority` | 2 jobs | 4 GB | Free |
| 5      | Low      | `low_priority` | 1 job | 4 GB | Overflow |

**Fair Scheduling Algorithm:**
```
Pattern: [High, High, Normal, High, High, Low]
Result: 60% high, 30% normal, 10% low

This ensures:
- Pro/Enterprise users get fast service
- Free users don't starve (30% guaranteed)
- New users can still run jobs (10% overflow)
```

**Task Types:**
```python
# High-priority tasks (Pro/Enterprise)
@celery.task(queue='high_priority')
def execute_pro_job(job_id):
    # ML training with HPO, ensemble, SHAP
    pass

# Normal-priority tasks (Free tier)
@celery.task(queue='normal_priority')
def execute_free_job(job_id):
    # Basic ML training
    pass

# Low-priority tasks (background)
@celery.task(queue='low_priority')
def compute_dataset_stats(dataset_id):
    # Async stats computation
    pass
```

**Auto-Scaling:**
- Scale up: When queue depth >20 jobs for >5 minutes
- Scale down: When queue depth <5 jobs for >10 minutes
- Max workers: 10 (cost limit)
- Min workers: 3 (always available)

---

### **8. Object Storage (Cloudflare R2)**

```
┌────────────────────────────────────────────────────────────┐
│                   CLOUDFLARE R2 STORAGE                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Bucket Structure:                                         │
│                                                            │
│  automl-production/                                        │
│  ├── datasets/                                             │
│  │   ├── {user_id}/                                        │
│  │   │   ├── {dataset_id}/                                 │
│  │   │   │   ├── original.csv                              │
│  │   │   │   └── processed.parquet                         │
│  │                                                          │
│  ├── models/                                               │
│  │   ├── {user_id}/                                        │
│  │   │   ├── {model_id}/                                   │
│  │   │   │   ├── model.joblib                              │
│  │   │   │   ├── metadata.json                             │
│  │   │   │   └── shap_plots/                               │
│  │                                                          │
│  ├── artifacts/                                            │
│  │   ├── feature_importance.png                            │
│  │   ├── confusion_matrix.png                              │
│  │   └── roc_curve.png                                     │
│  │                                                          │
│  └── archives/                                             │
│      ├── credit_transactions_2024.parquet                  │
│      └── old_snapshots_2024.parquet                        │
│                                                            │
│  Storage: ~100 GB (at 1000 DAU)                           │
│  Cost: $0.015/GB/mo = $1.50/mo                            │
│  Egress: Free (Cloudflare R2 advantage)                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Access Patterns:**
- **Presigned URLs:** For direct upload/download (no API bottleneck)
- **Lifecycle Rules:** Delete inactive datasets after 30/180 days
- **CDN Integration:** Static artifacts cached at edge

**Security:**
- **Encryption:** AES-256 at rest
- **Access Control:** IAM policies per bucket
- **Audit:** All access logged to S3 access logs

---

### **9. External Services Integration**

```
┌────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Payments   │  │  Ad Rewards  │  │    Email     │   │
│  │              │  │              │  │              │   │
│  │   Stripe     │  │   AdMob      │  │  SendGrid    │   │
│  │              │  │              │  │              │   │
│  │ - Checkout   │  │ - Rewarded   │  │ - Transact   │   │
│  │ - Webhooks   │  │ - Server     │  │ - Marketing  │   │
│  │ - Invoices   │  │   Verify     │  │ - Support    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐                      │
│  │ Fraud Detect │  │  Monitoring  │                      │
│  │              │  │              │                      │
│  │IPQualityScore│  │   Sentry     │                      │
│  │FingerprintJS │  │   Datadog    │                      │
│  │              │  │              │                      │
│  │ - IP Intel   │  │ - Errors     │                      │
│  │ - Device ID  │  │ - APM        │                      │
│  │ - Risk Score │  │ - Logs       │                      │
│  └──────────────┘  └──────────────┘                      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Integration Patterns:**
- **Stripe:** Webhook-based (idempotent payment confirmation)
- **AdMob:** Server-to-server callback verification
- **SendGrid:** Async email queue (Celery task)
- **IPQualityScore:** Real-time API call on ad claim
- **FingerprintJS:** Client-side generation + server validation
- **Sentry:** Automatic error capture + breadcrumbs
- **Datadog:** Agent-based metrics + APM traces

---

### **10. Monitoring & Observability**

```
┌────────────────────────────────────────────────────────────┐
│              MONITORING & OBSERVABILITY STACK              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │                  DATADOG APM                     │    │
│  │                                                   │    │
│  │  Metrics Collected:                               │    │
│  │  - API latency (p50, p95, p99)                   │    │
│  │  - Database query time                            │    │
│  │  - Redis hit rate                                 │    │
│  │  - Worker queue depth                             │    │
│  │  - Error rate                                     │    │
│  │  - Job success/failure rate                       │    │
│  │                                                   │    │
│  │  Traces: Full request → response path            │    │
│  │  Logs: Centralized log aggregation               │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │                   SENTRY                          │    │
│  │                                                   │    │
│  │  Error Tracking:                                  │    │
│  │  - Exception grouping                             │    │
│  │  - Stack traces                                   │    │
│  │  - User context                                   │    │
│  │  - Breadcrumbs                                    │    │
│  │  - Release tracking                               │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │                  GRAFANA DASHBOARDS               │    │
│  │                                                   │    │
│  │  Dashboards:                                      │    │
│  │  1. System Health (CPU, Memory, Disk)            │    │
│  │  2. API Performance (Latency, Throughput)        │    │
│  │  3. Business Metrics (Users, Jobs, Revenue)      │    │
│  │  4. Fraud Detection (Flags, Blocks)              │    │
│  │  5. Cost Monitoring (Compute, Storage)           │    │
│  │                                                   │    │
│  │  Alerts: PagerDuty integration                    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Alert Thresholds:**

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| API p99 latency | >1s | >3s | Scale up API instances |
| Error rate | >1% | >5% | Page on-call |
| Queue depth | >50 | >100 | Scale up workers |
| DB CPU | >70% | >90% | Optimize queries |
| Redis memory | >80% | >95% | Increase instance size |
| Fraud score high | >10 users | >50 users | Investigate |

---

## 💰 Cost Breakdown (Monthly)

| Component | Provider | Size | Cost/mo | Notes |
|-----------|----------|------|---------|-------|
| **Compute** | | | | |
| API Instances (x3) | Railway | 2GB RAM each | $60 | Auto-scale to 10 |
| Celery Workers (x5) | Railway | 4-8GB RAM | $200 | CPU-optimized |
| **Database** | | | | |
| PostgreSQL Primary | Neon | 10GB | $25 | Serverless |
| PostgreSQL Replica | Neon | 10GB | $30 | Read-only |
| **Cache** | | | | |
| Redis | Upstash | 2GB | $10 | AOF persistence |
| **Storage** | | | | |
| Object Storage (R2) | Cloudflare | 100GB | $1.50 | Free egress |
| **CDN** | | | | |
| CDN + DDoS | Cloudflare | Unlimited | $20 | Pro plan |
| **External Services** | | | | |
| IP Intelligence | IPQualityScore | 5K checks | $30 | Fraud detection |
| Device Fingerprint | FingerprintJS | 10K IDs | $99 | Anti-fraud |
| Email | SendGrid | 10K emails | $15 | Transactional |
| Error Tracking | Sentry | 10K events | $26 | Free tier + paid |
| Monitoring | Datadog | 5 hosts | $75 | APM + logs |
| **Payments** | | | | |
| Stripe | Stripe | Variable | $0 | 2.9% + 30¢ per txn |
| **Total** | | | **~$592/mo** | At 1000 DAU |

**Revenue Break-Even:**
- Need: ~75 Pro users ($10/mo) + ad revenue
- OR: 50 Pro users + 1000 free users (ads)
- Expected: Break-even Month 2-3

**Scaling Costs:**
- 5K DAU: ~$1,200/mo
- 10K DAU: ~$2,500/mo
- 50K DAU: ~$8,000/mo

---

## 📈 Scalability Roadmap

### **Phase 1: MVP (0-1K DAU)**
- 3 API instances
- 5 workers
- Single region (US East)
- 10 GB database
- **Cost:** $592/mo

### **Phase 2: Growth (1K-5K DAU)**
- 5-10 API instances (auto-scale)
- 10-15 workers (auto-scale)
- Read replicas: 2
- Database: 50 GB
- Redis: 4 GB
- **Cost:** $1,200/mo

### **Phase 3: Scale (5K-20K DAU)**
- 10-20 API instances
- 20-40 workers
- Multi-region deployment (US, EU)
- Database: 200 GB
- Redis: 8 GB (cluster mode)
- CDN: Enterprise plan
- **Cost:** $4,000/mo

### **Phase 4: Global (20K-100K DAU)**
- 50+ API instances
- 100+ workers
- Global deployment (US, EU, Asia)
- Database: 1 TB (sharded)
- Redis: 32 GB (cluster)
- Dedicated infrastructure
- **Cost:** $15,000/mo

---

## 🔒 Security Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   SECURITY LAYERS                          │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Layer 1: Edge (Cloudflare)                               │
│  ├─ DDoS Protection (up to 100 Gbps)                      │
│  ├─ Bot Detection                                          │
│  ├─ Rate Limiting (IP-based)                               │
│  └─ SSL/TLS Termination                                    │
│                                                            │
│  Layer 2: Load Balancer (NGINX)                           │
│  ├─ IP Allowlist (optional)                                │
│  ├─ Request Size Limits                                    │
│  ├─ Header Validation                                      │
│  └─ Health Checks                                          │
│                                                            │
│  Layer 3: Application (FastAPI)                           │
│  ├─ JWT Authentication                                     │
│  ├─ Rate Limiting (per-user)                               │
│  ├─ Input Validation (Pydantic)                            │
│  ├─ CORS Policy                                            │
│  └─ SQL Injection Prevention                               │
│                                                            │
│  Layer 4: Fraud Detection                                 │
│  ├─ IP Intelligence                                        │
│  ├─ Device Fingerprinting                                  │
│  ├─ Velocity Checks                                        │
│  └─ Pattern Analysis                                       │
│                                                            │
│  Layer 5: Data (Encryption)                               │
│  ├─ Database: AES-256 at rest                             │
│  ├─ Storage: AES-256 at rest                              │
│  ├─ Transit: TLS 1.3                                       │
│  └─ Backups: Encrypted                                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Compliance:**
- ✅ GDPR (EU): Data deletion, minimal PII, consent
- ✅ COPPA (US): Age verification, parental consent
- ✅ SOC 2 Type II: Audit trails, access controls
- ✅ HIPAA: N/A (no healthcare data)

---

## 🔄 Data Flow Diagrams

### **Job Creation Flow**

```
User → Frontend → API → Redis (Rate Check) → Database (Transaction)
                                            → Celery Queue
                                                    ↓
Worker → Fetch Job → Download Dataset (R2) → Train Model
                                            → Save Model (R2)
                                            → Update DB
                                            → Notify User (WebSocket)
```

### **Ad Reward Flow**

```
User Watches Ad → AdMob → Callback to API
                                    ↓
                         API → Verify Token (AdMob)
                            → Check IP (IPQualityScore)
                            → Check Device (Redis)
                            → Check Velocity (Redis)
                            → Create Transaction (DB)
                            → Update Balance (DB)
                            → Return Credits (Response)
```

### **Real-Time Updates Flow**

```
Job Status Change → Worker → Update DB
                                  ↓
                         Redis Pub/Sub → All API Instances
                                                ↓
                                         WebSocket Connections
                                                ↓
                                         Frontend Update
```

---

## 🎯 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| API Latency (p95) | <200ms | TBD |
| Database Query Time (p95) | <50ms | TBD |
| Job Queue Wait (Free) | <3 min | TBD |
| Job Queue Wait (Pro) | <30 sec | TBD |
| WebSocket Latency | <100ms | TBD |
| Uptime | 99.9% | TBD |
| Error Rate | <0.1% | TBD |

---

## ✅ Deployment Checklist

### **Pre-Launch**
- [ ] Deploy database schema
- [ ] Run migrations (risk mitigation)
- [ ] Set up read replica
- [ ] Configure Redis
- [ ] Deploy API instances (3)
- [ ] Deploy workers (5)
- [ ] Configure load balancer
- [ ] Set up CDN
- [ ] Configure external services (Stripe, AdMob, etc.)
- [ ] Set up monitoring (Sentry, Datadog, Grafana)
- [ ] Configure alerts
- [ ] Load testing (100 concurrent users)
- [ ] Security audit
- [ ] Backup testing

### **Post-Launch**
- [ ] Monitor dashboards 24/7
- [ ] Weekly cost review
- [ ] Monthly security audit
- [ ] Quarterly disaster recovery drill

---

## 🎓 Architecture Decisions Log

### **Why Cloudflare R2 over AWS S3?**
- **Cost:** R2 has zero egress fees (vs $0.09/GB on S3)
- **Performance:** Comparable latency
- **Savings:** ~$500/mo at 5TB egress

### **Why Neon over AWS RDS?**
- **Cost:** Serverless pricing (pay per compute-second)
- **Features:** Instant read replicas, branching, time-travel
- **Savings:** ~$100/mo vs RDS

### **Why Railway over AWS ECS?**
- **Simplicity:** Zero DevOps overhead
- **Speed:** Deploy in minutes vs hours
- **Trade-off:** Slightly higher cost, less control

### **Why Celery over AWS Lambda?**
- **Long-running:** ML jobs can take 10+ minutes
- **Cost:** Cheaper for sustained workloads
- **Control:** Better resource management

---

## 🚀 YOU'RE READY TO BUILD!

**Complete Design Package:**
1. ✅ Database Schema (production-grade)
2. ✅ API Design (risk-reduced)
3. ✅ System Architecture (this document)

**Total Design Time:** 10 topics completed  
**Risk Level:** 🟢 Production-Ready  
**Estimated Build Time:** 3-4 months (2 developers)

**Next Steps:**
1. Set up infrastructure (Railway, Neon, Redis)
2. Deploy base schema
3. Build API endpoints (FastAPI)
4. Build workers (Celery)
5. Build frontend (React)
6. Launch MVP! 🎉

**Good luck!** 🚀
