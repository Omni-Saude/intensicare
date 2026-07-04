# RULE-TENANCY-ORGANIZACAO-043 — Auto-refresh polling interval driven by company setting (empresa dashboard)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
The company dashboard's list of estabelecimentos indicators auto-refreshes on an interval equal to the company's configured tempo_atualizacao (in seconds) converted to milliseconds, but only while the global AutoReloadContext "update" toggle is enabled.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| currentEmpresa.tempo_atualizacao | number | seconds | > 0 (falsy/0 disables polling since the effect guards on truthiness) |
| update (AutoReloadContext) | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| polling-interval | number | milliseconds |

## Logic
```text
if (currentEmpresa?.tempo_atualizacao && update) {
  setInterval(_getEmpresaIndicadores, currentEmpresa.tempo_atualizacao * 1000)
}
// also: if timer running and update becomes false -> clearInterval
// also: re-fetches immediately whenever id_empresa or update changes
```

## Edge cases (as implemented)
tempo_atualizacao == 0 or undefined -> guarded as falsy -> no interval created (effectively disables auto-refresh, no error).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/pages/empresa/[id_empresa].tsx | 57-87 | f9656be2 | primary |

- Merged from: RULE-empresa-FE-08-002
- Related rules: RULE-TENANCY-ORGANIZACAO-044, RULE-TENANCY-ORGANIZACAO-048

## Notes
Same pattern duplicated at estabelecimento dashboard (RULE-empresa-FE-08-003). | Reconciliation: functionally identical polling mechanism independently re-implemented at the establishment dashboard (empresa-FE-08-003) — same formula (tempo_atualizacao * 1000), same AutoReloadContext gate, different target fetch function and page. No divergence found between the two copies; kept as separate rules (per the variant-preservation instruction for the same pattern applied at two hierarchy levels) and cross-referenced via related, rather than merged.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
