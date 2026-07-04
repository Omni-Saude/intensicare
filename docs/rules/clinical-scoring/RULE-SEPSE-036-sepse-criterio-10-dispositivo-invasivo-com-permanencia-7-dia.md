# RULE-SEPSE-036 — Sepse criterio_10 - Dispositivo invasivo com permanencia > 7 dias

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
Minor criterion 10 fires when a peripheral venous access in use has been inserted > 7 days ago, OR a double-lumen dialysis catheter in use has been inserted > 7 days ago; uses the latest nursing evolution's invasive-devices data.

## Inputs

- dispositivos_invasivos.acesso_venoso_periferico {em_uso, data_insercao} (json)
- dispositivos_invasivos.cateter_duplo_lumen_hemodialise {em_uso, data_insercao} (json)

## Outputs

- criterio_10 (boolean or None)

## Logic

```text
formulario = get_evolucao_enfermagem()   # latest Formulario tipo="enfermagem" for nr_atendimento
if formulario and formulario.dispositivos_invasivos:
    avp_em_uso = acesso_venoso_periferico.get("em_uso") if acesso_venoso_periferico else False
    avp_data   = acesso_venoso_periferico.get("data_insercao") if acesso_venoso_periferico else False
    dl_em_uso  = cateter_duplo_lumen_hemodialise.get("em_uso", None) if cateter_duplo_lumen_hemodialise else False
    dl_data    = cateter_duplo_lumen_hemodialise.get("data_insercao") if cateter_duplo_lumen_hemodialise else False
    return any([
        all([avp_em_uso, (diferenca_dias(strptime(avp_data,"%Y-%m-%d").date()) > 7) if avp_data else False]),
        all([dl_em_uso,  (diferenca_dias(strptime(dl_data,"%Y-%m-%d").date())  > 7) if dl_data  else False]),
    ])
# implicit: returns None when no formulario or no dispositivos_invasivos
```

## Edge cases (as implemented)

Strict > 7 days. Returns None (falsy, counted as not-True) when there is no nursing evolution or no invasive-devices record. data_insercao parsed with strptime "%Y-%m-%d"; malformed/absent date -> ValueError or False sub-branch. diferenca_dias() lives in utils.handlers (OUTSIDE this partition) and defines the exact day-difference semantics.

## Verification

- **Verdict:** UNVERIFIABLE
- **Clinical impact:** n/a
- **Reference:** No authoritative published equation defines a fixed catheter/venous-access dwell-time threshold as a scored sepsis-screening criterion. Prolonged invasive-device dwell is a recognized CRBSI/HAI risk factor (CDC/HICPAC Guidelines for the Prevention of Intravascular Catheter-Related Infections, 2011; INICC), but the >7-day cutoff and its use as a minor sepsis criterion are institutional. Internal business rule. ([source](https://www.cdc.gov/infection-control/hcp/intravascular-catheter-related-infection/index.html))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | 7-day threshold is institutional, not from a published sepsis criterion |
| units | days; diferenca_dias(entrada)=timezone.now().date()-entrada -> .days (whole calendar days). data_insercao parsed strptime '%Y-%m-%d' (date only) |
| ranges | n/a |
| rounding | date-only subtraction truncates time-of-day; '>7' therefore requires >=8 whole calendar days between insertion date and today |
| cutoffs | strict > 7 (i.e. >=8 calendar days) |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| avp_em_uso=true; avp_data_insercao=8 calendar days ago; dl= | n/a (no published cutoff) | diferenca_dias=8 > 7 -> True | yes |
| avp_em_uso=true; avp_data_insercao=7 calendar days ago; dl= | n/a | diferenca_dias=7 > 7 -> False (boundary excluded) | yes |
| avp_em_uso=false; avp_data_insercao=20 days ago; dl_em_uso=false | n/a | any([all([False,...]), all([False,...])]) -> False (device not in use) | yes |
| formulario= | n/a | no evolucao_enfermagem/dispositivos -> implicit return None (falsy, counted not-True) | yes |

**Verifier notes**

Internal infection-risk business rule; no authoritative sepsis-criterion source for the 7-day dwell threshold. Logic hand-traces correctly and consistently. diferenca_dias (utils/handlers.py:63-65) confirmed to use date-only subtraction, so '>7 days' effectively means the insertion calendar date is >=8 days before today. Flag for internal clinical review, not a defect.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 270-330 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-010`

**Related rules:**

- [RULE-SEPSE-003](../alert-threshold/RULE-SEPSE-003-sepse-classificacao-de-alerta-maiores-menores.md)

## Notes

get_evolucao_enfermagem() (lines 385-392) selects latest Formulario tipo="enfermagem" by leito__nr_atendimento, order_by -criado_em. Verifier must inspect utils.handlers.diferenca_dias (out of partition) for exact >7-day arithmetic. Minor criterion.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
