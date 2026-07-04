# RULE-SEPSE-096 — Sepsis interactive bundle step and package enums

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Enumerates the interactive sepsis protocol packages (primeira_hora = first hour; reavaliacao = reassessment) and the bundle item names, including the Surviving-Sepsis 1-hour actions.

## Inputs

- pacote choice, nome_item choice (string enum)

## Outputs

- allowed choices (enum)

## Logic

```text
pacote() = [("primeira_hora","Primeira hora"), ("reavaliacao","Reavaliacao")]
nome_item() = [
  ("solicitacao_exames", "Solicitacao de exames laboratoriais e culturas para bacterias e fungos em ate 1 hora"),
  ("inicio_escalonamento_antimicrobiano", "Inicio ou escalonamento antimicrobiano e realizar controle de foco em ate 1 hora"),
  ("realizacao_expansao_volemica", "Realizacao de expansao volemica com cristaloides em ate 1 hora"),
  ("exames","Exames"), ("status_hemodinamico","Status hemodinamico"),
  ("dispositivos_invasivos","Dispositivos invasivos"), ("drogas_vasoativas","Drogas vasoativas"),
]
```

## Edge cases (as implemented)

First three item labels encode the 1-hour SSC bundle deadlines textually.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/choices/trilha_interativa.py` | 4-35 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-interativa-BE-03-130`

**Related rules:**

- [RULE-SEPSE-076](RULE-SEPSE-076-sepse-interactive-protocol-bundle-hour-1-vs-reassessment-ite.md)
- [RULE-SEPSE-079](RULE-SEPSE-079-sepsis-1h-bundle-exam-solicitation-auto-check.md)

## Notes

Choices applied to ItemTrilhaInterativaSpese.pacote and .nome_item fields.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
