# RULE-FORMULARIOS-CLINICOS-017 — Intercorrencia (clinical incident/complication) domain-concept icon

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | care-pathway |
| Type | workflow |
| Status | AMBIGUOUS |
| Confidence | low |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A dedicated icon component 'Intercorrencia.jsx' exists, named after the Portuguese clinical term 'intercorrência' (adverse event / complication / unplanned clinical occurrence). Its existence as a first-class icon signals a distinct feature/workflow for recording or flagging clinical intercorrências, though no logic is present in this icon file (only SVG artwork).

## Inputs

_None._

## Outputs

_None._

## Logic

```text
# No executable logic in this file; icon existence is the only evidence.
ICON_NAME "Intercorrencia" => implies elsewhere: a workflow/form/list for
recording patient "intercorrências" (adverse events/complications).
```

## Edge cases (as implemented)

AMBIGUOUS: the actual intercorrência recording workflow (fields, required data, severity classification, who may record it) is not part of this partition and was not observed; this entry documents only the domain concept's existence based on the icon naming. (The concrete incident forms are RULE-FORMULARIOS-CLINICOS-007/009/015.)

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/icons/Intercorrencia.jsx` | 1-9 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-CLINICAL-FE-09-013`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-007](../triage-eligibility/RULE-FORMULARIOS-CLINICOS-007-home-care-incident-triage-urgency-grade-and-symptom-classifi.md)
- [RULE-FORMULARIOS-CLINICOS-009](RULE-FORMULARIOS-CLINICOS-009-home-care-incident-intervention-conduct-with-conditional-spe.md)
- [RULE-FORMULARIOS-CLINICOS-015](RULE-FORMULARIOS-CLINICOS-015-home-care-incident-disposition-outcome-enum.md)

## Notes

No logic beyond SVG markup found; kept as AMBIGUOUS per ground rules (not dropped, to avoid silent loss).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
