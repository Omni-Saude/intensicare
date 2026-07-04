# RULE-EVOLUCOES-017 — Medico form bundles vital-signs creation tied to daily balanco hidrico

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | decision-tree |
| Status | AMBIGUOUS |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | evolucoes |

## Rule
If the physician-form payload includes a 'sinais_vitais' block, the system derives the day from 'dt_registro' (format 'YYYY-MM-DD HH:MM'), looks up (or auto-creates) that leito's BalancoHidrico for that day, attaches its id to the vitals payload, and creates the SinaisVitais record directly via the serializer (bypassing the SinaisVitais viewset).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dt_registro ['YYYY-MM-DD HH:MM'] |  |  |  |
| sinais_vitais (payload block) |  |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| SinaisVitais record |  |  |
| BalancoHidrico record (existing or newly created) |  |  |

## Logic
```text
sinais_data = data.get("sinais_vitais")
if sinais_data:
    dia_form = datetime.strptime(data["dt_registro"], "%Y-%m-%d %H:%M").date()
    try:
        balanco_dia = leito.balancohidrico_set.get(dia=dia_form).get_pk   # see edge_cases
    except BalancoHidrico.DoesNotExist:
        try:
            balanco_dia = BalancoHidrico.objects.create(
                nr_atendimento=leito.nr_atendimento, leito=leito, dia=dia_form).pk
        except Exception as e:
            print(e)
            raise ValidationError({"sinais_vitais": f"Não foi possível criar o balanço hídrico para o dia {dia_form}: {e}"})
    sinais_data["balanco"] = balanco_dia
    sinais_serializer = SinaisVitaisSerializer(data=sinais_data, context={"request": request})
    sinais_serializer.is_valid(raise_exception=True)
    sinais_serializer.create(sinais_serializer.validated_data)
```

## Edge cases (as implemented)
`.get_pk` is called on the BalancoHidrico instance returned by `leito.balancohidrico_set.get(...)`; Django model instances normally expose `.pk`, not `.get_pk`. Whether BalancoHidrico defines a custom `get_pk` property/method cannot be confirmed from this partition (models.py is out of scope), so this may raise AttributeError instead of proceeding — which would NOT be caught by the surrounding `except BalancoHidrico.DoesNotExist` clause and would propagate as a 500 error rather than falling back to record creation. Any other exception during BalancoHidrico.create() is logged via print() (not proper logging) and surfaced as a ValidationError under key "sinais_vitais".

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/formulario_medico.py` | 40-61 | `8166c07e` | primary |
- Merged from: RULE-formulario-BE-08-030
- Related rules: RULE-EVOLUCOES-031, RULE-EVOLUCOES-028

## Notes
Flagged AMBIGUOUS rather than DISCREPANCY because BalancoHidrico's model definition (which would confirm/deny a get_pk property) is outside partition BE-08's scope.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
