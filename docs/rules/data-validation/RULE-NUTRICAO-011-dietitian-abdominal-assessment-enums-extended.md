# RULE-NUTRICAO-011 — Dietitian abdominal assessment enums (extended)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | nutricao |

## Rule
Dietitian abdominal exam adds colostomy, ascites, diuresis-route and stool-aspect fields beyond the nursing version.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_abdominal.* | enum/boolean/string |  | see logic |

## Outputs
| Name | Type | Unit |
|---|---|---|
| abdominal assessment | object |  |

## Logic
```text
geral (multicheck): plano | globoso | escavado | cirurgia_recente | colostomia
ruidos_hidroaereos (multicheck): presentes | diminuidos | ausentes
presenca_dor (multicheck): doloroso | indolor | ascitico
massas_palpaveis (boolean); peristalse (boolean)
evacuacoes (select): ausente | presente; aspecto_fezes (string)
diurese (multicheck): ausente | presente | svd | sva | fralda; aspecto_urina (string)
```

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormNutricionista.ts | 111-190 | f9656be2 | primary |

- Merged from: RULE-nutrition-FE-01-049
- Related rules: none

## Notes
Verified against source lines 111-190. Phase-1 note flags this as extended vs a nursing abdominal version; the nursing counterpart was not present in the nutricao partition (likely captured in another cluster) so no cross-copy comparison was possible here.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
