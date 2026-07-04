# RULE-PIORA-CLINICA-010 — Piora Clinica - Calculo do alerta (soma agregada + gatilho por criterio)

| Field | Value |
|---|---|
| Category | alert-threshold |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: high |
| Confidence | high |
| Cluster | piora-clinica |

## Rule
Aggregates the 9 graded sub-scores (criterio_1..9) into a color alert. This is a MEWS/NEWS-style track-and-trigger: any single criterion at grade 2 (+/-) sets AMARELO and any at grade 3 (+/-) sets VERMELHO (message names the criterion); only if NO criterion reached grade 2/3 does a total-sum banding apply (0-7 NEUTRO, 8-14 AMARELO, 15-21 VERMELHO).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| criterio_1..criterio_9 | array[enum grade strings] | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta | enum | — |
| mensagem | string | — |

## Logic
```text
soma = 0
payload = {}
for c in range(1, 10):
    criterio = getattr(self, f"criterio_{c}")   # e.g. "0","1+","2-","3+"
    soma += int(criterio[0])                     # magnitude only; sign discarded ("3-" and "3+" both add 3)
    if criterio in ["2-", "2+"]:
        payload["mensagem"] = f"Moderado risco de piora clinica – {nome_criterio(f'criterio_{c}')}"
        payload["alerta"]  = "AMARELO"
    elif criterio in ["3-", "3+"]:
        payload["mensagem"] = f"Alto risco de piora clinica – {nome_criterio(f'criterio_{c}')}"
        payload["alerta"]  = "VERMELHO"
if not payload:
    if   0  <= soma <=  7: alerta="NEUTRO",   mensagem="Baixo risco de piora clinica"
    elif 8  <= soma <= 14: alerta="AMARELO",  mensagem="Moderado risco de piora clinica"
    elif 15 <= soma <= 21: alerta="VERMELHO", mensagem="Alto risco de piora clinica"
```

## Edge cases (as implemented)
int(criterio[0]) reads only the first char, so grade SIGN is discarded when summing. The per-criterion payload is OVERWRITTEN each loop iteration, so the LAST (highest-index) criterion at grade 2 or 3 determines the final alerta/mensagem - a later grade-2 criterion can DOWNGRADE an earlier grade-3 one (VERMELHO -> AMARELO). The soma-banding branch runs only when NO criterion reached grade 2/3 (all sub-scores in {0,1+,1-}); then soma <= 9, so the 15-21 band is dead and only soma 8-9 can reach AMARELO. criterio must be non-null (guaranteed after save()); calling on an unsaved instance with None criterio raises on criterio[0].

## Verification
- Verdict: DISCREPANCY (impact: high)
- Reference: NEWS2 / MEWS track-and-trigger escalation logic (Royal College of Physicians NEWS2, 2017; NICE MIB205). Two-tier trigger: (a) ANY single parameter scoring 3 ("red score") mandates urgent escalation regardless of aggregate; (b) aggregate bands drive graded response (NEWS2: 0-4 low, 5-6 medium, >=7 high). A high-severity single parameter must never be downgraded by other parameters, and every abnormal parameter contributes to the aggregate.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/models/piora_clinica.py | 236-262 | 8166c07e | primary |
- Merged from: RULE-piora-BE-06-010
- Related rules: RULE-PIORA-CLINICA-001, RULE-PIORA-CLINICA-002, RULE-PIORA-CLINICA-003, RULE-PIORA-CLINICA-004, RULE-PIORA-CLINICA-005, RULE-PIORA-CLINICA-006, RULE-PIORA-CLINICA-007, RULE-PIORA-CLINICA-008, RULE-PIORA-CLINICA-009, RULE-PIORA-CLINICA-011

## Notes
DISCREPANCY (three internal defects, preserved verbatim): (1) last-writer-wins overwrite lets a lower-severity later criterion mask a higher-severity earlier one; (2) soma ignores +/- direction (magnitude only); (3) the 15-21 (and most of 8-14) sum band is unreachable because it only runs when every criterion is grade <=1. nome_criterio() map at lines 221-234. save() (lines 70-81) recomputes criterio_1..9 then sets alerta. get_detalhe() only surfaces criterio_1..3 (range(1,4)) via payload_piora_clinica_homecare (facade RULE-PIORA-CLINICA-011). verify=true: aggregate track-and-trigger banding has a plausible published anchor (MEWS/NEWS-style early-warning score).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
