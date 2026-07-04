# RULE-CLINICAL-SCORING-017 — SDRA (ARDS) severity enumeration

| Field | Value |
|---|---|
| Cluster | clinical-scoring |
| Category | clinical-scoring |
| Type | validation |
| Status | AMBIGUOUS |
| Confidence | medium |
| Verification verdict | VERIFIED |
| Clinical impact | none |

## Rule
ARDS severity levels defined but the sdra field is commented out of DadosProntuario.

## Inputs

| name | type | range |
|---|---|---|
| sdra | str enum | leve, moderada, grave, '' (Nao informado) |

## Outputs

| name | type |
|---|---|
| severity | str |

## Logic

```text
SDRAChoices.tipo(): leve(Leve), moderada(Moderada), grave(Grave), '' (Nao informado)
```

## Edge cases (as implemented)

DadosProntuario.sdra field is commented out (dados_prontuario.py:57-60); a test references dados_prontuario.sdra which would fail against the current model.

## Verification

- **Verdict:** VERIFIED
- **Clinical impact:** none
- **Reference:** ARDS Definition Task Force (Ranieri VM, Rubenfeld GD, Thompson BT, et al.). Acute respiratory distress syndrome: the Berlin Definition. JAMA. 2012;307(23):2526-2533. Three mutually exclusive severity classes: mild (200 < PaO2/FiO2 <= 300), moderate (100 < PaO2/FiO2 <= 200), severe (PaO2/FiO2 <= 100), all at PEEP >= 5 cmH2O. ([source](https://pubmed.ncbi.nlm.nih.gov/22797452/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | ok |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| sdra=leve | mild ARDS (200 < P/F <= 300) | label 'Leve' | yes |
| sdra=moderada | moderate ARDS (100 < P/F <= 200) | label 'Moderada' | yes |
| sdra=grave | severe ARDS (P/F <= 100) | label 'Grave' | yes |
| sdra= | no Berlin equivalent (missing-data sentinel) | label 'Nao informado' | yes |

**Verifier notes**

The three-class severity taxonomy (leve/moderada/grave = mild/moderate/severe) matches the Berlin Definition exactly; the '' "Nao informado" is a benign missing-data sentinel with no reference counterpart. Extraction status was AMBIGUOUS because the DadosProntuario.sdra field is COMMENTED OUT (dados_prontuario.py:57-60) while SDRAChoices remains imported and legacy tests/facade payloads still reference 'sdra' - this is dead code / code-hygiene debt, NOT a discrepancy against the reference. The enum carries no PaO2/FiO2 cutoffs, so there is no numeric threshold to mismatch; nothing to verify beyond the label taxonomy, which is correct. Flag the dead field for internal cleanup (a test referencing dados_prontuario.sdra would fail against the current model).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/choices/indicadores.py` | 36-44 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-choice-BE-10-072`

**Related rules:** _none_

## Notes

AMBIGUOUS/dead: SDRAChoices imported but the model field is disabled (verified dados_prontuario.py:57-60 commented). test_dados_prontuario.py:30 and test_facade payloads still reference 'sdra' (legacy). _ANTIGAS sedation criteria referenced "SDRA moderada ou grave" - dropped in current version.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
