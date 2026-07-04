# RULE-SEPSE-032 — Sepse criterio_6 - Oliguria (sonda) ou dessaturacao

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | clinical-scoring |
| Type | threshold |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | moderate |

## Rule
Major criterion 6 fires if the last fluid-output was catheter diuresis (diurese_sonda) with volume <= 100 recorded within the last 2 hours, OR patient on O2 support with SpO2 < 96%.

## Inputs

- balanco.ultima_saida().tipo (enum)
- balanco.ultima_saida().quantidade (float, mL)
- balanco.ultima_saida().criado_em (datetime)
- sinais_vitais.ventilacao (enum)
- sinais_vitais.saturacao_o2 (float, percent)

## Outputs

- criterio_6 (boolean)

## Logic

```text
branch_A = all([
    ultima_saida.tipo == "diurese_sonda",
    ultima_saida.quantidade <= 100,
    (timezone.now() - ultima_saida.criado_em).seconds / 3600 < 2,
]) if (sinais_vitais and balanco.saidas.exists()) else False
branch_B = (ventilacao == "suporte_o2" if ventilacao else False) AND (saturacao_o2 < 96 if saturacao_o2 else False)
return any([branch_A, branch_B])
```

## Edge cases (as implemented)

quantidade <= 100 uses the raw units stored (mL assumed). The 2-hour recency check uses timedelta.seconds/3600 (only the intra-day seconds component, 0-86399) so an output older than 24h wraps and may spuriously satisfy "< 2". quantidade could be null (default 0) -> 0 <= 100 True.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** moderate
- **Reference:** KDIGO AKI 2012 & SSC severe-sepsis organ-dysfunction criteria - oliguria = urine output < 0.5 mL/kg/h for >=2 consecutive hours (weight- and time-normalized). NEWS2 SpO2 target range 94-98%. ([source](https://pmc.ncbi.nlm.nih.gov/articles/PMC8486643/))

**Checks**

| Dimension | Result |
|---|---|
| equation | diff |
| coefficients | diff |
| units | diff |
| ranges | n/a |
| rounding | n/a |
| cutoffs | diff |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| peso_kg=70; ultima_saida_tipo=diurese_sonda; quantidade_mL=90; idade_saida_h=1; ventilacao= | 90 mL over 2h at 70 kg = 0.64 mL/kg/h, NOT oliguric = False | 90<=100 True and recency<2 True -> branch_A True -> True | no |
| peso_kg=100; ultima_saida_tipo=diurese_sonda; quantidade_mL=100; idade_saida_h=1; ventilacao= | 0.5 mL/kg/h*2h = 100 mL, strict < not met -> NOT oliguric = False | 100<=100 True -> branch_A True -> True | no |
| peso_kg=70; ultima_saida_tipo=diurese_sonda; quantidade_mL=150; idade_saida_h=1; ventilacao= | 150 mL/2h at 70 kg = 1.07 mL/kg/h, NOT oliguric = False | 150<=100 False -> branch_A False, no O2 -> False | yes |
| ventilacao=suporte_o2; saturacao_o2=93 | desaturation on O2 (SpO2<94 NEWS2) -> supportive of hypoperfusion | branch_B suporte_o2 & 93<96 True -> True | yes |

**Verifier notes**

Oliguria branch_A diverges from the KDIGO/SSC definition on THREE audited dimensions: (a) uses a fixed absolute volume (<=100 mL) instead of a weight-normalized rate (0.5 mL/kg/h); (b) evaluates only the single last catheter void, not summed output over 2 consecutive hours; (c) recency test uses timedelta.seconds/3600 (0-86399 s, intra-day only) so a void older than 24h wraps and can spuriously satisfy '<2h' (same .seconds bug family as RULE-balanco-BE-06-006). Net effect: firing depends on the raw last-void volume rather than true UO rate -> both false positives (low single void in a non-oliguric patient; null quantidade default 0<=100) and false negatives. Moderate impact: it is a MAJOR screening criterion and the mismatch is systematic. The SpO2<96%-on-O2 desaturation branch_B is a reasonable NEWS2-consistent supportive threshold and is not the source of the discrepancy.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 196-227 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-006`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

Branch_B duplicates criterio_2 branch_B. Recency uses .seconds (same bug family as RULE-balanco-BE-06-006).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
