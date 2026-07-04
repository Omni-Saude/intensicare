# RULE-SEPSE-003 — Sepse - Classificacao de alerta (maiores/menores)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | alert-threshold |
| Type | decision-tree |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | low |

## Rule
Aggregates the 11 boolean criteria into a color alert. Criteria 1-7 are "maiores" (major) and 8-11 are "menores" (minor). VERMELHO (high risk) if >2 majors or exactly 4 minors; AMARELO (risk) if exactly 2 majors or exactly 3 minors; otherwise NEUTRO.

## Inputs

- criterio_1..criterio_7 (maiores) (array[boolean])
- criterio_8..criterio_11 (menores) (array[boolean])

## Outputs

- alerta (enum)
- mensagem (string)

## Logic

```text
maiores = [c1,c2,c3,c4,c5,c6,c7].count(True)
menores = [c8,c9,c10,c11].count(True)
if maiores > 2 or menores == 4:
    alerta = "VERMELHO"
elif maiores == 2 or menores == 3:
    alerta = "AMARELO"
else:
    alerta = "NEUTRO"
mensagem = ""
if alerta != "NEUTRO":
    mensagem = "Risco para SEPSE." if alerta == "AMARELO" else "Alto risco para SEPSE."
```

## Edge cases (as implemented)

count(True) counts only Python True; None (e.g. criterio_10 unset) is not counted. Boundaries: maiores==2 -> AMARELO, maiores==3 -> VERMELHO. Default field value alerta="NEUTRO". This alerta is recomputed and persisted on every save().

## Divergence

'menores == 4' branch is unreachable because criterio_11 (RULE-SEPSE-037) is hard-coded False, so the minor group maxes at 3; VERMELHO is reachable only via maiores>2. Note this homecare classifier uses strict maiores>2 / ==2 and menores==4 / ==3 bands, unlike v1 (RULE-SEPSE-001) and manual (RULE-SEPSE-004) which use >= comparisons.

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** low
- **Reference:** No external reference for the aggregation; the flagged discrepancy is an INTERNAL dead-branch logic bug, verifiable by code inspection. External screening context: ILAS screening protocol 2018; Singer M et al. Sepsis-3, JAMA 2016;315(8):801-810. ([source](https://ilas.org.br/wp-content/uploads/2022/02/protocolo-de-tratamento.pdf))

**Checks**

| Dimension | Result |
|---|---|
| equation | n/a |
| coefficients | n/a |
| units | n/a |
| ranges | diff: minor group declared as 4 fields (criterio_8..11) but criterio_11 is hard-coded False (RULE-SEPSE-037), so menores effectively ranges 0-3, never 4. |
| rounding | n/a |
| cutoffs | diff-INTERNAL: uses strict maiores>2 / ==2 and menores==4 / ==3 bands (equality, not >=) unlike the >= bands in RULE-SEPSE-001/004. The 'menores==4' -> VERMELHO branch is UNREACHABLE because the minor pool maxes at 3. Confirmed by hand-trace of trilha_homecare/models/sepse.py:350-383. |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| maiores=3; menores=0 | high-risk (>2 majors) | VERMELHO (via maiores>2) | yes |
| maiores=2; menores=0 | risk (==2 majors) | AMARELO | yes |
| maiores=0; menores=4 | menores==4 branch intends VERMELHO | unreachable - criterio_11 hard-coded False caps minors at 3, so max menores==3 -> AMARELO; minor-driven VERMELHO never fires | no |
| maiores=0; menores=3 | risk | AMARELO | yes |

**Verifier notes**

CONFIRMED (internal dead-branch bug, extraction flag upheld). VERMELHO is reachable ONLY via maiores>2; the minor-only high-risk path is dead code because criterio_11 is hard-coded False. Impact low: no achievable patient state is misclassified relative to the reachable logic (a genuine 4-of-4 minor state is impossible to represent), so the bug is latent rather than actively harming triage - but it signals an incomplete criterio_11 and an intent (minor-driven VERMELHO) that never executes. A superseded soma-based classifier (0-7/8-14/15-21 bands) exists commented-out at lines 394-419 and is NOT active. alerta is recomputed and persisted on every save().

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/sepse.py` | 350-383 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-06-013`

**Related rules:**

- [RULE-SEPSE-001](../clinical-scoring/RULE-SEPSE-001-sepse-v1-alert-maiores-menores-dual-threshold.md)
- [RULE-SEPSE-002](../clinical-scoring/RULE-SEPSE-002-sepse-v3-alert-maiores-menores-or-thresholds-risk-message.md)
- [RULE-SEPSE-004](RULE-SEPSE-004-sepsis-pathway-alert-major-minor-two-axis-threshold.md)
- [RULE-SEPSE-027](../clinical-scoring/RULE-SEPSE-027-sepse-criterio-1-febre-fever.md)
- [RULE-SEPSE-028](../clinical-scoring/RULE-SEPSE-028-sepse-criterio-2-taquipneia-dessaturacao-sob-o2.md)
- [RULE-SEPSE-029](../clinical-scoring/RULE-SEPSE-029-sepse-criterio-3-escalonamento-de-suporte-ventilatorio.md)
- [RULE-SEPSE-030](../clinical-scoring/RULE-SEPSE-030-sepse-criterio-4-tempo-de-enchimento-capilar-5s.md)
- [RULE-SEPSE-031](../clinical-scoring/RULE-SEPSE-031-sepse-criterio-5-hipotensao.md)
- [RULE-SEPSE-032](../clinical-scoring/RULE-SEPSE-032-sepse-criterio-6-oliguria-sonda-ou-dessaturacao.md)
- [RULE-SEPSE-033](../clinical-scoring/RULE-SEPSE-033-sepse-criterio-7-variacao-do-nivel-de-consciencia.md)
- [RULE-SEPSE-034](../clinical-scoring/RULE-SEPSE-034-sepse-criterio-8-hipotermia.md)
- [RULE-SEPSE-035](../clinical-scoring/RULE-SEPSE-035-sepse-criterio-9-taquicardia.md)
- [RULE-SEPSE-036](../clinical-scoring/RULE-SEPSE-036-sepse-criterio-10-dispositivo-invasivo-com-permanencia-7-dia.md)
- [RULE-SEPSE-037](../clinical-scoring/RULE-SEPSE-037-sepse-criterio-11-placeholder-sempre-false.md)

## Notes

DISCREPANCY: `menores == 4` is unreachable because criterio_11 is always False (see RULE-sepse-BE-06-011), so the minors group maxes at 3. Thus VERMELHO can only be reached via `maiores > 2`. A superseded soma-based classifier (0-7/8-14/15-21 bands) is present commented-out at lines 394-419 and is NOT active. save() (lines 89-103) recomputes all criteria then alerta inside a transaction.atomic.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
