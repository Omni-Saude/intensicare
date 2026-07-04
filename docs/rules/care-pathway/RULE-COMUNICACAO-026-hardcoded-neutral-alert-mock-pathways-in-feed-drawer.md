# RULE-COMUNICACAO-026 — Hardcoded neutral-alert mock pathways in feed drawer

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | comunicacao |

## Rule
When opening the recommendations drawer from a feed item, the feed page passes a hardcoded array of four "mock" care pathways (trilhasMock) — Reinternação, Alta Melhorada, Segurança do paciente, Restrições alimentares — each with a fixed alerta value of "NEUTRO", instead of deriving pathway/alert state from the actual occupancy data returned for that patient.

## Outputs
| Name | Type | Unit |
|---|---|---|
| trilhasMock | array of 4 Trilha objects | — |

## Logic
```text
trilhasMock = [
  { nome: "Reinternação",             tipo: "reinternacao",          alerta: "NEUTRO", id: "0" },
  { nome: "Alta Melhorada",            tipo: "alta_melhorada",        alerta: "NEUTRO", id: "1" },
  { nome: "Segurança do paciente",      tipo: "seguranca_paciente",    alerta: "NEUTRO", id: "2" },
  { nome: "Restrições alimentares",     tipo: "restricoes_alimentares",alerta: "NEUTRO", id: "3" },
]
<TabRecomendacoes trilhasMock={trilhasMock} ... ocupacao={drawerContent.data} .../>
```

## Edge cases (as implemented)
Because alerta is fixed to "NEUTRO" for all four pathways regardless of the patient's actual clinical state, any alert-coloring/urgency logic inside TabRecomendacoes (out of FE-08 scope) driven by these four mock entries will always render as neutral for feed-opened drawers, even if the patient truly has an active/urgent alert on one of these pathways.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa]/feed/index.tsx | 155-181, 263-274 | f9656be2 | primary |
- Merged from: RULE-feed-FE-08-003
- Related rules: RULE-COMUNICACAO-024, RULE-COMUNICACAO-025

## Notes
Recorded verbatim; flagged as a likely-unfinished/stub implementation rather than corrected, per ground rules. Only this feed page passes trilhasMock; other pages that render TabRecomendacoes (chats/index.tsx, setor/[id_setor].tsx) do not pass this prop.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
