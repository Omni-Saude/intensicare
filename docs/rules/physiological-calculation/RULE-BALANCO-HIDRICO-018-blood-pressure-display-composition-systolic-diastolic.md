# RULE-BALANCO-HIDRICO-018 — Blood-pressure display composition (systolic/diastolic)

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | formula |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | balanco-hidrico |

## Rule
Composes the arterial blood pressure string from systolic (pas) and diastolic (pad) fields. Each component is shown only when strictly greater than 0; otherwise it is replaced by the placeholder "--". The composed value is rendered as "systolic/diastolic". The whole Pressao Arterial row is displayed only if at least one of pad or pas is truthy.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| item.pas | — | mmHg | — |
| item.pad | — | mmHg | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| valuePressaoArterial | — | mmHg |

## Logic
```text
sistole  = (pas != null && pas > 0) ? pas : "--"
diastole = (pad != null && pad > 0) ? pad : "--"
valuePressaoArterial = sistole + "/" + diastole
// Row "Pressao Arterial (mmHg)" rendered only if (pad || pas) is truthy
// AND the composed value is truthy (which it always is, being a string).
```

## Edge cases (as implemented)
pas/pad of 0 or negative render as "--" (0 treated as missing). A value of exactly 0 is NOT displayed. Because pas/pad==0 makes (pad || pas) falsy, if BOTH are 0/absent the entire BP row is hidden; if one is >0 the row shows e.g. "120/--".

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. UI display/formatting rule composing a 'systolic/diastolic' string; each side shown only when strictly > 0 else '--'. No hypertension/hypotension thresholds applied. (n/a)
- Test vectors: 3/3 match
- Pure display formatting (pas=systolic, pad=diastolic); no clinical scale, calculation, or threshold to verify
against a published source. No unit conversion (mmHg passthrough). Cross-surface contrast with the PDF path
(RULE-...-028, which requires BOTH pas AND pad) is preserved-as-implemented, not a reference discrepancy.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/components/BalancoHidricoItens/ItemSinaisVitais/ItemSinaisVitais.tsx | 29-48 | f9656be2 | primary |
- Merged from: RULE-balanco-FE-03-001
- Related rules: RULE-BALANCO-HIDRICO-028, RULE-BALANCO-HIDRICO-052

## Notes
pas = pressao arterial sistolica (systolic), pad = pressao arterial diastolica (diastolic). No hypertension/hypotension thresholds are applied here; this is purely a display/formatting rule.

Cross-surface contrast (NOT auto-flagged as divergence - different documents): this interactive balanco card renders the Pressao Arterial row when EITHER pas or pad is truthy and shows '--' for the missing side; the backend medical-evolution PDF (RULE-BALANCO-HIDRICO-028, pdf_medico.html) renders its PA row only when BOTH pas AND pad are present. Preserved as-implemented on both sides.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
