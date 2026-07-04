# RULE-PRESCRICAO-021 — Bulk medication-administration checkoff (multi_checagem)

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | prescricao |

## Rule
A custom PATCH action accepts a list of {"horario": <HorariosPrescricao pk>, "prescricao": <PrescricaoContinua pk>} pairs and marks each corresponding schedule slot as administered (administrado=True), always setting administrado unconditionally to True (no way to un-check via this endpoint) and stamping each with the current leito id from the URL.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| request.data.horarios | list[object] |  | each item: {horario: uuid, prescricao: uuid, ...other passthrough fields} |

## Outputs

| Name | Type | Unit |
|---|---|---|
| HorariosPrescricao.administrado | boolean |  |

## Logic

```text
horarios = request.data.pop("horarios")
for horario in horarios:
    horario_instance = HorariosPrescricao.objects.get(pk=horario["horario"])
    data = request.data                      # NOTE: same dict object reused/mutated every iteration
    data["horario"] = horario_instance.horario
    data["administrado"] = True
    data["prescricao_continua"] = horario["prescricao"]
    data["leito"] = kwargs["ocupacoes__pk"]
    serializer = HorarioPrescricaoSerializer(data=data, instance=horario_instance, context=...)
    serializer.is_valid(raise_exception=True)
    serializer.save()
return Response({"message": "Horários checados com sucesso!"})
```

## Edge cases (as implemented)
`HorariosPrescricao.objects.get(pk=...)` (not objects_without_deleted) - could match a soft-deleted schedule slot. The shared `request.data` dict is mutated in place across loop iterations rather than copied per item; functionally each of the four overwritten keys is reset every iteration, but any other keys in request.data persist unchanged across all items. Any single missing/invalid pk raises HorariosPrescricao.DoesNotExist or a validation error, aborting the loop (partial batch may already be saved for earlier items - not wrapped in a transaction.atomic block).

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/prescricao.py` | 113-126 | `8166c07e` | primary |

**Merged from:**

- RULE-prescricao-BE-08-044

**Related rules:**

- RULE-PRESCRICAO-008

## Notes
Not wrapped in @transaction.atomic, unlike the destroy() methods in entradas.py/saidas.py/sinais_vitais.py.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
