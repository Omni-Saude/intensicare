# RULE-VENTILACAO-001 — Predicted body weight and protective tidal volume (VC 4/5/6 ml/kg)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | VERIFIED, impact: none |
| Confidence | high |
| Cluster | ventilacao |

## Rule

When the physiotherapist enters height (cm), computes predicted/ideal body weight (ARDSNet/Devine-style: sex-specific base + 0.91 kg per cm above 152.4 cm) and derives three lung-protective tidal-volume targets at 4, 5 and 6 mL/kg of that predicted weight.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| altura (cm) | | | |
| ocupacao.paciente.genero (string enum "F" | other) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| calculo_peso (kg, base constant only) | | |
| peso_ideal (string, 4 decimals, kg) | | |
| vc_ideal_4 / vc_ideal_5 / vc_ideal_6 (string, 4 decimals, mL) | | |

## Logic

```text
on altura(e) change:
  pesoGender = (ocupacao?.paciente?.genero === "F") ? 45.5 : 50   // any non-"F" (incl. undefined) => male base 50
  if (e === null || e === 0):
    pesoIdeal = 0
  else:
    pesoIdeal = pesoGender + 0.91 * (e - 152.4)
  calculo_peso   = pesoGender                    // NOTE: stores the base constant itself, not a computed body weight
  peso_ideal     = pesoIdeal.toFixed(4)
  vc_ideal_4     = (pesoIdeal * 4).toFixed(4)
  vc_ideal_5     = (pesoIdeal * 5).toFixed(4)
  vc_ideal_6     = (pesoIdeal * 6).toFixed(4)
```

## Edge cases (as implemented)

Height null or 0 forces pesoIdeal=0. No plausibility bound on altura otherwise. All outputs are strings with exactly 4 decimals via toFixed(4). Input disabled when mode === "in_page" (read-only), so calculation only runs in "modal" (edit) mode.

## Verification

- Verdict: VERIFIED (clinical impact: none)
- Reference: ARDS Network (ARMA/ARDSNet) low tidal volume protocol - PBW (Devine formula): male = 50 + 0.91*(height_cm - 152.4); female = 45.5 + 0.91*(height_cm - 152.4); lung-protective tidal volume 4-6 mL/kg PBW (ARDSNet ventilator protocol card; ARMA trial NEJM 2000;342:1301-1308).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/FieldSetDadosPacienteFisioterapeuta/FieldSetDadosPacienteFisioterapeuta.tsx` | 20-38 | `f9656be2` | primary |

- Merged from: RULE-ventilacao-FE-05-001
- Related rules: RULE-VENTILACAO-020, RULE-VENTILACAO-017, RULE-VENTILACAO-003

## Notes

Matches standard ARDSNet PBW (male 50 + 0.91*(h-152.4); female 45.5 + 0.91*(h-152.4)) and 4-6 mL/kg lung-protective targets, hence OK. calculo_peso is labeled "Calculo Peso" in the UI but stores the raw sex base constant (45.5/50), not a computed weight - naming/behavior mismatch worth confirming; downstream peso_ideal/vc_ideal_* are computed correctly regardless.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
