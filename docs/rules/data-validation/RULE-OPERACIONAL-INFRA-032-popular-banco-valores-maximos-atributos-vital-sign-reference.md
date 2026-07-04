# RULE-OPERACIONAL-INFRA-032 — popular_banco valores_maximos_atributos — vital-sign reference ranges for synthetic data, PEEP mismatch vs validators.py

| Field | Value |
|---|---|
| Category | data-validation |
| Type | threshold |
| Status | DISCREPANCY |
| Verification | DISCREPANCY, impact: none |
| Confidence | high |
| Cluster | operacional-infra |

## Rule

Test/seed-data generator (popular_banco) defines a table of (min,max) reference ranges per vital-sign/lab attribute used to produce random plausible values for synthetic ICU records. For every attribute EXCEPT peep, these ranges are numerically identical to the corresponding validators in utils/validators.py. For peep, this table uses an upper bound of 41, while PeepValidator (RULE-vitais-BE-11-009) enforces an upper bound of 40 — a synthetic record generated with peep=41 would fail real validation.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| atributo | string | - | one of: peep, po2, tec, fr, lactato_arterial, volume_corrente, pas, pad, pam, debito_urinario_24h, bilirrubinas, temperatura, paco2, creatinina, leucocitos, frequencia_cardiaca, plaquetas, dobutamina |

## Outputs

| Name | Type | Unit |
|---|---|---|
| valor_sorteado | random integer in (min,max) via randint(a,b) | - |

## Logic

```text
valores_maximos_atributos = {
  "peep": (0, 41),                 # PeepValidator uses (0, 40) -- MISMATCH
  "po2": (0, 500),
  "tec": (3, 20),
  "fr": (0, 50),
  "lactato_arterial": (0, 20),
  "volume_corrente": (0, 1500),
  "pas": (50, 250),
  "pad": (0, 150),
  "pam": (0, 200),
  "debito_urinario_24h": (0, 10000),
  "bilirrubinas": (0, 30),
  "temperatura": (20, 43),
  "paco2": (0, 150),
  "creatinina": (0, 20),
  "leucocitos": (0, 40000),
  "frequencia_cardiaca": (0, 200),
  "plaquetas": (0, 700000),
  "dobutamina": (0, 30),
}
sorteia_dados(dados_prontuario):
  _atributo = atributos[randint(0, 16)]     # atributos has 18 items, indices 0-17
  a, b = valores_maximos_atributos[_atributo]
  dados_prontuario[_atributo] = randint(a, b)
```

## Edge cases (as implemented)

atributos list has 18 entries (index 0-17), but randint(0,16) can only select indices 0 through 16 — index 17, 'dobutamina', can NEVER be chosen by sorteia_dados, so the 'dobutamina' key is never populated into dados_prontuario by this random-selection mechanism (dead/unreachable branch for that attribute in the seed generator).

## Verification

- Verdict: DISCREPANCY (clinical impact: none)
- Reference: No external authoritative published reference defines a numeric data-entry cap for PEEP; PEEP (cmH2O) is a set ventilator parameter, not a validated scale/equation. The only governing authority is the internal production validator PeepValidator (utils/validators.py:73-81, RULE-vitais-BE-11-009), which enforces 0 <= peep <= 40. Clinically, applied PEEP is typically 5-15 cmH2O and rarely exceeds ~24 (up to ~30 in severe ARDS), so both 40 and 41 are non-physiologic sanity ceilings well above real use (cf. ARDSNet/Berlin high-PEEP tables).

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/popular_banco.py` | 38-62 | `8166c07e` | primary |

- Merged from: RULE-seed-BE-11-031
- Related rules: RULE-OPERACIONAL-INFRA-012, RULE-OPERACIONAL-INFRA-013, RULE-OPERACIONAL-INFRA-055

## Notes

DISCREPANCY #1: peep upper bound 41 here vs 40 in PeepValidator (RULE-vitais-BE-11-009) — recorded verbatim from both files, not reconciled. DISCREPANCY #2 (bug, not a data-range issue): dobutamina is statistically unreachable via sorteia_dados due to the randint(0,16) bound against an 18-item list. This is a test-data script, not an enforced validator, so it does not itself gate real user input — but it is documented here because it encodes the same reference ranges as the production validators and reveals the one place they diverge.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
