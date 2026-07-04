# RULE-BALANCO-HIDRICO-041 — Fluid-balance (balanco hidrico) row type-label resolution and signature-date format

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Prepares fluid-balance rows for display. For intake ("entrada") and output ("saida") rows, the displayed type is the humanized type label UNLESS the type is the free-text sentinel ("outra_entrada" for intake, "outra_saida" for output), in which case the user-entered custom name is shown. For all three route types (entrada, saida, sinais-vitais) the signature timestamp is formatted DD/MM/YYYY HH:mm when present.

## Inputs

- route
- values

## Outputs

- displayRows

## Logic

```text
switch (route):
  case "entrada":
    for each entrada:
      tipo = (entrada.tipo != "outra_entrada") ? entrada.tipo_humanizado : entrada.nome
      data_assinatura = entrada.data_assinatura && moment(entrada.data_assinatura).format("DD/MM/YYYY HH:mm")
  case "saida":
    for each saida:
      tipo = (saida.tipo != "outra_saida") ? saida.tipo_humanizado : saida.nome
      data_assinatura = saida.data_assinatura && moment(saida.data_assinatura).format("DD/MM/YYYY HH:mm")
  case "sinais-vitais":
    for each sinalVital:
      data_assinatura = sinalVital.data_assinatura && moment(...).format("DD/MM/YYYY HH:mm")
```

## Edge cases (as implemented)

If data_assinatura is falsy it is left falsy (short-circuit, no format applied). sinais-vitais rows keep their original tipo (no relabeling). No default branch: an unrecognized route returns undefined.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/convertBalancoData.ts` | 3-42 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-02-001`

**Related rules:**

- [RULE-BALANCO-HIDRICO-042](RULE-BALANCO-HIDRICO-042-fluid-balance-record-signature-eligibility.md)
- [RULE-BALANCO-HIDRICO-053](../data-validation/RULE-BALANCO-HIDRICO-053-fluid-intake-output-field-set-and-volume-unit-entrada-saida.md)

## Notes

Sentinel values "outra_entrada"/"outra_saida" are the domain-meaningful "Other" intake/output categories that carry a free-text name. Route enum values also meaningful (entrada=intake, saida=output, sinais-vitais=vital signs).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
