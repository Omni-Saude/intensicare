# RULE-COMUNICACAO-003 — AcaoHomecare balanco_hidrico method-reference bug

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | formula |
| Status | DISCREPANCY |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | comunicacao |

## Rule
AcaoHomecareSerializer exposes a computed "balanco_hidrico" field that is meant to return the primary key of the fluid-balance record tied to whichever of entrada/saida/sinal_vital triggered the action, but the code references the bound method `get_pk` without calling it.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| instance.entrada | object reference (nullable) | — | — |
| instance.saida | object reference (nullable) | — | — |
| instance.sinal_vital | object reference (nullable) | — | — |

## Outputs
| Name | Type | Unit |
|---|---|---|
| balanco_hidrico | expected int (pk); actual bound-method object | — |

## Logic
```text
obj = instance.entrada or instance.saida or instance.sinal_vital
if obj:
    return obj.balanco_hidrico.get_pk   # NOTE: missing "()" call
return None
```

## Edge cases (as implemented)
As written, `get_pk` is not invoked — it evaluates to a Python bound-method object, not an integer/pk value. Serializing this through a CharField (as declared: `alerta`... actually this field itself is a bare SerializerMethodField with no explicit output field type) will coerce the bound method to its repr string (e.g. "<bound method ... at 0x...>") rather than the intended id. This almost certainly renders incorrect/useless data to any API consumer of this field.

## Verification
- Verdict: UNVERIFIABLE
- Reference: No authoritative published clinical reference. Internal serializer field meant to expose the fluid-balance (balanco hidrico) record pk for a homecare-feed action. Relevant external authority is only Python/Django attribute-access + property semantics.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_homecare/api/v1/serializers/acao_homecare.py | 54-58 | 8166c07e | primary |
- Merged from: RULE-acao-BE-07-001
- Related rules: RULE-COMUNICACAO-034

## Notes
Recorded verbatim per instructions; the likely intended call was `obj.balanco_hidrico.get_pk()` or simply `obj.balanco_hidrico_id`/`obj.balanco_hidrico.pk`.

---

Reconciled: AcaoHomecare (trilha_homecare/models/acao_homecare.py) is explicitly documented in its own docstring as "Modelo do feed do homecare" — i.e. this serializer bug and RULE-COMUNICACAO-034's leito-validation bug are two different defects on the SAME homecare-feed model/serializer family, confirmed in-cluster (not misrouted).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
