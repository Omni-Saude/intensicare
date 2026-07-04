# RULE-ALERTAS-008 — Homecare-bed alert ignoring attendance (PioraClinica + Sepse)

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | alert-threshold |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Highest-severity alert among a homecare bed's PioraClinica and Sepse pathways, disregarding attendance.

## Inputs

- PioraClinica.alerta (VERMELHO|AMARELO|NEUTRO)
- Sepse.alerta (VERMELHO|AMARELO|NEUTRO)

## Outputs

- alerta_nao_assistido (string)

## Logic

```text
piora = latest PioraClinica by (sinais_vitais.balanco.leito==self, nr_atendimento) or NEUTRO stub.
sepse = latest Sepse by nr_atendimento or NEUTRO stub.
alertas = [d.alerta for d in (piora_dict, sepse_dict) if d.alerta in ("VERMELHO","AMARELO")]
if alertas: VERMELHO if "VERMELHO" in alertas elif "AMARELO" else NEUTRO
else: "" (empty)
```

## Edge cases (as implemented)

Missing records default to a NEUTRO stub dict. Stored to Leito.alerta_nao_assistido when tipo=="homecare" and ocupado.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/leito.py` | 653-707 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-alerta-BE-04-015`

**Related rules:**

- [RULE-ALERTAS-007](RULE-ALERTAS-007-automatic-bed-alert-ignoring-attendance-alerta-nao-assistido.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
