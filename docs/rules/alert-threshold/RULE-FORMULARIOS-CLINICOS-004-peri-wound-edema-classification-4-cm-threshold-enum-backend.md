# RULE-FORMULARIOS-CLINICOS-004 — Peri-wound edema classification - 4 cm threshold enum (backend canonical)

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | alert-threshold |
| Type | threshold |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Peri-wound edema classification enum encoding numeric extent thresholds around the 4 cm boundary (with and without pitting/sulco, plus crepitation). Backend canonical definition.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| edema_tecido category | enum | cm (extent around wound) |  |

## Outputs

| name | type | unit |
|---|---|---|
| edema classification | string |  |

## Logic

```text
edema_tecido() = (
  ("minimo_edema",              "Mínimo edema ao redor da ferida."),
  ("edema_sem_sulco_menor_4cm", "Edema sem fazer sulco que se estende < 4 cm ao redor da ferida."),
  ("edema_sem_sulco_maior_4cm", "Edema sem fazer sulco que se estende >= 4 cm ao redor da ferida."),
  ("edema_com_sulco_menor_4cm", "Edema com sulco que se estende < 4 cm ao redor da ferida."),
  ("crepitacao_maior_4cm",      "Crepitação e/ou edema com formação de sulco estende-se >= 4 cm."),
)
```

## Edge cases (as implemented)

Boundary at 4 cm; '< 4 cm' vs '>= 4 cm' partitions. Labels distinguish pitting (sulco) vs non-pitting; top tier adds crepitation.

## Divergence

Top-tier stored VALUE differs by implementation for the same clinical label ('crepitation and/or pitting edema extending >= 4 cm'): backend + TecEnfermagem FE use "crepitacao_maior_4cm"; nursing + dietitian FE (dataFormEnfermagem.ts:220, dataFormNutricionista.ts:307) use "crepitacao_edema_com_sulco_maior_4cm". NEW reconciliation finding: backend agrees with TecEnfermagem, diverges from nursing/dietitian.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** Bates-Jensen Wound Assessment Tool (BWAT), item 'Peripheral Tissue Edema': 1=none; 2=non-pitting <4 cm; 3=non-pitting >4 cm; 4=pitting <4 cm; 5=crepitus and/or pitting >4 cm. ([source](https://aci.health.nsw.gov.au/__data/assets/pdf_file/0010/388243/22.-Bates-Jensen-wound-assessment-tool-BWAT.pdf))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | ok |
| ranges | ok |
| rounding | diff |
| cutoffs | ok |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| finding=non-pitting edema extending 3 cm | BWAT score 2 (non-pitting <4 cm) | edema_sem_sulco_menor_4cm | yes |
| finding=non-pitting edema extending exactly 4 cm | BWAT undefined at =4 cm (score 2 says <4, score 3 says >4) | edema_sem_sulco_maior_4cm (>=4 cm) -> legacy resolves the =4 cm gap into the higher tier | yes |
| finding=pitting edema extending 2 cm | BWAT score 4 (pitting <4 cm) | edema_com_sulco_menor_4cm | yes |
| finding=crepitus + pitting extending 5 cm | BWAT score 5 (crepitus and/or pitting >4 cm) | crepitacao_maior_4cm | yes |

**Verifier notes**

The backend canonical enum reproduces the BWAT Peripheral Tissue Edema item EXACTLY: 5 tiers, the 4 cm boundary, and the non-pitting/pitting/crepitus progression all match the reference. Only nuance vs the reference: BWAT labels use '<4 cm' and '>4 cm' (leaving exactly 4 cm undefined), whereas legacy uses '<4 cm' and '>=4 cm', which actually closes that ambiguity - not a clinical error. The extraction-flagged DISCREPANCY is the cross-implementation stored-VALUE drift: backend + TecEnfermagem use "crepitacao_maior_4cm" while nursing/dietitian FE use "crepitacao_edema_com_sulco_maior_4cm" for the same top tier -> internal data inconsistency, not a deviation from the published scale. Impact low (data-consistency/reporting only; category labels stored, no numeric score computed). Verdict DISCREPANCY preserved per extraction.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/choices/avaliacao_global.py` | 92-115 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-wound-BE-06-002`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-002](../clinical-scoring/RULE-FORMULARIOS-CLINICOS-002-pressure-injury-lpp-staging-wound-bed-composite-assessment-n.md)
- [RULE-FORMULARIOS-CLINICOS-003](../clinical-scoring/RULE-FORMULARIOS-CLINICOS-003-nursing-technician-tecenfermagem-tegumentary-lpp-list-varian.md)

## Notes

This enum, together with cor_pele (avaliacao_global.py:67-90) and exsudato (117-125), resembles a wound-assessment scale (Sessing/PUSH-like). Only category labels are stored; no numeric score is computed in this partition. Status upgraded OK->DISCREPANCY during BE/FE reconciliation. verify=true: alert-threshold with a plausible published wound-scale anchor.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
