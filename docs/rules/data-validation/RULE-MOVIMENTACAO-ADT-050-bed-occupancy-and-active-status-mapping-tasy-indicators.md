# RULE-MOVIMENTACAO-ADT-050 — Bed occupancy and active-status mapping (Tasy indicators)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
When upserting a Leito, occupancy and active flags are derived from Tasy single-character indicators: a bed is occupied iff ie_ocupado == "S" (Sim/Yes), and active iff ie_situacao == "A" (Ativo). nr_atendimento (encounter number) is copied through.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| ie_ocupado | char(1), {S, N, null} |  |  |
| ie_situacao | char(2), {A, ...} |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| ocupado | boolean |  |
| ativo | boolean |  |

## Logic
```text
Leito.update_or_create(
    codigo=cd_unidade_compl, nome=ds_leito, setor=setor,
    defaults={
        "tipo": tipo,
        "ocupado": (ie_ocupado == "S"),
        "nr_atendimento": nr_atendimento,
        "ativo": (ie_situacao == "A"),
    })
```

## Edge cases (as implemented)
Any value other than exactly "S"/"A" (including null) maps to False. Leito matched on the triple (codigo, nome, setor); Leito.DoesNotExist / MultipleObjectsReturned are caught and logged as warnings (row skipped).

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/etl/estabelecimento_setor_leito.py` | 64-90 | `8166c07e` | primary |

- Merged from: RULE-leito-BE-02-003
- Related rules: RULE-MOVIMENTACAO-ADT-021

## Notes
Estabelecimento and Setor are update_or_create'd on (codigo, parent) with nome+tipo defaults (lines 8-61).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
