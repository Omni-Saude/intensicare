# IntensiCare Threat Model

> **Document ID**: INT-TM-001  
> **Version**: 1.0 — 2026-07-08  
> **Classification**: Internal — Confidential  
> **Methodology**: OWASP Threat Dragon / STRIDE  
> **Scope**: IntensiCare ICU Clinical Platform (API, workers, database, integrations)

---

## 1. System Description

IntensiCare is a software-as-a-service clinical platform that provides
continuous monitoring, early-warning scoring, antimicrobial stewardship,
clinical pathway orchestration, and electronic prescribing for intensive
care units (ICUs) and high-dependency wards.

The platform ingests real-time vitals from hospital information systems
(HIS) and bedside monitors, applies clinical-rule engines (sepsis,
ventilation, sedation, prophylaxis), and surfaces deterioration alerts
to clinicians via a web dashboard and WebSocket push notifications.

### 1.1 Architecture Overview (high-level)

```
┌──────────┐      ┌────────────────┐      ┌──────────────────────────────┐
│ Clinician│─────▶│  API Gateway   │─────▶│  IntensiCare FastAPI Backend │
│ Browser  │ TLS  │  (ALB / NLB)  │ TLS  │  (EC2 / ECS Fargate)         │
└──────────┘      └────────────────┘      └──────────┬───────────────────┘
                   │  WAF (optional)  │              │
                   └──────────────────┘              │
                          │                          │
              ┌───────────┴───────────┐              │
              │  Identity Center      │              │
              │  (IAM IC / OIDC)      │              │
              └───────────────────────┘              │
                          │                          │
         ┌────────────────┼──────────────────────────┼──────────────┐
         │                │                          │              │
         ▼                ▼                          ▼              ▼
┌────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐
│ PostgreSQL │  │  Redis (cache,   │  │  AWS Lake        │  │  FHIR / MPI  │
│ TimescaleDB│  │  rate-limit, WS) │  │  Formation /     │  │  (external)  │
│            │  │                  │  │  Athena           │  │              │
└────────────┘  └──────────────────┘  └──────────────────┘  └──────────────┘
```

### 1.2 Key Components

| Component | Role | AuthN / AuthZ |
|---|---|---|
| FastAPI Backend | REST API + WebSocket server | JWT (dev/test) / IAM IC OIDC (staging/prod) |
| PostgreSQL + TimescaleDB | Clinical data, scores, prescriptions | Database roles + row-level security (planned) |
| Redis | Session cache, rate-limit counters, WS pub/sub | AUTH password (required in prod) |
| AWS Lake Formation | Data-lake queries (analytics) | ABAC via Lake Formation tags |
| HAPI FHIR / MPI | External FHIR server + Master Patient Index | Token-based auth |

---

## 2. Trust Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    UNTRUSTED ZONE                            │
│  Internet / Hospital guest network / compromised endpoints │
└──────────────┬──────────────────────────────────────────────┘
               │  Boundary 1: TLS-terminating load balancer
               │  (WAF rules, DDoS protection, IP allow-lists)
┌──────────────▼──────────────────────────────────────────────┐
│                   SEMI-TRUSTED ZONE                          │
│  API Gateway / ALB — terminates TLS, forwards to backend   │
└──────────────┬──────────────────────────────────────────────┘
               │  Boundary 2: Backend network (VPC / security group)
               │  Service-to-service auth (IAM roles, secrets)
┌──────────────▼──────────────────────────────────────────────┐
│                    TRUSTED ZONE                              │
│  FastAPI containers, PostgreSQL, Redis, Lake Formation      │
│  All intra-VPC traffic assumed authenticated                │
└─────────────────────────────────────────────────────────────┘
```

| # | Boundary | Between | Controls |
|---|---|---|---|
| B1 | Internet → ALB | Untrusted → Semi-Trusted | TLS 1.2+, WAF rules, DDoS shield |
| B2 | ALB → Backend | Semi-Trusted → Trusted | Security groups, mutual TLS, IAM roles |
| B3 | Backend → Database | Trusted (app → PG) | TLS, DB credentials in Secrets Manager |
| B4 | Backend → External (FHIR/MPI) | Trusted → External | API tokens, TLS, egress allow-lists |

---

## 3. Key Assets

### 3.1 Primary Assets

| Asset | Classification | Sensitivity | Location |
|---|---|---|---|
| **PHI / ePHI** (protected health information) | HIPAA / LGPD Category I | **Critical** | PostgreSQL, in-transit API responses |
| **Clinical Scores** (SOFA, APACHE, NEWS, SAPS) | Clinical Decision Support | **High** | PostgreSQL — `vitals`, `scores` tables |
| **Medication Orders / Prescriptions** | e-Prescribing | **Critical** | PostgreSQL — `prescricao` tables |
| **User Credentials** (passwords, JWTs, IAM tokens) | AuthN | **Critical** | Redis (session), JWT claims |
| **Audit Logs** | Compliance (HIPAA / LGPD) | **High** | PostgreSQL — `audit_log` table |
| **Alert Routing Rules** | Clinical Operations | **Medium** | PostgreSQL |
| **Antimicrobial Stewardship Data** | Clinical Quality | **High** | PostgreSQL — `antimicrobial` tables |

### 3.2 Supporting Assets

| Asset | Sensitivity | Impact of Compromise |
|---|---|---|
| Rate-limit counters (Redis) | Low | DoS amplification |
| WebSocket connection state | Medium | Real-time alert interception |
| FHIR enrichment cache | Medium | Stale/incomplete patient data |
| Athena query history | Medium | Analytics data leakage |

---

## 4. Threat Actors

| Actor | Motivation | Capability | Likelihood |
|---|---|---|---|
| **External Attacker (script kiddie)** | Defacement, notoriety | Low | **High** — automated scanning |
| **Organised Cyber-criminal** | Ransomware, PHI exfiltration for resale | **High** | **Medium** — healthcare is a top target |
| **Compromised Clinician Account** | Accidental accomplice (phishing) | Medium (legit access) | **Medium** — phishing is prevalent |
| **Malicious Insider (clinician/staff)** | PHI theft, sabotage | High (legit access) | **Low** — but impact is extreme |
| **Third-party Integrator** | Accidental data leak via FHIR/MPI | Medium (API key) | **Low** |
| **Nation-state Actor** | Espionage, critical-infrastructure disruption | **Very High** | **Low** — but must be in scope |

---

## 5. Top 10 Threats (STRIDE-classified)

### T-01 — SQL Injection via Clinical Form Inputs
- **STRIDE**: **T**ampering / **I**nformation Disclosure
- **OWASP**: A03:2021 — Injection
- **Asset**: PHI, clinical scores
- **Vector**: Malicious SQL fragments in form fields (e.g., free-text `evolucoes` notes) bypass ORM parameterisation
- **Likelihood**: Medium | **Impact**: Critical
- **Existing Controls**: SQLAlchemy 2.0 parameterised queries; input validation via Pydantic schemas
- **Gap**: No WAF SQL-injection rules confirmed; free-text fields lack length limits

### T-02 — JWT Token Forgery / Weak Secret
- **STRIDE**: **S**poofing / **E**levation of Privilege
- **OWASP**: A07:2021 — Identification and Authentication Failures
- **Asset**: User credentials, clinical data
- **Vector**: Default `secret_key = "change-me-in-production"` in dev leaks to staging; weak HS256 key brute-forced
- **Likelihood**: Medium | **Impact**: Critical
- **Existing Controls**: Production validator blocks default secret; IAM IC replaces JWT in staging/prod (Fase 3)
- **Gap**: Dev/CI environments still use HS256; no asymmetric key (RS256/ES256) fallback

### T-03 — PHI Exposure via Missing Security Headers
- **STRIDE**: **I**nformation Disclosure
- **OWASP**: A05:2021 — Security Misconfiguration
- **Asset**: All HTTP responses containing PHI
- **Vector**: Clickjacking (no `X-Frame-Options`), MIME sniffing (no `X-Content-Type-Options`), mixed-content downgrade (no HSTS)
- **Likelihood**: Medium | **Impact**: High
- **Existing Controls**: **SecurityHeadersMiddleware (F-SEC-008)** — this document's companion control ✓
- **Gap**: CSP currently allows `style-src 'unsafe-inline'`; should be tightened post-frontend audit

### T-04 — Brute-Force / Credential Stuffing on Auth Endpoints
- **STRIDE**: **S**poofing
- **OWASP**: A07:2021 — Identification and Authentication Failures
- **Asset**: User accounts, PHI visibility
- **Vector**: Automated login attempts at `/auth/login`
- **Likelihood**: High | **Impact**: High
- **Existing Controls**: RateLimitMiddleware — 5 req/min on `/auth` endpoints ✓
- **Gap**: No account lockout after N failures; no CAPTCHA

### T-05 — Privilege Escalation via Unprotected Admin Endpoints
- **STRIDE**: **E**levation of Privilege
- **OWASP**: A01:2021 — Broken Access Control
- **Asset**: All clinical data, user management
- **Vector**: Auth'd user with `leitor` role accesses admin-only routes via missing RBAC decorator
- **Likelihood**: Medium | **Impact**: Critical
- **Existing Controls**: RBAC dependency checks (`RequireRole`, `require_permission`); admin router gated
- **Gap**: No automated RBAC integration test for every endpoint; audit of decorator coverage pending

### T-06 — WebSocket Alert Interception / Injection
- **STRIDE**: **T**ampering / **I**nformation Disclosure
- **OWASP**: A01:2021 — Broken Access Control
- **Asset**: Real-time alerts, vitals stream
- **Vector**: Attacker connects to `/ws` with a stolen JWT and subscribes to another unit's alerts
- **Likelihood**: Low | **Impact**: High
- **Existing Controls**: WebSocket auth via JWT token in connect params; room-based pub/sub
- **Gap**: No per-message authorisation re-check; token revocation not propagated to open WS connections

### T-07 — Redis Cache Poisoning / Data Leakage
- **STRIDE**: **T**ampering / **I**nformation Disclosure
- **OWASP**: A02:2021 — Cryptographic Failures
- **Asset**: Session tokens, rate-limit state, WS state
- **Vector**: Unauthenticated Redis (no password in dev); attacker flushes/poisons cache
- **Likelihood**: Low (prod requires password) | **Impact**: Medium
- **Existing Controls**: Redis AUTH enforced in staging/prod via validator; firewall restricts port 6379
- **Gap**: Redis not configured for TLS in-transit encryption

### T-08 — Excessive Data Exposure via API Responses
- **STRIDE**: **I**nformation Disclosure
- **OWASP**: A04:2021 — Insecure Design
- **Asset**: PHI fields returned to clients that don't need them
- **Vector**: `/api/v1/patients/{id}` returns full PHI (address, document numbers) regardless of caller role
- **Likelihood**: Medium | **Impact**: High
- **Existing Controls**: Pydantic response schemas define fields
- **Gap**: No field-level access control; no response filtering by role

### T-09 — Denial of Service via Expensive Queries
- **STRIDE**: **D**enial of Service
- **OWASP**: A04:2021 — Insecure Design
- **Asset**: Platform availability, clinical workflows
- **Vector**: Unauthenticated user hits `/api/v1/dashboard/scores` with unbounded date range causing full-table scan
- **Likelihood**: Medium | **Impact**: High (clinical downtime)
- **Existing Controls**: Rate limiting; connection pooling (max 10 PG connections); staleness watchdog
- **Gap**: No query timeout enforcement at API layer; no pagination enforcement on list endpoints

### T-10 — Supply Chain Compromise via Python Dependency
- **STRIDE**: **T**ampering / **E**levation of Privilege
- **OWASP**: A06:2021 — Vulnerable and Outdated Components
- **Asset**: Entire platform
- **Vector**: Attacker publishes malicious version of a transitive dependency; CI pulls it automatically
- **Likelihood**: Low | **Impact**: Critical
- **Existing Controls**: `requirements.txt` with pinned versions; Dependabot / Renovate scanning
- **Gap**: No SBOM generation; no software bill of materials in CI pipeline

---

## 6. Existing Security Controls (Defence-in-Depth)

| Layer | Control | Status |
|---|---|---|
| **Network** | TLS 1.2+ on all external endpoints | ✓ Planned / infra |
| **Network** | WAF with OWASP Core Rule Set | ⚠️ Recommended |
| **Network** | Security groups (VPC) restricting DB/Redis access | ✓ Planned / infra |
| **Application** | JWT authentication + IAM IC OIDC (Fase 3) | ✓ Implemented |
| **Application** | RBAC (roles: admin, médico, enfermeiro, leitor) | ✓ Implemented |
| **Application** | Rate limiting (token bucket, Redis-backed) | ✓ F-SEC-006 |
| **Application** | Security headers (HSTS, CSP, X-Frame-Options, …) | ✓ **F-SEC-008 (this task)** |
| **Application** | Input validation (Pydantic models) | ✓ Implemented |
| **Application** | CORS allow-list (no wildcard in prod) | ✓ Implemented |
| **Data** | PostgreSQL TLS + password auth | ⚠️ TLS pending |
| **Data** | Redis AUTH (enforced in prod) | ✓ Implemented |
| **Data** | KMS envelope encryption (per-tenant DEKs) | ✓ Fase 3 |
| **Monitoring** | Structured logging (JSON) | ✓ Implemented |
| **Monitoring** | OpenTelemetry traces + Prometheus metrics | ✓ CON-0006 |
| **Monitoring** | Watchdog / dead-man's switch (CloudWatch pings) | ✓ INV-5 |
| **Monitoring** | Staleness alert (no-scores timeout) | ✓ INV-5 |

---

## 7. Open Findings (from Forensic Audit — F-SEC-011)

| # | Finding | Severity | Mitigation |
|---|---|---|---|
| F-01 | No `Content-Security-Policy` header | High | ✅ Mitigated — SecurityHeadersMiddleware (this task) |
| F-02 | No `X-Frame-Options` / `frame-ancestors` | Medium | ✅ Mitigated — SecurityHeadersMiddleware |
| F-03 | No HSTS header | High | ✅ Mitigated — SecurityHeadersMiddleware (staging/prod) |
| F-04 | `style-src 'unsafe-inline'` in CSP | Low | ⚠️ Accepted risk — required by frontend framework; tighten post-audit |
| F-05 | JWT secret validation bypass in dev mode | Medium | ✅ Blocked by production validator; IAM IC replaces JWT in upper envs |
| F-06 | Redis unauthenticated in dev (design choice) | Low | ⚠️ Accepted risk — dev only; AUTH enforced in staging/prod |
| F-07 | No query timeout on API endpoints | Medium | 📋 Backlog — add `statement_timeout` at session level |
| F-08 | No account lockout after repeated login failures | Medium | 📋 Backlog — implement in auth service |
| F-09 | WebSocket authorisation not re-checked per message | Medium | 📋 Backlog — add `RequireRole` equivalent for WS frames |
| F-10 | No SBOM in CI pipeline | Low | 📋 Backlog — integrate `cyclonedx-python` |

---

## 8. Risk Matrix Summary

| Likelihood →<br>Impact ↓ | Low | Medium | High |
|---|---|---|---|
| **Critical** | T-06 (WS injection) | T-01 (SQLi), T-02 (JWT), T-05 (PrivEsc), T-10 (supply chain) | — |
| **High** | T-07 (Redis leak) | T-03 (headers), T-08 (data exposure), T-09 (DoS) | T-04 (brute force) |
| **Medium** | — | — | — |
| **Low** | — | — | — |

---

## 9. Review & Maintenance

| Activity | Cadence | Owner |
|---|---|---|
| Threat model review | Every major release / architecture change | Security Champion |
| CSP header audit | Quarterly — verify no new third-party origins needed | DevOps |
| Penetration test | Annually (external firm) | CISO / Tech Lead |
| Dependency audit (`pip-audit`) | Weekly in CI | DevOps |
| RBAC coverage test | Per-sprint | Backend team |

---

*Document prepared as part of F-SEC-011 (threat model) and F-SEC-008 (security headers).*  
*Next review: Q4 2026 or after Fase 3 (IAM IC + Lake Formation) deployment.*
