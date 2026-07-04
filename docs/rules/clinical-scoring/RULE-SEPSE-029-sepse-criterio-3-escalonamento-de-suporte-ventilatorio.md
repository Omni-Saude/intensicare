# RULE-SEPSE-029 — Sepse criterio_3 - Escalonamento de suporte ventilatorio

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | UNVERIFIABLE |
| Clinical impact | n/a |

## Rule
Major criterion 3 fires if current ventilation is mechanical while the previous vital-sign reading was room air, OR current ventilation is O2 support (within a 24h window guard).

## Inputs

- sinais_vitais.ventilacao (enum, ambiente|suporte_o2|mecanica)
- sinais_vitais.anterior(nr_atendimento).ventilacao (enum, ambiente|suporte_o2|mecanica)
- sinais_vitais.tempo_criacao() (float, hours)

## Outputs

- criterio_3 (boolean)

## Logic

```text
anterior = sinais_vitais.anterior(nr_atendimento) if sinais_vitais else None
branch_A = (ventilacao == "mecanica") AND (anterior.ventilacao == "ambiente" if anterior else False)
branch_B = (ventilacao == "suporte_o2") if sinais_vitais.tempo_criacao() <= 24 else False
return any([branch_A, branch_B]) if sinais_vitais else False
```

## Edge cases (as implemented)

anterior is the SECOND most recent reading (index [1]) per RULE-balanco-BE-06-007; if fewer than 2 readings exist, anterior is None. tempo_criacao <= 24 always true (see RULE-balanco-BE-06-006) so branch_B reduces to ventilacao == "suporte_o2".

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published sepsis scale defines a discrete 'ventilatory-support escalation' criterion with these exact transitions (mechanical-after-room-air OR current O2-support). Related concept only: new/increased supplemental-oxygen requirement scores in NEWS2 (Royal College of Physicians, 2017). The specific escalation logic is institutional. ([source](https://www.rcp.ac.uk/improving-care/resources/national-early-warning-score-news-2/))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | n/a |
| rounding | n/a |
| cutoffs | n/a |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| ventilacao=mecanica; anterior_ventilacao=ambiente | no published truth value | True (branch_A: mecanica AND prior ambiente) | n/a |
| ventilacao=suporte_o2; tempo_criacao_h=2 | n/a | True (branch_B: suporte_o2, window always <=24) | n/a |
| ventilacao=ambiente; anterior_ventilacao=ambiente | n/a | False (neither branch) | n/a |
| ventilacao=mecanica; anterior= | n/a | False (anterior None -> branch_A False; not suporte_o2) | n/a |

**Verifier notes**

Institutional respiratory-escalation major criterion; no primary published reference to grade its thresholds/transitions. Flag for internal review. Internal-implementation notes (not reference discrepancies): 'anterior' is the 2nd-most-recent reading (index [1]); tempo_criacao()<=24 guard is effectively always-true (timedelta.seconds bug), reducing branch_B to ventilacao=='suporte_o2'.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 144-166 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-003`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

Major criterion.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
