# RULE-FORMULARIOS-CLINICOS-018 — Pressure-injury (LPP) origin classification enum (tipo_lpp, backend serializer)

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Every pressure-injury (LPP) record must be classified as either a 'new lesion' (arose during this care episode) or a 'lesion prior to admission' (pre-existing) - a two-value enum hardcoded directly in the serializer rather than sourced from the shared choices module.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| tipo_lpp | string (choice) |  | nova_lesao \| lesao_previa |

## Outputs

| name | type | unit |
|---|---|---|
| tipo_lpp | string (choice) |  |

## Logic

```text
tipo_lpp = ChoiceField(choices=(
    ("nova_lesao", "Nova lesão"),
    ("lesao_previa", "Lesão prévia a admissão"),
), allow_null=True, allow_blank=True)
```

## Edge cases (as implemented)

allow_null and allow_blank both True -> the field can be submitted empty despite being a clinically meaningful classification.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/serializers/lesao_por_pressao.py` | 8-15 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-lpp-BE-07-001`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-002](../clinical-scoring/RULE-FORMULARIOS-CLINICOS-002-pressure-injury-lpp-staging-wound-bed-composite-assessment-n.md)
- [RULE-FORMULARIOS-CLINICOS-003](../clinical-scoring/RULE-FORMULARIOS-CLINICOS-003-nursing-technician-tecenfermagem-tegumentary-lpp-list-varian.md)

## Notes

New-vs-prior-to-admission distinction is the standard basis for hospital-acquired vs community-acquired pressure-injury quality reporting. Identical inline choices are duplicated verbatim in LPPPDFSerializer.tipo_lpp (same file, lines 62-70) for PDF display (ListChoiceField). Values MATCH the FE forms (RULE-FORMULARIOS-CLINICOS-002/003) tipo_lpp {nova_lesao, lesao_previa} - no divergence.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
