# RULE-SEPSE-089 — Current protocol tab requires non-empty checklist items

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | validation |
| Status | OK |
| Confidence | medium |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The "Protocolo Atual" tab is only rendered if trilhaInterativaAtual exists AND its itens_trilha_interativa (checklist items) field is truthy/non-empty; otherwise only historical tabs (if any) are shown.

## Inputs

- trilhaInterativaAtual.itens_trilha_interativa (array)

## Outputs

- tab visibility (boolean)

## Logic

```text
if (trilhaInterativaAtual && trilhaInterativaAtual.itens_trilha_interativa) {
  render Tabs.TabPane "Protocolo Atual"
}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor]/leito/[id_leito]/ocupacao/[id_ocupacao]/sepse/[id_trilha]/index.tsx` | 269-278 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-FE-08-006`

**Related rules:** _none_

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
