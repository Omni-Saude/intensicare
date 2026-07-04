# RULE-COMUNICACAO-034 — Validacao de leito para acao de feed homecare

| Field | Value |
|---|---|
| Cluster | comunicacao |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Validates that a feed action is only registered for a homecare-type bed; a second guard intended to block actions on unoccupied beds is present but unreachable.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| self.leito.tipo | enum |  |  |
| self.leito.ocupado | boolean |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| raises ValidationError or passes | control-flow |  |

## Logic

```text
if self.leito.tipo != "homecare":
    raise ValidationError("Apenas leitos de homecare podem ter acoes do feed registradas")
if not self.leito.ocupado:
    if self.leito.tipo != "homecare":          # always False here (tipo already == "homecare")
        raise ValidationError("Leitos ocupados nao podem ter acoes registradas")
```

## Edge cases (as implemented)

The inner condition can never be True because the first check already guaranteed tipo == "homecare"; therefore the "unoccupied bed" validation NEVER fires (dead code).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/models/acao_homecare.py` | 117-128 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-feed-BE-06-001`

**Related rules:**

- [RULE-COMUNICACAO-003](../care-pathway/RULE-COMUNICACAO-003-acaohomecare-balanco-hidrico-method-reference-bug.md)
- [RULE-COMUNICACAO-012](RULE-COMUNICACAO-012-patient-snapshot-in-observation-branches-by-leito-type.md)
- [RULE-COMUNICACAO-035](RULE-COMUNICACAO-035-homecare-feed-action-type-vocabulary-acaodict-render-map-vs.md)

## Notes

DISCREPANCY: the nested `if self.leito.tipo != "homecare"` inside the `if not self.leito.ocupado` block is dead code; the intended rule (block feed actions on unoccupied beds) is not enforced. Also validar_leito() is defined but not called from save() in this file (save only sets paciente and builds mensagem, lines 107-115).
 | RECONCILED: confirmed directly against trilha_homecare/models/acao_homecare.py (docstring: "Modelo do feed do homecare") that (a) validar_leito()'s inner 'unoccupied bed' check is dead code as originally flagged, AND (b) validar_leito() itself is never invoked anywhere in save() (save() only sets self.paciente and builds self.mensagem) — so BOTH the outer 'must be homecare bed' and inner 'must be occupied' guards are entirely unenforced at the model layer, not merely the inner one. Same model/serializer family as RULE-COMUNICACAO-003.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
