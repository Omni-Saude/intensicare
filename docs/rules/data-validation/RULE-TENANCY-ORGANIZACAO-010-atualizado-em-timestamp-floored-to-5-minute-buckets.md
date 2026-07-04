# RULE-TENANCY-ORGANIZACAO-010 — 'atualizado_em' timestamp floored to 5-minute buckets

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | tenancy-organizacao |

## Rule
SetorSerializer.get_atualizado_em returns the current time with its minute component rounded DOWN to the nearest multiple of 5 (e.g. 14:37 -> 14:35); seconds/microseconds are left unchanged.

## Outputs

| Name | Type | Unit |
|---|---|---|
| atualizado_em | datetime |  |

## Logic

```text
horario = timezone.now().astimezone()
minuto = int(horario.minute - horario.minute % 5)
horario = horario.replace(minute=minuto)
return horario
```

## Edge cases (as implemented)
Only the minute field is replaced - seconds and microseconds from the original timezone.now() call are preserved, so the result is NOT floored to an exact 5-minute clock boundary (e.g. could be 14:35:42.123456, not 14:35:00.000000).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference. Internal cache-bucketing helper: SetorSerializer.get_atualizado_em floors the minute component to the nearest lower multiple of 5. Legacy verbatim confirmed at core/api/v1/serializers/setor.py:112-116 @ 8166c07. Arithmetic (n - n%5) is a standard floor-to-bucket; checked for internal self-consistency only.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/serializers/setor.py` | 112-116 | `8166c07e` | primary |

- Merged from: `RULE-setor-BE-05-002`

## Notes
Likely intended as a cache-bucketing/throttling value for a 'last updated' display, not a literal computation from real data changes.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
