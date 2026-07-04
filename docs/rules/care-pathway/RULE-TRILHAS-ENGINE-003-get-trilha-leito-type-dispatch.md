# RULE-TRILHAS-ENGINE-003 — get_trilha leito-type dispatch

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | trilhas-engine |

## Rule
Resolves the active care-pathway (trilha) record for a bed (leito) and encounter, branching on the bed's tipo. 'automatica' returns the first matching record with no explicit ordering; 'homecare' returns the most recently created matching record; any other tipo raises a validation error.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| Trilha | Django model class |  |  |
| leito | object with nr_atendimento attribute |  |  |
| tipo | string enum |  | "automatica" \| "homecare" \| other |

## Outputs

| Name | Type | Unit |
|---|---|---|
| trilha | model instance or None |  |

## Logic
```text
IF tipo == "automatica":
  RETURN Trilha.objects.filter(nr_atendimento=leito.nr_atendimento).first()
ELIF tipo == "homecare":
  RETURN Trilha.objects.filter(nr_atendimento=leito.nr_atendimento)
                        .order_by("-criado_em").first()
ELSE:
  RAISE ValidationError("Tipo de leito inválido")
```

## Edge cases (as implemented)
No matching row returns None silently (not raised) for automatica/homecare. The 'automatica' branch relies on the Trilha model's default queryset ordering (not defined in this partition) to pick 'the' record when more than one exists for the same nr_atendimento; 'homecare' is explicit (-criado_em). A leito.tipo of "manual" (seen in utils/popular_banco.py) is not one of the two handled branches and would hit the else-raise.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `utils/trilha.py` | 4-14 | `8166c07e` | primary |

- Merged from: `RULE-trilha-BE-11-001`
- Related rules: RULE-TRILHAS-ENGINE-001, RULE-TRILHAS-ENGINE-002, RULE-TRILHAS-ENGINE-012

## Notes
Called throughout utils/handlers.py (conteudo_trilha_automatica_criterios, conteudo_observacao_criterios, conteudo_trilha_homecare_criterios). AMBIGUOUS because the 'automatica' branch's lack of explicit ordering makes the chosen record implementation-dependent (default PK/insertion order) unlike the homecare branch.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
