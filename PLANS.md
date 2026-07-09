# PLANS.md — Pós-Auditoria V2 + Trilhas Engine Remediation

> **Orquestrador:** Parreira | **Data:** 2026-07-08
> **Fontes:** FORENSICS_FINAL_VERDICT_V2.md + PROMPT_TRILHAS_ENGINE.md
> **Score Atual:** 80/100 | **Alvo:** >85 universal

## Envelope

| Campo | Valor |
|-------|-------|
| **Goal** | Resolver 4 condições short-term + Milestone 1 do Trilhas Engine |
| **Risk** | L2 |
| **Scope** | alerts.py, health.py, trilhas_*.py, _work/alerts/, scripts/ |

## Task Inventory

### Short-Term (GO Conditions — Wave 1, paralelo)
| # | ID | Severity | File(s) | Effort |
|---|-----|----------|---------|--------|
| S1 | F-SEC-001b | HIGH | `alerts.py` (list_alerts + trace_alert) | 2h → agent |
| S2 | F-INT-006 | MEDIUM | `health.py` (concurrent checks) | 3h → agent |
| S3 | Tests | MEDIUM | `test_vitals.py` (auth tokens) | 4h → agent |
| S4 | npm | LOW | `frontend-v2/` (audit fix) | 30min → agent |

### Trilhas Engine (Milestone 1 — Wave 2)
| # | ID | Severity | Scope | Effort |
|---|-----|----------|-------|--------|
| T1 | F-ARCH-001/002 | CRITICAL | Schema + CI Gates + Compiler | XL |

## Wave 1 — Parallel (no shared files)

### Agent S1: F-SEC-001b — Auth on alert endpoints
- File: `src/intensicare/api/v1/alerts.py`
- Add `Depends(get_current_user)` to `list_alerts` (line 84) and `trace_alert` (line 238)
- Keep existing auth on other endpoints intact

### Agent S2: F-INT-006 — Concurrent health checks
- File: `src/intensicare/api/v1/health.py`
- Run DB, Redis, Athena checks concurrently via `asyncio.gather()`

### Agent S4: npm audit fix
- Dir: `frontend-v2/`
- Run `npm audit fix` for LOW vulns

## Wave 2 — Depends on Wave 1

### Agent T1: Trilhas Engine Milestone 1 — Schema + CI Gates
- Files: schema, validate_alerts.py, CI workflow, pyproject.toml, test

## Validation Gates
- GATE-SEC: security-manager after S1
- GATE-PROD: production-validator after all waves
- pytest: all affected test files
