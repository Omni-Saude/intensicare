# RULE-CADASTROS-UI-016 — Brazilian document and number formatting masks

| Field | Value |
|---|---|
| Cluster | cadastros-ui |
| Category | data-validation |
| Type | formula |
| Status | OK |
| Confidence | high |
| Verification verdict | DISCREPANCY |
| Clinical impact | none |

## Rule
Applies display masks to Brazilian identifiers and numbers: CPF, CNPJ, CEP (postal), phone (length-dependent), BRL currency, and human byte sizes. Also an inverse "unformat" that strips mask punctuation.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| value | string |  |  |
| type | enum |  | cpf \| cnpj \| cep \| tel \| real \| bytes |

## Outputs

| name | type | unit |
|---|---|---|
| formatted | string |  |

## Logic

```text
cpf:  /(\d{3})(\d{3})(\d{3})(\d{2})/ -> "$1.$2.$3-$4"        (11 digits)
cnpj: /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/ -> "$1.$2.$3/$4-$5"  (14 digits)
cep:  /(\d{2})(\d{3})(\d{3})/ -> "$1.$2-$3"                  (8 digits)
tel by value.length:
  11 -> /(\d{2})(\d{1})(\d{4})(\d{4})/ -> "($1) $2 $3-$4"    (mobile w/ 9th digit)
  10 -> /(\d{2})(\d{4})(\d{4})/       -> "($1) $2-$3"        (landline w/ DDD)
  9  -> /(\d{1})(\d{4})(\d{4})/       -> "$1 $2-$3"
  8  -> /(\d{4})(\d{4})/             -> "$1-$2"
  default -> value (unchanged)
real: Intl.NumberFormat("pt-BR",{style:currency,currency:BRL}).format(+value)
bytes:
  if bytes==0 -> "0 Bytes"
  kilo=1024; sizes=[Bytes,KB,MB,GB,TB,PB,EB,ZB,YB]
  exponent = floor( log(bytes)/log(1024) )
  result = parseFloat( (bytes/1024^exponent).toFixed(2) ) + " " + sizes[exponent]
unformat: strips characters . - _ / ( ) and spaces
```

## Edge cases (as implemented)

Mask regexes are unanchored and assume the raw digit count already matches; malformed input passes through partially/unchanged. tel branches only on exact lengths 8/9/10/11. bytes: exponent can exceed the sizes array for absurd values (undefined unit) and negative/NaN bytes are unguarded (only 0 is special-cased).

## Verification

- **Verdict:** DISCREPANCY
- **Clinical impact:** none
- **Reference:** Brazilian identifier/postal display masks. CPF/CNPJ are governed by Receita Federal (11-digit CPF displayed 000.000.000-00; 14-digit CNPJ displayed 00.000.000/0000-00). CEP is governed by Correios: official display is the 5-3 form NNNNN-NNN with a single hyphen and NO period ("...não deverão ser sublinhados ou separados por ponto"). Mobile phone (11-digit) is governed by ANATEL's numbering plan: the ninth digit (always 9) is prepended to the original 8-digit subscriber number, conventionally displayed as (XX) 9XXXX-XXXX. BRL currency: Intl/ICU pt-BR currency format (R$ 1.234,56). Byte sizing: 1024 base with SI/JEDEC labels KB/MB/GB (IEC would use KiB/MiB for 1024 base). ([source](https://www.correios.com.br/enviar/precisa-de-ajuda/tudo-sobre-cep))

**Checks**

| Dimension | Result |
|---|---|
| equation | ok for CPF, CNPJ, BRL; diff for CEP; minor-diff for tel(11); n/a for bytes label |
| coefficients | CPF regex (3)(3)(3)(2)->$1.$2.$3-$4 MATCHES official. CNPJ regex (2)(3)(3)(4)(2) ->$1.$2.$3/$4-$5 MATCHES official. CEP regex (2)(3)(3)->$1.$2-$3 produces the 2-3-3 grouping NN.NNN-NNN (spurious leading period) instead of official 5-3 NNNNN-NNN. tel len=11 regex (2)(1)(4)(4)->($1) $2 $3-$4 splits the ninth digit out as "(XX) 9 XXXX-XXXX" rather than the ANATEL-conventional "(XX) 9XXXX-XXXX". |
| units | CPF=11 digits, CNPJ=14, CEP=8, tel=8/9/10/11, real=BRL, bytes=1024-base |
| ranges | All mask regexes are UNANCHORED and assume the raw digit count already matches; malformed/short input passes through partially unchanged. tel branches only on exact lengths 8/9/10/11 (all other lengths returned as-is). bytes: exponent can exceed the 9-element sizes array for absurd inputs (undefined unit); negative/NaN bytes unguarded (only 0 special-cased). Matches catalog edge_cases. |
| rounding | bytes uses parseFloat(x.toFixed(2)); real delegates to Intl.NumberFormat |
| cutoffs | tel length switch: 11=mobile+DDD, 10=landline+DDD, 9=mobile no DDD, 8=landline no DDD |

**Test vectors**

| Inputs | Expected (per reference) | Actual (per legacy) | Match |
|---|---|---|---|
| type=cpf; value=12345678900 | 123.456.789-00 (Receita Federal 000.000.000-00) | 123.456.789-00 | yes |
| type=cnpj; value=11222333444455 | 11.222.333/4444-55 (Receita Federal 00.000.000/0000-00) | 11.222.333/4444-55 | yes |
| type=cep; value=01310100 | 01310-100 (Correios NNNNN-NNN, hyphen only, no period) | 01.310-100 | no |
| type=cep; value=20010000 | 20010-000 (Correios) | 20.010-000 | no |
| type=tel; value=11987654321 | (11) 98765-4321 (ANATEL nono digito, 9XXXX-XXXX block) | (11) 9 8765-4321 | no |
| type=tel; value=1133334444 | (11) 3333-4444 (landline + DDD) | (11) 3333-4444 | yes |
| type=real; value=1234.56 | R$ 1.234,56 (pt-BR BRL) | R$ 1.234,56 | yes |

**Verifier notes**

Legacy confirmed at src/utils/formatter.ts:3-61. CPF, CNPJ and BRL masks match the authoritative Receita Federal / pt-BR standards exactly. DISCREPANCY on CEP: the regex (\d{2})(\d{3})(\d{3}) -> "$1.$2-$3" inserts a period after the first two digits, yielding NN.NNN-NNN (e.g. 01.310-100), whereas the Correios official format is the 5-3 form NNNNN-NNN with a hyphen and explicitly no period. Secondary minor divergence: 11-digit mobile is rendered "(XX) 9 XXXX-XXXX" (ninth digit split off with a space) vs the ANATEL-conventional "(XX) 9XXXX-XXXX". Clinical impact NONE: these are administrative/display masks only, not clinical calculations; underlying value integrity is preserved because unformat() strips '.', '-', '/', '(', ')', '_' and spaces before submit (RULE-CADASTROS-UI-009/010), so the CEP period and phone spacing never reach the stored digits. Administrative impact LOW (cosmetic non-conformance to the Correios/ANATEL display convention). bytes labels KB/MB with a 1024 base is the common JEDEC convention (IEC-strict would be KiB/MiB); not a Brazilian-standard issue, recorded as-written.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/formatter.ts` | 3-61 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-validation-FE-02-004`

**Related rules:**

- [RULE-CADASTROS-UI-009](RULE-CADASTROS-UI-009-cpf-input-mask-and-unformatting.md)
- [RULE-CADASTROS-UI-010](RULE-CADASTROS-UI-010-formusuario-submit-value-normalization.md)

## Notes

CPF=individual taxpayer id (11), CNPJ=company id (14), CEP=postal (8). Phone length 11 = mobile with leading 9; 10 = landline+DDD.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
