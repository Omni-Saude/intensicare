# PROMPT.md — Niemeyer (Sprint 5-8 Governance)

> **Auto-prompt:** Niemeyer executando sua própria faixa de governança
> **Data:** 2026-07-07

---

## Mission

Produzir **ADRs + Contratos OpenAPI + TDDs** para os 4 domínios críticos do Sprint 5-8, estabelecendo a baseline de governança antes que parreira e product-designer iniciem implementação.

## Entregáveis

### ADRs (Architecture Decision Records)

| ADR | Domínio | Decisão |
|-----|---------|---------|
| ADR-020 | trilhas-engine | Arquitetura do motor de pathways: state machine vs rule engine vs workflow engine |
| ADR-021 | trilhas-engine | Modelo de dados: pathways versionados? Snapshots de estado? |
| ADR-022 | ventilacao | Unificação com domain_respiratory.py existente ou serviço separado? |
| ADR-023 | estabilidade | Modelo de scoring: threshold-based vs ML-based vs híbrido |

### Contratos OpenAPI
- `docs/contracts/pathways-openapi.yaml` — 6 endpoints
- `docs/contracts/ventilation-openapi.yaml` — 2 endpoints
- `docs/contracts/stability-openapi.yaml` — 2 endpoints
- `docs/contracts/deterioration-openapi.yaml` — 2 endpoints

### TDDs (Technical Design Documents)
- `docs/tdd/tdd-trilhas-engine.md` — design completo da engine
- `docs/tdd/tdd-ventilacao.md` — integração com dados ventilatorios

## Regras
- ADRs no formato MADR (Markdown ADR)
- Contratos seguem padrão OpenAPI 3.1 dos contratos existentes
- TDDs incluem: visão geral, bounded contexts, modelo de dados, APIs, fluxos, segurança
