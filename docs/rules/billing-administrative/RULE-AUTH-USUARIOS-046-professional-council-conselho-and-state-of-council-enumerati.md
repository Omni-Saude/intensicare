# RULE-AUTH-USUARIOS-046 — Professional council (conselho) and state-of-council enumerations — backend model vs frontend copy

| Field | Value |
|---|---|
| Cluster | auth-usuarios |
| Category | billing-administrative |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Brazilian professional-registration council and issuing state for a user (credentialing). The frontend independently re-declares the identical 7-value `conselho` codeset (same codes, same order) as `choicesConselho`, using shorter display labels (e.g. "CR de Medicina" vs backend's "Conselho Regional de Medicina") — a cosmetic label-wording difference only; the `estado_conselho` (Brazilian state) enumeration has no frontend copy in this cluster's partitions.

## Inputs

| name | type | range |
|---|---|---|
| conselho | string | CRM\|COREN\|CREFITO\|CRN\|CRFA\|CRP\|AGMT |
| estado_conselho | string (UF) | 27 Brazilian UF codes (AC..TO) |

## Outputs

| name | type |
|---|---|
| credential_scope | string |

## Logic

```text
# Backend — core/models/choices/usuario.py:22-64
UsuarioChoices.conselho() -> CRM(medicine), COREN(nursing), CREFITO(physio/OT),
  CRN(nutrition), CRFA(speech), CRP(psychology), AGMT(Assoc. Goiana de Musicoterapia).
UsuarioChoices.estado_conselho() -> all 26 states + DF.
Usuario.conselho CharField(max_length=7), estado_conselho CharField(max_length=2),
numero_conselho CharField(max_length=20); all null/blank.

# Frontend — src/utils/choicesConselho.ts:1-30 (same 7 codes/order, abbreviated labels)
choicesConselho = [
  {CRM: "CR de Medicina"}, {COREN: "CR de Enfermagem"},
  {CREFITO: "CR de Fisioterapia e Terapia Ocupacional"}, {CRN: "CR de Nutrição"},
  {CRFA: "CR de Fonoaudiologia"}, {CRP: "CR de Psicologia"}, {AGMT: "Ass. Go. de Musicoterapia"},
]
```

## Edge cases (as implemented)

Nullable; no cross-field required-if enforcement (conselho can exist without number). 7 councils; no council for pharmacist/dentist/physician-assistant despite those cargos existing (farmaceutico, odontologo have no matching conselho entry).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/choices/usuario.py` | 22-64 | `8166c07eae` | primary |
| trilhas-frontend | `src/utils/choicesConselho.ts` | 1-30 | `f9656be266` | frontend-copy |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-acesso-BE-04-007`
- `RULE-cargos-FE-02-002`

**Related rules:**

- [RULE-AUTH-USUARIOS-044](RULE-AUTH-USUARIOS-044-clinical-administrative-role-cargo-enumeration-backend-model.md)

## Notes

AGMT is an association (not a formal council) but is grouped in the conselho enum.
---
Cross-check with cargos.ts: farmaceutico and odontologo roles lack a council option here.

---
Label text differs in verbosity/wording only (full council name vs UI-abbreviated "CR de X"); the option list (7 codes, same order) is identical, so this is not treated as a functional divergence per the values/operators/units/option-list/rounding comparison axes.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
