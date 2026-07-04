# RULE-SEPSE-076 — SEPSE interactive protocol bundle (hour-1 vs reassessment items)

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
Accepting the SEPSE protocol instantiates exactly seven checklist items in two bundles. The "primeira_hora" (hour-1) bundle: request labs, start/escalate antimicrobials, perform volume expansion. The "reavaliacao" (reassessment) bundle: labs review, hemodynamic status, invasive devices, vasoactive drugs.

## Inputs

- trilha_interativa (identifier)

## Outputs

- items (list[{nome_item, pacote}])

## Logic

```text
itens = [
  {nome_item: "solicitacao_exames",                  pacote: "primeira_hora"},
  {nome_item: "inicio_escalonamento_antimicrobiano", pacote: "primeira_hora"},
  {nome_item: "realizacao_expansao_volemica",        pacote: "primeira_hora"},
  {nome_item: "exames",                              pacote: "reavaliacao"},
  {nome_item: "status_hemodinamico",                 pacote: "reavaliacao"},
  {nome_item: "dispositivos_invasivos",              pacote: "reavaliacao"},
  {nome_item: "drogas_vasoativas",                   pacote: "reavaliacao"},
]
# each item gets trilha_interativa set, then bulk-validated and saved
```

## Edge cases (as implemented)

Items are created via the item serializer (many=True) with is_valid(raise_exception=True); creation triggers checagem_envio_automatico per item (core.utils, out of partition).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/api/v1/serializers/trilha_interativa_sepse.py` | 107-143 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-sepse-BE-02-008`

**Related rules:**

- [RULE-SEPSE-096](RULE-SEPSE-096-sepsis-interactive-bundle-step-and-package-enums.md)
- [RULE-SEPSE-078](RULE-SEPSE-078-sepsis-first-hour-auto-check-guard.md)
- [RULE-SEPSE-072](RULE-SEPSE-072-sepse-protocol-acceptance-workflow-and-orange-alert.md)

## Notes

Mirrors the Surviving-Sepsis "hour-1 bundle" concept. Item ordering elsewhere is by (pacote, nome_item).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
