# RULE-MOVIMENTACAO-ADT-037 — Automatic-pathway bed trilhas only populate when the bed is occupied

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
_get_trilhas_automaticas returns an empty list unless instance.ocupado is True; when occupied, it iterates the bed's configured automatic pathway models and includes the latest record's payload for each pathway that has one.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| instance.ocupado | boolean |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| trilhas | array of object |  |

## Logic
```text
trilhas = []
if instance.ocupado:
    for Trilha in instance.get_trilhas_automaticas():
        trilha = get_trilha(Trilha, instance, instance.tipo)   # latest record for this leito/pathway
        if trilha:
            trilhas.append(trilha.get_payload())
return trilhas
```

## Edge cases (as implemented)
An unoccupied bed always yields an empty trilhas list even if historical trilha records exist.

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/leito.py` | 181-189 | `8166c07e` | primary |

- Merged from: RULE-leito-BE-05-005
- Related rules: RULE-MOVIMENTACAO-ADT-018, RULE-MOVIMENTACAO-ADT-036

## Notes
get_trilha/instance.get_trilhas_automaticas are defined outside this partition.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
