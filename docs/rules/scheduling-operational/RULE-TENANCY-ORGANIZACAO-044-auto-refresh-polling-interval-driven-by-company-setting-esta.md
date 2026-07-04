# RULE-TENANCY-ORGANIZACAO-044 — Auto-refresh polling interval driven by company setting (estabelecimento dashboard)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
The establishment dashboard's list of setores indicators auto-refreshes on an interval equal to the parent company's tempo_atualizacao (seconds) x 1000ms, gated by the global AutoReloadContext "update" toggle. Functionally identical to RULE-empresa-FE-08-002 but implemented independently on a different page.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| empresa.tempo_atualizacao | number | seconds | > 0 |
| update (AutoReloadContext) | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| polling-interval | number | milliseconds |

## Logic
```text
onLoadEmpresa: setReloadTime(empresa.tempo_atualizacao)
if (reloadTime && update) {
  setInterval(_getEstabelecimentoIndicadores, reloadTime * 1000)
}
```

## Edge cases (as implemented)
Same as RULE-empresa-FE-08-002.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento].tsx | 63-93 | f9656be2 | primary |

- Merged from: RULE-empresa-FE-08-003
- Related rules: RULE-TENANCY-ORGANIZACAO-043, RULE-TENANCY-ORGANIZACAO-048

## Notes
Duplicated implementation of the same polling rule; consider consolidating. | Reconciliation: functionally identical polling mechanism independently re-implemented at the empresa dashboard (empresa-FE-08-002) — same formula and gate, different target fetch function and page. No divergence found; kept separate and cross-referenced.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
