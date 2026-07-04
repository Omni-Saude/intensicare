# RULE-FORMULARIOS-CLINICOS-022 — Vascular-access / dressing tracked-field enum

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Maps device/dressing tracking field codes to labels, defining the set of attributes recorded for indwelling devices and dressings (catheter in-use, insertion/dressing dates, next change, phlebitis, palpable thrill, external-institution insertion).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| value | string field code |  | one of the 10 keys |

## Outputs

| name | type | unit |
|---|---|---|
| label | string ("" if unknown) |  |

## Logic

```text
get_humanized_name(value) = {
  em_uso:"Em uso", local:"Local", data_insercao:"Data de insercao",
  data_curativo:"Data do curativo", curativo:"Curativo",
  aspecto_do_curativo:"Aspecto do curativo", data_proxima_troca:"Data da proxima troca",
  inserido_em_outra_instituicao:"Inserido em outra instituicao",
  fremito_palpavel:"Fremito palpavel", flebite:"Flebite",
}.get(value, "")
```

## Edge cases (as implemented)

Uses .get(value, "") so unknown codes render as empty string (no error).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/templatetags/formulario.py` | 156-170 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-diagnostico-BE-09-002`

**Related rules:** _none_

## Notes

fremito_palpavel (palpable thrill) and flebite (phlebitis) indicate AV-fistula / peripheral-line monitoring; data_proxima_troca drives dressing-change scheduling. Field catalog only; thresholds/scheduling elsewhere.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
