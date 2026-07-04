# RULE-OPERACIONAL-INFRA-056 — Diagnosis-list checks are non-functional (vars().fromkeys misuse)

| Field | Value |
|---|---|
| Cluster | operacional-infra |
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Every criterion that tries to test whether a diagnosis string is present/absent in diagnostico_1..4 or diag_inter_1..5 builds the candidate set with vars(ultima_evolucao).fromkeys((...field names...)). dict.fromkeys(iterable) returns a NEW dict whose KEYS are the field-name strings (e.g. "diagnostico_1") and whose VALUES are all None; it does NOT read the object's actual field values. Consequently the membership/startswith tests operate on the literal field-name strings (or on all-None .values()), never on real diagnoses.

## Inputs

| name | type | unit | range |
|---|---|---|---|
| ultima_evolucao diagnostico_1..4 / diag_inter_1..5 | string fields on DadosBrutosEvolucao |  |  |

## Outputs

| name | type | unit |
|---|---|---|
| diagnosis sub-condition | boolean (effectively constant) |  |

## Logic

```text
candidate = vars(ultima_evolucao).fromkeys(("diagnostico_1","diagnostico_2","diagnostico_3","diagnostico_4"))
# candidate == {"diagnostico_1": None, ...}  -> keys are field names, values all None
list(filter(lambda x: x == "DRC em TRS", candidate))            # iterates KEY strings -> always []
list(filter(lambda x: x.startswith("I64"), candidate))          # iterates KEY strings -> always []
"SCA - ..." in candidate.fromkeys(...).values()                 # values() all None -> always False
# => "presence" tests are always False; "not <presence>" (absence) tests are always True.
```

## Edge cases (as implemented)

Systemic; makes presence-of-diagnosis gates unsatisfiable and absence-of-diagnosis gates vacuously satisfied.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_automatica/models/trilhas_v3/trilha_sepse.py` | 593-605, 654-666, 722-734 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-systemic-BE-03-001`

**Related rules:**

- [RULE-OPERACIONAL-INFRA-048](../scheduling-operational/RULE-OPERACIONAL-INFRA-048-backend-ci-gate-covers-only-trilha-manual-tests.md)

## Notes

Same defect recurs in trilha_estabilidade.py c13 (I64 startswith, lines 692-704), trilha_eficiencia.py c3/c4/c5/c6/c7 (SCA/I64/antecedentes, lines 456-487, 521-552, 588-607, 698-713, 770-785), trilha_profilaxia.py c1 (diagnosticos_intern, lines 259-271), and trilha_sepse.py c8/c9/c10. Flagged individually in each affected criterion rule.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
