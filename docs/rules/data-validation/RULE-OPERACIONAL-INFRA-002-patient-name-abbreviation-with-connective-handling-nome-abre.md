# RULE-OPERACIONAL-INFRA-002 — Patient name abbreviation with connective handling (nome_abreviado_paciente)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | formula |
| Status | DISCREPANCY |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | operacional-infra |

## Rule

Produces a shortened display name - keeps the first two words in full, and if the second word is a Portuguese connective (da/de/do/das/dos) keeps the first three words in full, abbreviating every remaining word to its initial letter.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| nome_completo | string | - | must contain >= 2 words |

## Outputs

| Name | Type | Unit |
|---|---|---|
| iniciais_nome | string | - |

## Logic

```text
lista_conectivos = ["da", "de", "do", "das", "dos"]
nome_fracionado = nome_completo.split(" ")
iniciais_nome = ""
for i, parte in enumerate(nome_fracionado):
    if (i < 3 and nome_fracionado[1].lower() in lista_conectivos) or (i < 2):
        iniciais_nome += f' {parte}'        # keep full word
    else:
        iniciais_nome += f' {parte[0]}'     # keep initial only
return iniciais_nome                        # leading space; each token space-prefixed
```

## Edge cases (as implemented)

Always keeps first 2 tokens full (i<2); keeps a 3rd full only if token index 1 is a connective. Result has a leading space. A name with fewer than 2 words raises IndexError on nome_fracionado[1]. A word that is an empty string (double space) raises IndexError on parte[0] in the else branch.

## Verification

- Verdict: UNVERIFIABLE
- Reference: No authoritative published reference exists. Portuguese display-name abbreviation with connective (da/de/do/das/dos) handling is a proprietary UI/partial-anonymization business rule, not governed by any clinical guideline or standard calculator.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 34-48 | `8166c07e` | primary |

- Merged from: RULE-ADMIN-BE-12-024

## Notes

DISCREPANCY - unguarded nome_fracionado[1] access crashes on single-word names. Purpose is patient-identity display/ partial-anonymization. Sibling helper fraciona_nome_paciente (core/utils.py:26-31; trilha_automatica/utils.py:16-21) returns concatenated initials of every word (not recorded separately - trivial transform).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
