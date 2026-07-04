# RULE-TRILHAS-ENGINE-017 — Per-criterion drug-dosing reference image

| Field | Value |
|---|---|
| Category | drug-dosing |
| Type | workflow |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | trilhas-engine |

## Rule
When a pathway criterion carries a dosage image (criterio.imagem), an "Acessar dosagens" button is shown that opens a modal titled "Dosagens" displaying the dosing reference image.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| criterio.imagem | string (image URL) |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| dosages modal | UI modal |  |

## Logic
```text
if (criterio.imagem):
  render button "Acessar dosagens" (pill icon)
  onClick -> Modal.info({ title: "Dosagens", content: <img src=criterio.imagem/> })
```

## Edge cases (as implemented)
Only shown when criterio.imagem is truthy. The drug dose values themselves live inside the image asset (not machine-readable in this partition).

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference is verifiable for this rule. The rule is categorized drug-dosing (verify:true) but encodes only a UI surfacing mechanism: the actual dose values are embedded in an opaque image asset (criterio.imagem), not in machine-readable code. No equation, coefficient, unit, valid-range, rounding, or cutoff is present in the partition to check against a clinical guideline or standard calculator.
- Test vectors:
  1. inputs: {"criterio.imagem": "https://cdn/dose_noradrenalina.png"} — expected: Button 'Acessar dosagens' rendered; onClick opens Modal.info title 'Dosagens' with <img src=that URL>; actual (legacy): criterio.imagem truthy -> Button + Modal.info({title:'Dosagens', content:<img src=criterio.imagem>}) rendered (TabRecomendacoes.tsx L257-277); match: True
  2. inputs: {"criterio.imagem": null} — expected: No dosing button shown; actual (legacy): criterio.imagem falsy -> {criterio.imagem && (...)} short-circuits, no button rendered; match: True
  3. inputs: {"criterio.imagem": ""} — expected: Empty string is falsy -> no dosing button; actual (legacy): '' is falsy in JS -> no button rendered; match: True
- Legacy code confirmed at trilhas-frontend @ f9656be, src/components/TabRecomendacoes/TabRecomendacoes.tsx lines 257-277: `{criterio.imagem && (<Button icon=mdiPill shape=round onClick=Modal.info({title:"Dosagens", content:<img src=criterio.imagem!/>})>Acessar dosagens</Button>)}`. The rule matches the source verbatim. However the audit's target — the numeric drug doses (mcg/kg/min vs mcg/kg/h, mg/dl vs mmol/L, FiO2 fraction vs percent, etc.) — is NOT in the code: it is rendered from a pre-authored image (criterio.imagem) served by the backend/CMS and is opaque to static analysis. Therefore no dosing value can be traced against a published reference from this partition. Flagged for internal review: the actual dosing image assets (their source, clinical provenance, and last-reviewed date) should be audited separately by a human clinician against the relevant guidelines. This is NOT a defect in the rule as written; the surfacing mechanism is correct and the verdict reflects the absence of a machine-checkable numeric payload, not a discrepancy.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/TabRecomendacoes/TabRecomendacoes.tsx` | 257-277 | `f9656be2` | primary |

- Merged from: `RULE-trilha-FE-03-009`
- Related rules: RULE-TRILHAS-ENGINE-016

## Notes
verify:true by category (drug-dosing). The actual drug dosing content is an image (criterio.imagem), so the numeric dosing rules are not extractable from code; captured here as the mechanism by which dosing guidance is surfaced per criterion. Verifier can only confirm the surfacing mechanism, not the numeric doses inside the image asset.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
