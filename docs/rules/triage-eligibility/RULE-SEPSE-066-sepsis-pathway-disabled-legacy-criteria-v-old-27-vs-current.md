# RULE-SEPSE-066 — Sepsis pathway - disabled/legacy criteria (v-old 27 vs current 20)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | triage-eligibility |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Documents criteria that exist in code but are disabled, and the prior 27-criterion version, so a rebuild does not reintroduce them silently.

## Inputs

- various (mixed)

## Outputs

- n/a

## Logic

```text
Disabled (commented) calcular_criterio_21..27 covered: SNE with conscious patient (glasgow>=11 & no VM);
invasive vascular devices >10d; femoral central >7d; antibiotic in 24h; recent abdominal surgery;
noradrenaline started <24h (balanço hídrico); urea>50 & creatinina>2. Also a commented leukocyte
criterio_17 (leukocytes <4000 or >15000, or |delta|>5000 across measurements).
```

## Edge cases (as implemented)

None active; save() only computes criterio_1..20.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/trilha_sepse.py` | 13-42,204-210,427-456,491-524 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-10-047`

**Related rules:**

- [RULE-SEPSE-004](../alert-threshold/RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)
- [RULE-SEPSE-038](RULE-SEPSE-038-sepsis-c1-major-fever.md)
- [RULE-SEPSE-039](RULE-SEPSE-039-sepsis-c2-major-spontaneous-respiratory-distress.md)
- [RULE-SEPSE-040](RULE-SEPSE-040-sepsis-c3-major-recent-start-of-mechanical-ventilation.md)
- [RULE-SEPSE-041](RULE-SEPSE-041-sepsis-c4-major-noradrenaline-started-in-last-24h.md)
- [RULE-SEPSE-042](RULE-SEPSE-042-sepsis-c5-major-slow-capillary-refill.md)
- [RULE-SEPSE-043](RULE-SEPSE-043-sepsis-c6-major-hypotension-pas-90-or-pad-90-in-24h.md)
- [RULE-SEPSE-044](RULE-SEPSE-044-sepsis-c7-major-oliguria-or-rising-creatinine.md)
- [RULE-SEPSE-045](RULE-SEPSE-045-sepsis-c8-major-glasgow-drop-or-delirium.md)
- [RULE-SEPSE-046](RULE-SEPSE-046-sepsis-c9-major-hyperbilirubinemia.md)
- [RULE-SEPSE-047](RULE-SEPSE-047-sepsis-c10-minor-hypothermia-in-last-24h.md)
- [RULE-SEPSE-048](RULE-SEPSE-048-sepsis-c11-minor-tachycardia.md)
- [RULE-SEPSE-049](RULE-SEPSE-049-sepsis-c12-minor-hypocapnia-or-poor-oxygenation.md)
- [RULE-SEPSE-050](RULE-SEPSE-050-sepsis-c13-minor-elevated-arterial-lactate.md)
- [RULE-SEPSE-051](RULE-SEPSE-051-sepsis-c14-minor-leukocytosis-in-last-24h.md)
- [RULE-SEPSE-052](RULE-SEPSE-052-sepsis-c15-minor-thrombocytopenia-in-last-24h.md)
- [RULE-SEPSE-053](RULE-SEPSE-053-sepsis-c16-minor-poor-oral-intake-with-preserved-consciousne.md)
- [RULE-SEPSE-054](RULE-SEPSE-054-sepsis-c17-minor-depressed-consciousness-in-last-12h.md)
- [RULE-SEPSE-055](RULE-SEPSE-055-sepsis-c18-minor-central-line-7-days.md)
- [RULE-SEPSE-056](RULE-SEPSE-056-sepsis-c19-minor-femoral-central-line-5-days.md)
- [RULE-SEPSE-057](RULE-SEPSE-057-sepsis-c20-minor-recent-abdominal-surgery.md)

## Notes

_ANTIGAS_REGRAS (27 criteria) is the prior version; _REGRAS (20) is current. Cross-ref sepse C1..C20 rules above. Note descricao_criterio_8 default uses _REGRAS.get("criterio8") (missing underscore) -> stores None instead of the C8 text (data-cosmetic bug, line 114).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
