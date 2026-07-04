# RULE-BALANCO-HIDRICO-035 — List endpoint required-day + auto-create with mismatched day value

| Field | Value |
|---|---|
| Cluster | balanco-hidrico |
| Category | care-pathway |
| Type | workflow |
| Status | DISCREPANCY |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
The list() action requires the 'dia' query parameter (raises ValidationError if absent). It then recomputes a *separate* dia_param using the 07:00-cutoff rule, but assigns it as `dia_param if now.hour >= 7 else now.date() - timedelta(days=1)` — meaning when the current hour is before 07:00, the caller-supplied 'dia' string is discarded and replaced with "yesterday" (a date object) for the purposes of auto-creating a new BalancoHidrico record, even though the actual filter used to look up an existing record (get_queryset()) parses and uses the caller-supplied 'dia' string correctly. Only when no matching record is found does the record get created with this second, inconsistent dia_param value.

## Inputs

- dia (query param)
- now.hour (hour)

## Outputs

- BalancoHidrico record (existing or newly created)

## Logic

```text
dia_param = query_params["dia"]              # required, string
if not dia_param: raise ValidationError("É necessário enviar um dia no parametro")
now = datetime.now().astimezone()
dia_param = dia_param if now.hour >= 7 else now.date() - timedelta(days=1)
# NOTE: when now.hour < 7, dia_param becomes `now.date() - 1 day` (a date object),
# NOT the parsed value of the caller-supplied string.
leito = Leito.objects.get(pk=kwargs["ocupacoes__pk"])
obj = filter_queryset(get_queryset()).first()   # get_queryset() independently re-parses query_params["dia"]
if not obj:
    obj = BalancoHidrico.objects.create(leito=leito, nr_atendimento=leito.nr_atendimento, dia=dia_param)
return Response(BalancoHidricoSerializer(obj).data)
```

## Edge cases (as implemented)

If invoked before 07:00 local time for a day other than "yesterday" (e.g. requesting an explicit historical date), and no BalancoHidrico exists yet for that date, the system silently creates the new record dated "yesterday" instead of the requested date. This does not affect lookups of already-existing records (those use get_queryset(), which correctly parses the requested 'dia').

## Divergence

list() requires the 'dia' query param (raises ValidationError if absent), then reassigns dia_param = dia (the caller string) if now.hour >= 7 else now.date() - timedelta(days=1) (a date object). When invoked before 07:00 local time for an explicit historical date with no existing record, the auto-created BalancoHidrico is dated 'yesterday' instead of the requested date. Lookups of already-existing records use get_queryset(), which re-parses the caller 'dia' correctly, so only first-time creation is mis-dated.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `trilha_homecare/api/v1/views/balanco_hidrico.py` | 48-64 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-balanco-BE-08-007`

**Related rules:**

- [RULE-BALANCO-HIDRICO-023](../physiological-calculation/RULE-BALANCO-HIDRICO-023-default-clinical-day-cutoff-07-00-for-balanco-hidrico.md)
- [RULE-BALANCO-HIDRICO-036](RULE-BALANCO-HIDRICO-036-balanco-hidrico-auto-provisioning-no-direct-write-endpoints.md)

## Notes

Recorded verbatim per ground rules; this looks like an unintended bug (dia_param reassignment appears to have been meant to mirror get_queryset()'s cutoff-default logic for the *no dia supplied* case, but list() requires dia and then overwrites it anyway).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
