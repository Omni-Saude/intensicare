# RULE-BALANCO-HIDRICO-028 — Medical-evolution 24h-indicator gate vs value source mismatch

| Field | Value |
|---|---|
| Category | physiological-calculation |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | balanco-hidrico |

## Rule
On the medical-evolution PDF, each 24h indicator row (diurese, ganhos, balanco, temperatura max, HGT) is CONDITIONED on the truthiness of formulario_data.sinais_vitais.<field> but then DISPLAYS the value from formulario_data.indicadores_24h.<field>. If the sinais_vitais gating value is falsy while indicadores_24h has data (or vice versa), the row is hidden or the wrong source shown.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| formulario_data.sinais_vitais.{diurese_24h,ganhos_24h,balanco_24h,temperatura_max_24h,hgt_24h} | — | — | — |
| formulario_data.indicadores_24h.{same keys} | — | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| rendered indicator rows | — | — |

## Logic
```text
# diurese, ganhos, temperatura_max, hgt rows (evacuacoes uses sinais_vitais for both gate+value):
if formulario_data.sinais_vitais.diurese_24h:          show indicadores_24h.diurese_24h
if formulario_data.sinais_vitais.ganhos_24h:           show indicadores_24h.ganhos_24h
if formulario_data.sinais_vitais.balanco_24h:          show indicadores_24h.balanco_24h
if formulario_data.sinais_vitais.temperatura_max_24h:  show indicadores_24h.temperatura_max_24h
if formulario_data.sinais_vitais.hgt_24h:              show indicadores_24h.hgt_24h
# PA row: show only if BOTH pas and pad present -> "{pas} por {pad}"
```

## Edge cases (as implemented)
Row visibility keyed on sinais_vitais.* but printed value taken from indicadores_24h.*; the two namespaces can disagree. evacuacoes_24h row (l.495-497) both gates and prints from sinais_vitais. PA row requires both systolic (pas) and diastolic (pad) to render.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published source. Pure PDF-template presentation/gating logic for the medical-evolution report; the underlying 24h indicator VALUES trace to utils.py helpers (RULE-...-006..011) which are the clinically-relevant computations, not this row-visibility rule. (n/a)
- Test vectors: 2/4 match
- Extraction status AMBIGUOUS. Characterized: the gate/value namespace mismatch (gate on sinais_vitais.*, value from indicadores_24h.*) is a real template defect that can hide a row when the gating field is falsy while the indicator value exists (test vectors 2 and 3 diverge), or vice-versa. This is display/presentation logic with NO authoritative published clinical reference; the serializer that populates both namespaces is in api/ (out of the cited partition), so intent cannot be confirmed here. Flag for internal review (confirm whether sinais_vitais.* and indicadores_24h.* are guaranteed to co-populate). Not a clinical-formula error; impact on the underlying computed values is n/a (this rule only governs row visibility on a PDF).

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/templates/arquivos/pdf_medico.html | 469-501 | 8166c07e | primary |
- Merged from: RULE-balancohidrico-BE-09-011
- Related rules: RULE-BALANCO-HIDRICO-006, RULE-BALANCO-HIDRICO-012, RULE-BALANCO-HIDRICO-018

## Notes
AMBIGUOUS/likely DISCREPANCY: mismatched gate vs value namespaces (sinais_vitais.* vs indicadores_24h.*). Underlying indicator values come from utils.py RULE-...-002..006. Cannot confirm intent from this partition alone (serializer that builds the context is in api/, out of scope).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
