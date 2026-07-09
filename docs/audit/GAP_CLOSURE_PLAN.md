# GAP_CLOSURE_PLAN.md — IntensiCare Forensic Remediation
## 38 Gaps → 10 Phases → 100% DONE or BLOCKED

**Created:** 2026-07-09 08:15 UTC-3
**Orchestrator:** Parreira (SOUL.md v3)
**Baseline:** `audit-results/CONSOLIDATED_FORENSIC_AUDIT.md`

---

## STATUS LEGEND
- ⬜ OPEN — not started
- 🔄 IN_PROGRESS — agent dispatched
- ✅ DONE — gatekeeper passed
- 🚫 BLOCKED — AWS/human dependency; documented in BLOCKERS.md

---

## PHASE TRACKER

| # | Phase | Gaps | Status | Started | Completed |
|---|-------|------|--------|---------|-----------|
| 0 | RECON & PLAN | — | ✅ DONE | 08:15 | 08:15 |
| 1 | Data Model Criticals | C3, C4, C5 | 🔄 IN_PROGRESS | 08:16 | — |
| 2 | Movimentação ADT | C1, C2, H2 | ⬜ OPEN | — | — |
| 3 | YAMLs + Domain Svc | H1, H07* | ⬜ OPEN | — | — |
| 4 | Prescricao | H3, H4, H5 | ⬜ OPEN | — | — |
| 5 | Formularios + Evolucoes | H8, H9, H10, H11, M8 | ⬜ OPEN | — | — |
| 6 | Frontend ADR | H12, H13, M1, M9, M10 | ⬜ OPEN | — | — |
| 7 | Security | C7, H6, H14, H15, M6, M7, M11 | ⬜ OPEN | — | — |
| 8 | Testing & Quality | M2, M3, M4, M5 | ⬜ OPEN | — | — |
| 9 | Infra & DR | C6, H7 | ⬜ OPEN | — | — |
| 10 | Polish | L1, L2, L3, L4, M12 | ⬜ OPEN | — | — |

---

## GAP INVENTORY (38 gaps)

### 🔴 CRITICAL (7)
| ID | Gap | Status | Phase |
|----|-----|--------|-------|
| C1 | CDC consumer ADT | 🚫 BLOCKED (AWS) | 2 |
| C2 | 3 tabelas ADT (2 missing: PatientLocationCurrent, DischargeSummary) | 🔄 IN_PROGRESS | 2 |
| C3 | Storage in-memory → PostgreSQL | 🔄 IN_PROGRESS | 1 |
| C4 | encounter_id no PatientPathway | 🔄 IN_PROGRESS | 1 |
| C5 | Content-addressing SHA-256 | 🔄 IN_PROGRESS | 1 |
| C6 | ECS Task Definitions | 🚫 BLOCKED (AWS) | 9 |
| C7 | RBAC granular | ⬜ OPEN | 7 |

### 🟡 HIGH (15)
| ID | Gap | Status | Phase |
|----|-----|--------|-------|
| H1 | 8 pathway YAMLs missing | ⬜ OPEN | 3 |
| H2 | 74 DMN movement rules | 🚫 BLOCKED (AWS/C1) | 2 |
| H3 | Prescricao API routes diverge | ⬜ OPEN | 4 |
| H4 | Composable validation pipeline | ⬜ OPEN | 4 |
| H5 | ANVISA drug database | ⬜ OPEN | 4 |
| H6 | IAM SSO test | 🚫 BLOCKED (IdP) | 7 |
| H7 | DR configuration | ⬜ OPEN | 9 |
| H8 | Cross-field validation (RASS→CAM-ICU) | ⬜ OPEN | 5 |
| H9 | Form versioning | ⬜ OPEN | 5 |
| H10 | Pre-population MovimentacaoStateStore | 🚫 BLOCKED (C1) | 5 |
| H11 | 14 clinical role templates | ⬜ OPEN | 5 |
| H12 | Per-tenant white-label | ⬜ OPEN | 6 |
| H13 | Neumorphic elevation tokens | ⬜ OPEN | 6 |
| H14 | Query timeout PostgreSQL | ⬜ OPEN | 7 |
| H15 | Account lockout | ⬜ OPEN | 7 |

### 🟠 MEDIUM (12)
| ID | Gap | Status | Phase |
|----|-----|--------|-------|
| M1 | ~30 tailwind color violations | ⬜ OPEN | 6 |
| M2 | 42 legacy test failures | ⬜ OPEN | 8 |
| M3 | Test coverage 31.2% → 80% | ⬜ OPEN | 8 |
| M4 | Style Dictionary in CI | ⬜ OPEN | 8 |
| M5 | L1/L2 harness wired | ⬜ OPEN | 8 |
| M6 | SBOM in CI | ⬜ OPEN | 7 |
| M7 | WS per-message auth | ⬜ OPEN | 7 |
| M8 | Offline-first submission | ⬜ OPEN | 5 |
| M9 | Drawer overlay stack manager | ⬜ OPEN | 6 |
| M10 | Breadcrumb component | ⬜ OPEN | 6 |
| M11 | admin:admin RTSP fix | ⬜ OPEN | 7 |
| M12 | SEPSE migration documented | ⬜ OPEN | 10 |

### 🟢 LOW (4)
| ID | Gap | Status | Phase |
|----|-----|--------|-------|
| L1 | Contrast fix (verify.py) | ⬜ OPEN | 10 |
| L2 | Python version doc | ⬜ OPEN | 10 |
| L3 | OPA/Rego policies | ⬜ OPEN | 10 |
| L4 | Phantom paths cleaned | ✅ DONE | 10 |

---

## DEPENDENCY ORDER (execution sequence)
```
C4 ──► C5
C3 ──► independent
C2 ──► C1 ──► H2 ──► H10
C7 ──► independent (can run parallel with F1)
H1 ──► independent
H3 ──► H4 ──► H5
H8, H9, M8 ──► independent
H11 ──► independent
H12, H13, M1, M9, M10 ──► independent from backend
H14, H15, M6, M7, M11 ──► independent
M2 ──► M3 (coverage after tests fixed)
M4, M5 ──► independent
C6, H7 ──► BLOCKED (AWS)
L1-L4, M12 ──► independent (last)
```

## CURRENT STATE (validated 2026-07-09 08:15)
- C2: AdmissionEpisode EXISTS in models/movimentacao.py ✅; PatientLocationCurrent + DischargeSummary MISSING
- C4: encounter_id = 0 occurrences in pathway.py — CONFIRMED ABSENT
- C5: definition_version_id = 0 occurrences — CONFIRMED ABSENT
- C3: domain_prescricao.py has 2 `= {}` patterns — CONFIRMED IN-MEMORY
- H1: 4/12 YAML definitions written — 8 MISSING
- L4: Phantom paths already cleaned ✅

---

*Plano vivo — atualizado a cada milestone concluído.*
