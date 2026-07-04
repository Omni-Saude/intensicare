# RULE-BALANCO-HIDRICO-017 — SinaisVitais.anterior - leitura anterior de sinais vitais

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Returns the SECOND most recent vital-signs record for an admission (the reading before the current one), or None if fewer than two exist.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| nr_atendimento | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| anterior | — | — |

## Logic
```text
try:
    return SinaisVitais.objects.filter(balanco__nr_atendimento=nr_atendimento).order_by("-criado_em")[1]
except IndexError:
    return None
```

## Edge cases (as implemented)
Index [1] = second newest. Does NOT filter deletado_em, so soft-deleted readings can be returned as "previous". Returns None when 0 or 1 readings exist.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal data-access helper: returns the 2nd-most-recent SinaisVitais row (order_by -criado_em, index [1]) for an admission; used as the 'previous reading' baseline for sepse change-detection criteria. (n/a)
- Test vectors: 3/3 match
- Internal business/data-access rule with no published clinical source to check against; flag for internal review,
not treated as wrong. Behavioral observation only: the query does NOT filter deletado_em, so a soft-deleted
reading can be returned as the 'previous' vital sign — worth an internal-review note, not a reference discrepancy.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/balanco_hidrico/sinais_vitais.py | 115-123 | 8166c07e | primary |
- Merged from: RULE-balanco-BE-06-007
- Related rules: RULE-BALANCO-HIDRICO-016

## Notes
Consumed by sepse criterio_3 (ventilation change) and criterio_7 (consciousness change).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
