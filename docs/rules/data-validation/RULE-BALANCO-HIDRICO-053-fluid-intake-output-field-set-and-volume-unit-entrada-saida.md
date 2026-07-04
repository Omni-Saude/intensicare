# RULE-BALANCO-HIDRICO-053 — Fluid intake/output field set and volume unit (entrada/saida)

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Defines the field set for fluid intake (entrada) and output (saida) records and fixes the volume unit as milliliters (ml). Entrada records carry tipo, aceitacao, quantidade(ml), observacao. Saida records carry tipo, aspecto, presenca, presenca_espontanea, quantidade(ml), observacao. Each row renders only when its value is truthy.

## Inputs

- entrada.tipo
- entrada.aceitacao_humanizado
- entrada.quantidade (ml)
- saida.tipo
- saida.aspecto_humanizado
- saida.presenca_humanizado
- saida.presenca_espontanea_humanizado
- saida.quantidade (ml)

## Outputs

- rendered intake/output rows

## Logic

```text
Entrada rows (rendered if value truthy):
  "Tipo de entrada"  <- tipo
  "Status"           <- aceitacao_humanizado
  "Quantidade (ml)"  <- quantidade
  "Observacao"       <- observacao
Saida rows (rendered if value truthy):
  "Tipo de saida"                 <- tipo
  "Aspecto"                       <- aspecto_humanizado
  "Presenca"                      <- presenca_humanizado
  "Houve presenca espontanea?"    <- presenca_espontanea_humanizado
  "Quantidade (ml)"               <- quantidade
  "Observacao"                    <- observacao
Table columns (ColumnsEntrada/ColumnsSaida) mirror these with header
"Quantidade (ml)" and additionally Horario, Preenchido por, Data assinatura.
```

## Edge cases (as implemented)

quantidade rendered via ?.toString(); a quantidade of 0 stringifies to "0" (truthy string) so it WOULD render in the card, but in the overview grid a 0 is suppressed (see RULE-balanco-FE-03-004). observacao longer than 50 chars is truncated with resizeString(...,50) and shown under a click-triggered tooltip.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/components/BalancoHidricoItens/ItemEntrada/ItemEntrada.tsx` | 20-48 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-03-003`

**Related rules:**

- [RULE-BALANCO-HIDRICO-052](RULE-BALANCO-HIDRICO-052-vital-signs-field-set-and-units-sinais-vitais.md)
- [RULE-BALANCO-HIDRICO-041](../care-pathway/RULE-BALANCO-HIDRICO-041-fluid-balance-balanco-hidrico-row-type-label-resolution-and.md)

## Notes

Also defined in ItemSaida/ItemSaida.tsx lines 20-56 and in ColumnsBalancoHidrico/ColumnsEntrada.tsx (lines 21-98) and ColumnsSaida.tsx (lines 21-112). Enum members (tipo, aceitacao, aspecto, presenca) come from the backend as *_humanizado strings; the raw choice enums are not defined in this partition.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
