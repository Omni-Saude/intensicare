# RULE-FORMULARIOS-CLINICOS-001 — Pressure-injury (LPP) NPUAP staging enum

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | clinical-scoring |
| Type | scoring |
| Status | OK |
| Confidence | high |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
Canonical pressure-injury (Lesao Por Pressao) staging classification used by AvaliacaoGlobal.grau_ou_estagio / estagio_lpp. NPUAP/EPUAP-style stage categories.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| grau_ou_estagio / estagio_lpp | enum |  | suspeita_de_lesao\|estagio_i\|estagio_ii\|estagio_iii\|estagio_iv\|nao_graduavel |

## Outputs

| name | type | unit |
|---|---|---|
| LPP stage | string |  |

## Logic

```text
estagio_lpp() = (
  ("suspeita_de_lesao", "Suspeita de lesão profunda dos tecidos"),
  ("estagio_i",   "I"),
  ("estagio_ii",  "II"),
  ("estagio_iii", "III"),
  ("estagio_iv",  "IV"),
  ("nao_graduavel", "Não graduável ou inclassificável"),
)
```

## Edge cases (as implemented)

Classification enum; no numeric score. Six categories = NPUAP I-IV + suspected deep tissue injury + unstageable.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** NPUAP/EPUAP/PPPIA Pressure Injury Staging System (Edsberg LE et al., Revised NPUAP Pressure Injury Staging System, J Wound Ostomy Continence Nurs 2016;43(6):585-597). Original 6-category NPUAP set: Stage I-IV + Suspected Deep Tissue Injury + Unstageable. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC5098472/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| estagio_lpp=estagio_i | Stage I (non-blanchable erythema, intact skin) | "I" | yes |
| estagio_lpp=suspeita_de_lesao | Suspected Deep Tissue Injury (intact purple/maroon skin or blood-filled blister) | "Suspeita de lesão profunda dos tecidos" | yes |
| estagio_lpp=nao_graduavel | Unstageable (depth obscured by slough/eschar) | "Não graduável ou inclassificável" | yes |

**Verifier notes**

Enum reproduces the canonical NPUAP 6-category staging set (I-IV plus SDTI plus Unstageable) faithfully. This is the pre-2016 naming ("suspeita de lesão profunda"/SDTI, "não graduável"/Unstageable); the 2016 revision renamed "ulcer"->"injury" and dropped the word "suspected" from DTI but kept the same 6 clinical tiers, so no clinical divergence. No numeric score computed. Categories and labels match reference.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/choices/avaliacao_global.py` | 127-154 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-wound-BE-06-001`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-002](RULE-FORMULARIOS-CLINICOS-002-pressure-injury-lpp-staging-wound-bed-composite-assessment-n.md)
- [RULE-FORMULARIOS-CLINICOS-003](RULE-FORMULARIOS-CLINICOS-003-nursing-technician-tecenfermagem-tegumentary-lpp-list-varian.md)
- [RULE-FORMULARIOS-CLINICOS-018](../data-validation/RULE-FORMULARIOS-CLINICOS-018-pressure-injury-lpp-origin-classification-enum-tipo-lpp-back.md)

## Notes

Backend canonical staging enum. The identical six-value staging set is re-implemented in the frontend wound-assessment forms (RULE-FORMULARIOS-CLINICOS-002 and -003); staging values MATCH across BE and FE (no divergence on staging).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
