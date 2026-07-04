# RULE-MOVIMENTACAO-ADT-048 — Fixed 3-second minimum spinner on bed camera page

| Field | Value |
|---|---|
| Category | data-validation |
| Type | workflow |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
The bed camera ("VideoUtiPage") view forces a loading spinner to display for exactly 3000ms after mount via a hardcoded setTimeout, independent of whether the occupancy data fetch or the video stream itself has actually finished loading.

## Outputs

| Name | Type | Unit |
|---|---|---|
| loading | boolean |  |

## Logic
```text
useMountEffect(() => {
  setTimeout(() => setLoading(false), 3000)
})
```

## Edge cases (as implemented)
If the underlying data/video stream takes longer than 3s to load, the spinner disappears prematurely; if it loads faster, the user waits an artificial 3s regardless. Best interpretation: an intentional UX delay to mask stream negotiation time, not tied to any real readiness event.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao].tsx` | 38-42 | `f9656be2` | primary |

- Merged from: RULE-ocupacao-FE-08-002
- Related rules: RULE-MOVIMENTACAO-ADT-010, RULE-MOVIMENTACAO-ADT-054

## Notes
Flagged ambiguous because intent (UX delay vs missing readiness-event wiring) cannot be confirmed from this file alone.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
