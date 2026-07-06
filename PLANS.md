# PLANS.md — Forensic Remediation Execution Plan

**Date:** 2026-07-06
**Orchestrator:** Parreira (SOUL.md v3 Agentic Loop)
**Mission:** Close ALL 25 gaps + gatekeeper findings. GO from production-validator + security-manager.
**Branch:** `build/v2-fase-0`

---

## Phase Execution Status

| Phase | Status | Gaps | Start | End |
|-------|--------|------|-------|-----|
| A: CRITICAL | ✅ COMPLETE | 7/7 | 2026-07-06 | 2026-07-06 |
| B: HIGH | 🔄 IN PROGRESS | 5 | 2026-07-06 | — |
| C: MEDIUM | ⏳ PENDING | 15 | — | — |

---

## Phase A — ✅ COMPLETE (7/7)

| Gap | Fix | Verified |
|-----|-----|----------|
| GAP-001 | RateLimitMiddleware wired (main.py:82-83) | ✅ grep=2 |
| GAP-002 | alembic.ini → %(DATABASE_URL)s | ✅ grep=0 |
| GAP-004 | BedCard.tsx → CSS custom props | ✅ grep=0, tokens=260/0 |
| GAP-005 | admin/thresholds bandStyles | ✅ |
| GAP-003 | JWT jti (uuid4) emitido | ✅ |
| GATE-SEC-01 | _validate_production_secrets | ✅ 3/3 tests |
| GATE-PROD-01 | auth.py removido | ✅ auth/ intact |

---

## Phase B: 🟠 HIGH Priority

### Wave B1 — Parallel (no deps)

| M# | Gap | Estimate | Tool | Agent |
|----|-----|----------|------|-------|
| B1 | GAP-010 — Legacy archive | 5 min | delegate_task | tdd-london-swarm |
| B2 | GAP-006-B1 — Clinical components (AlertCard, ScoreTimeline, VitalsChart) | 30 min | delegate_task | tdd-london-swarm |
| B3 | GAP-007 — design-tokens completion (11 JSON) | 60 min | delegate_task | tdd-london-swarm |

### Wave B2 — Parallel (after B1/B3)

| M# | Gap | Estimate | Tool | Agent |
|----|-----|----------|------|-------|
| B4 | GAP-008 — 3 clinical screens | 90 min | hermes chat -q -s | tdd-london-swarm |
| B5 | GAP-006-B2+B3 — 10 remaining frontend files | 60 min | delegate_task | tdd-london-swarm |

### Wave B3 — Sequential (after B2/B4)

| M# | Gap | Estimate | Tool | Agent |
|----|-----|----------|------|-------|
| B6 | GAP-009 — CI contract/storm/drills | 120 min | hermes chat -q -s | ops-cicd-github |

---

## Gatekeepers (Phase B)

| Milestone | Gatekeeper | When |
|-----------|-----------|------|
| All B waves | production-validator | After Phase B complete |
| All B waves | security-manager | After Phase B complete |
| B6 (CI) | ops-compliance-gate | contract tests LGPD/ANS |
