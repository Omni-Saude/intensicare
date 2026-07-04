# RULE-SEDACAO-027 — Unique sedative per prontuario + dose unit

| Field | Value |
|---|---|
| Cluster | sedacao |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
A given sedative drug can appear at most once per prontuario; quantity is in ml.

## Inputs

| name | type |
|---|---|
| (dados_prontuario, nome_sedativo) | tuple |

## Outputs

| name | type |
|---|---|
| uniqueness constraint | db constraint |

## Logic

```text
Meta.unique_together = ('dados_prontuario', 'nome_sedativo')
quantidade: PositiveIntegerField help_text "Quantidade de Sedativo em ml", validators=[SedativoValidator()]
on_delete=SET_NULL (nullable FK) - sedative rows survive prontuario deletion.
```

## Edge cases (as implemented)

Duplicate drug for same prontuario -> IntegrityError. Overdose criterion uses max ml (>15).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_manual/models/sedativo.py` | 8-24 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-cons-BE-10-068`

**Related rules:**

- [RULE-SEDACAO-026](../drug-dosing/RULE-SEDACAO-026-sedative-drug-enumeration-sedativo-nome-sedativo-choices.md)
- [RULE-SEDACAO-015](../care-pathway/RULE-SEDACAO-015-sedation-manual-c1-sedoanalgesia-overdose-any-sedative-15-ml.md)

## Notes

nome_sedativo choices fentanil/midazolam/propofol/cetamina (see RULE-choice-BE-10-071).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
