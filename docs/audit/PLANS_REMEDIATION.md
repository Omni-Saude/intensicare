# PLANS_REMEDIATION.md — Forensic Remediation Sprint

> **Orquestrador:** Parreira | **Data:** 2026-07-08
> **Fonte:** `docs/audit/REMEDIATION_SPRINT_PROMPT.md`
> **Referência:** `docs/audit/FORENSICS_FINAL_VERDICT.md` (78 findings, 6 dimensões)
> **Risk Level:** L2

## RECON Findings (Verified vs False Positives)

### True Gaps (confirmed real)
- **F-SEC-001:** dashboard.py (routes 21, 43), vitals.py (route 36) — no `Depends(get_current_user)`
- **F-SEC-004:** logout endpoint does NOT call `is_token_blacklisted()` — dead code in jwt.py
- **F-SEC-005:** frontend still uses sessionStorage, not HttpOnly cookies
- **F-SEC-008:** no security headers middleware in main.py
- **F-SEC-009:** no account lockout after failed login attempts
- **F-SEC-011:** no threat model document
- **F-CLIN-001:** NEWS2 scale 2 uses `hypercapnic or bool(supplemental_o2)` — wrong
- **F-CLIN-002:** no FiO2 guard in sofa.py
- **F-CODE-001:** zero eager loading in API endpoints (N+1 risk)
- **F-CODE-002:** `dict[str, Any]` used in domain services
- **F-INT-001:** SQL injection in gold_schema.py (f-strings)
- Multiple architecture gaps (E phase)

### Already Fixed (false positives or previously resolved)
- **F-SEC-006:** admin.py already has `require_admin` on all routes
- **F-SEC-006B:** `require_abac()` already implemented in abac.py:447
- **F-SEC-007:** RateLimitMiddleware already wired in main.py:101-102
- **F-SEC-003:** .gitignore already exists with proper entries
- **jti:** already generated in jwt.py tokens (line 17, 26)
- **is_token_blacklisted:** function exists in jwt.py:43 (but never called)

## FASE A — SECURITY (BLOQUEANTE — Fase de entrada)

### Milestone A.1: Auth Enforcement + Logout Blacklist
| Finding | File | Change |
|---------|------|--------|
| F-SEC-001 | `src/intensicare/api/v1/dashboard.py:21` | Add `Depends(get_current_user)` |
| F-SEC-001 | `src/intensicare/api/v1/dashboard.py:43` | Add `Depends(get_current_user)` |
| F-SEC-001 | `src/intensicare/api/vitals.py:36` | Add `Depends(get_current_user)` |
| F-SEC-004 | `src/intensicare/api/v1/auth.py:122-126` | Call `is_token_blacklisted()` on logout |
| F-SEC-004 | `src/intensicare/api/v1/auth.py:122-126` | Add token to Redis blacklist with TTL |
| F-SEC-009 | `src/intensicare/api/v1/auth.py:login` | Add lockout after 5 failed attempts |

### Milestone A.2: Frontend Token Security
| Finding | File | Change |
|---------|------|--------|
| F-SEC-005 | `frontend-v2/lib/auth.ts` | Migrate sessionStorage → HttpOnly; Secure; SameSite=Strict cookie |
| F-SEC-005 | `frontend-v2/lib/api.ts` | Remove sessionStorage token read; use cookie-based auth |

### Milestone A.3: Dependency Hygiene
- pip-audit: fix CVEs, bump versions in pyproject.toml
- npm audit: fix 3 HIGH vulnerabilities

### Milestone A.4: Security Headers + Threat Model
- Add security headers middleware to main.py
- Create `docs/security/threat-model.md`

## FASE B — CLINICAL SAFETY (paralelo com C, D)
## FASE C — CODE QUALITY (paralelo com B, D)
## FASE D — INTEGRATION (paralelo com B, C)
## FASE E — ARCHITECTURE (dependente de A, B, C, D)
