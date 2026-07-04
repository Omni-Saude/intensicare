# RULE-BALANCO-HIDRICO-046 — Fluid-balance PDF export with optional signatures

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | billing-administrative |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Generating a fluid-balance PDF report presents a confirmation modal asking whether to include signatures ("assinaturas"). The chosen boolean is sent to the report endpoint and the resulting file is downloaded with a name that embeds the report date.

## Inputs

- assinatura
- dia

## Outputs

- downloaded file

## Logic

```text
onClick "Gerar PDF":
  Modal.confirm("Deseja gerar o relatório das prescrições do paciente com assinaturas?")
    Sim -> _getRelatorioVisaoGeral(assinatura=true)
    Não -> _getRelatorioVisaoGeral(assinatura=false)

_getRelatorioVisaoGeral(assinatura):
  dia = date.format("YYYY-MM-DD")
  data = getRelatorioVisaoGeral(..., balanco.id, { dia, assinatura })
  download(data, `Relatorio_balanco_hidrico_${dia}.pdf`)
```

## Edge cases (as implemented)

If balanco is undefined (not yet loaded), balanco!.id would throw at runtime (non-null assertion, no guard).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/balanco/index.tsx` | 152-227 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-FE-08-002`

**Related rules:** _none_

## Notes

The modal's own button labels ("Sim"/"Não") are wired to the opposite of what a reader might assume from the okButtonProps being hidden and cancelButtonProps styled danger; confirmed by reading the onClick handlers directly, not by button styling.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
