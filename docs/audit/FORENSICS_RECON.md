# FORENSICS RECON — IntensiCare v2 Platform

**Data:** 2026-07-09 | **Auditor:** Niemeyer (System Architect)  
**Escopo:** Full-stack forensics comparing desired architecture (docs/) vs actual implementation (src/, frontend-v2/)

## Recon Summary

| Artefact | Desired (Docs) | Actual (Code) | Gap |
|----------|---------------|---------------|-----|
| ADRs | 31 (0001-0029 + README) | 28 proposed, 2 accepted, 1 implemented | **27 pending ratification** |
| TDDs | 5 (trilhas-engine, prescricao, movimentacao, formularios, evolucoes) | 5 TDDs written | 0 missing |
| OpenAPI Contracts | 15 contracts, 50 operations | 68 REST endpoints + 1 WS across 22 routers | **Naming gaps** (see below) |
| Rules (YAML) | 279 rules across 27 domains | 24/27 domains have domain services | 3 domains without services |
| Domain Services | — | 24 domain_*.py files (7,577 total LOC) | — |
| Test Files | — | 93 test files | — |
| Frontend (v2) | Described in ADRs 0001-0019 | ~33 pages in frontend-v2/app/ | **ADR-described features not fully verified** |
| Legacy Frontend | — | 10 TSX components | Deprecated |

## Contract Naming Gaps

| Contract File | API Router | Match? |
|--------------|-----------|--------|
| antimicrobial-openapi.yaml | antimicrobial.py | ✓ |
| cadastros-ui-openapi.yaml | NO ROUTER | **GAP** (UI-only contract, intentional?) |
| deterioration-openapi.yaml | deterioration.py | ✓ |
| documentacao-openapi.yaml | documentacao.py | ✓ |
| eficiencia-openapi.yaml | efficiency.py | ✓ (name mismatch) |
| evolucoes-openapi.yaml | evolucoes.py | ✓ |
| formularios-clinicos-openapi.yaml | formularios.py | ✓ (name mismatch) |
| indicadores-openapi.yaml | indicators.py | ✓ (name mismatch) |
| movimentacao-openapi.yaml | movimentacao.py | ✓ |
| pathways-openapi.yaml | pathways.py | ✓ |
| prescricao-openapi.yaml | prescricao.py | **5 vs 6 endpoints** |
| prophylaxis-openapi.yaml | prophylaxis.py | ✓ |
| sedacao-openapi.yaml | sedacao.py | ✓ |
| stability-openapi.yaml | stability.py | ✓ |
| ventilation-openapi.yaml | ventilation.py | ✓ |

## API Routers Without Contracts

| Router | Endpoints | Notes |
|--------|-----------|-------|
| admin.py | 3 | No contract exists |
| alert_routing.py | 5 | No contract exists |
| alerts.py | 5 | No contract exists |
| auth.py | 3 | No contract exists |
| dashboard.py | 2 | No contract exists |
| events.py | 1 (WS stream) | No contract exists |
| health.py | 1 | No contract exists |
| registry.py | 6 | No contract exists |
| ws.py | 1 | No contract exists |

## Rule Domain Gaps

| Domain | Rules (YAML) | Domain Service | Gap |
|--------|-------------|----------------|-----|
| sepse | 65 | domain_sepsis.py (1,022 LOC) | ✓ |
| balanco-hidrico | 31 | domain_fluid_balance.py (427 LOC) | ✓ |
| sedacao | 21 | domain_sedacao.py (609 LOC) | ✓ |
| tenancy-organizacao | 18 | domain_tenancy.py (594 LOC) | ✓ |
| estabilidade | 18 | domain_estabilidade.py (757 LOC) | ✓ |
| clinical-scoring | 18 | NO DOMAIN SERVICE | **GAP** |
| ventilacao | 14 | domain_ventilacao.py (433 LOC) | ✓ |
| operacional-infra | 14 | domain_operacional.py (443 LOC) | ✓ |
| piora-clinica | 11 | domain_piora_clinica.py (847 LOC) | ✓ |
| movimentacao-adt | 11 | domain_movimentacao.py (731 LOC) | ✓ |
| eficiencia | 10 | domain_eficiencia.py (667 LOC) | ✓ |
| indicadores-etl | 6 | NO DOMAIN SERVICE | **GAP** |
| formularios-clinicos | 6 | domain_formularios.py (719 LOC) | ✓ |
| sinais-vitais | 5 | vitals.py (service) | ✓ |
| nutricao | 5 | NO DOMAIN SERVICE | **GAP** |
| evolucoes | 5 | domain_evolucoes.py (1,331 LOC) | ✓ |
| profilaxia | 3 | domain_profilaxia.py (296 LOC) | ✓ |
| comunicacao | 3 | domain_comunicacao.py (264 LOC) | ✓ |
| equilibrio | 2 | domain_electrolyte.py (629 LOC) | ✓ |
| auth-usuarios | 2 | auth/ module | ✓ |
| alertas | 2 | domain_alertas.py (113 LOC) | ✓ |
| trilhas-engine | 1 | domain_trilhas_engine.py (433 LOC) | ✓ |
| prescricao | 1 | domain_prescricao.py (855 LOC) | ✓ |
| antimicrobiano | 1 | domain_antimicrobiano.py (311 LOC) | ✓ |

## ADR Ratification Status

| Status | Count | ADRs |
|--------|-------|------|
| **accepted** | 2 | 0001 (frontend stack), 0019 (Radix+Tailwind ratification) |
| **implemented** | 1 | 0020 (trilhas-engine architecture) |
| **proposed** | 28 | 0002-0018, 0021-0029 |

**⚠️ Critical finding:** 28 of 31 ADRs are still "proposed" — not ratified. This means the architecture baseline is **not yet governance-grade**. The implementation exists, but the architectural decisions that should govern it have not been formally approved.

## Gate Decision: BLOQUEADO (precisa de ratificação de ADRs)

A auditoria forense pode prosseguir, mas os resultados devem ser contextualizados: a implementação está à frente da governança. 28 ADRs precisam ser ratificados antes que qualquer veredito de "GO" possa ser emitido com confiança.
