# RULE-SEPSE-071 — SEPSE v3 interactive-protocol creation gate (can_criar_novo_protocolo)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | eligibility |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A new interactive sepsis protocol may be created only when no open interactive trilha exists, the last concluded one is >3 days old (or none), the alert is not NEUTRO, and not already assisted.

## Inputs

- trilha_interativa_pk (open protocol), ultima_concluida.concluido_em, self.alerta, self.assistido (object / datetime / string / bool)

## Outputs

- can_criar_novo_protocolo (boolean)

## Logic

```text
ultima_concluida = trilhas_interativas_sepse.filter(concluida=True).last()
return True if (
  not trilha_interativa_pk
  and (ultima_concluida.concluido_em < now - 3 days if ultima_concluida else True)
  and self.alerta != "NEUTRO"
  and not self.assistido
) else False
```

## Edge cases (as implemented)

3-day cooldown between concluded protocols; open protocol = trilhas_interativas_sepse.filter(finalizado=False).first().

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 323-338 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-03-121`

**Related rules:**

- [RULE-SEPSE-072](RULE-SEPSE-072-sepse-protocol-acceptance-workflow-and-orange-alert.md)
- [RULE-SEPSE-097](RULE-SEPSE-097-sepsis-protocol-refusal-permission.md)
- [RULE-SEPSE-083](RULE-SEPSE-083-interactive-sepsis-trail-filtered-by-bed.md)

## Notes

Depends on serializer import (api.v1.serializers) - cross-module.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
