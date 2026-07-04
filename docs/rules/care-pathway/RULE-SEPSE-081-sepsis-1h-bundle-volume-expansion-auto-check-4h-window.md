# RULE-SEPSE-081 — Sepsis 1h bundle - volume expansion auto-check (4h window)

| Field | Value |
|---|---|
| Cluster | sepse |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Auto-marks 'realizacao_expansao_volemica' done when an ADEP administration record updated within the 4h preceding pathway creation shows lactated-Ringer OR 0.9% saline volume > 0; posts observation with the administering professional.

## Inputs

- adep.dt_atualizacao_adep (datetime, >= trilha_interativa.criado_em - 4h)
- adep.soro_lactato (number, mL, > 0)
- adep.soro_09 (number, mL, > 0)

## Outputs

- item.checado (boolean)
- observacao (text)

## Logic

```text
elif item.nome_item == "realizacao_expansao_volemica":
    adep_4h = trilha.adep_leito.filter(dt_atualizacao_adep__gte = trilha_interativa.criado_em - timedelta(hours=4))
    if adep_4h.filter(Q(soro_lactato__gt=0) | Q(soro_09__gt=0)).exists():
        item.checado = True; item.save()
        profissional = adep_leito.first().ds_soro_lactato or adep_leito.first().ds_soro_09
        mensagem = f"Realizada reposicao volemica na 1a hora. Administrado por {profissional}"
        enviar_observacao_trilha_interativa(mensagem, "sepse", item.trilha_interativa, system_user)
```

## Edge cases (as implemented)

4-hour inclusive lookback (__gte) from pathway creation time. Condition is soro_lactato>0 OR soro_09>0 (strict >0). Professional attribution = ds_soro_lactato else ds_soro_09 (from adep_leito.first(), not necessarily the matched row).

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/utils.py` | 252-270 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-CAREPATH-BE-12-005`

**Related rules:**

- [RULE-SEPSE-078](RULE-SEPSE-078-sepsis-first-hour-auto-check-guard.md)
- [RULE-SEPSE-061](../drug-dosing/RULE-SEPSE-061-sepse-volume-expansion-expansao-volemica-decision-and-dosing.md)

## Notes

Distinct 4h window here vs 24h for antibiotics (RULE-004) and no window for exams (RULE-003).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
