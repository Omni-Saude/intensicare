# RULE-FORMULARIOS-CLINICOS-043 — Invasive-device dressing and exchange scheduling

| Field | Value |
|---|---|
| Category | scheduling-operational |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | formularios-clinicos |

## Rule
Per invasive device, a checkable ("checavel") group records site, insertion/dressing dates, dressing type and aspect, next-exchange date and external-insertion flag; some devices have device-specific fields.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| data_proxima_troca | date | null | null |
| curativo | enum | null | filme_transparente\|curativo_convencional |

## Outputs

| Name | Type | Unit |
|---|---|---|
| device record | object | null |

## Logic

```text
Devices (each grupoKey, checavel:true): cateter_venoso_central, colostomia, ileostomia, jejunostomia,
  traqueostomia, gastrostomia, cateter_duplo_lumen_hemodialise, pressao_arterial_invasiva,
  acesso_venoso_periferico, fistula_arteriovenosa, hipodermoclise, picc, port_a_cath, observacao.
Standard fields (CVC/ostomies/traqueo/gastro/CDL/PAI): local(string), data_insercao(date), data_curativo(date),
  curativo {filme_transparente, curativo_convencional}, aspecto_do_curativo {limpa_seca, flogisticos_secrecao,
  flogisticos_sem_secrecao, sanguinolento_sem_flogisticos}, data_proxima_troca(date),
  inserido_em_outra_instituicao(boolean).
acesso_venoso_periferico: local, data_insercao, data_curativo, data_proxima_troca, flebite(boolean) [no dressing enums].
fistula_arteriovenosa: local + fremito_palpavel(boolean).
hipodermoclise / picc / port_a_cath: local only.
```

## Edge cases (as implemented)

data_proxima_troca drives dressing/device exchange scheduling; no automatic interval computed here.

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | src/utils/dataForms/dataFormEnfermagem.ts | 781-1596 | f9656be2 | primary |

- Merged from: RULE-devices-FE-01-047
- Related rules: RULE-FORMULARIOS-CLINICOS-020, RULE-FORMULARIOS-CLINICOS-022

## Notes

The flag checavel=true marks a device as a checklist/round item. AVP tracks flebite (phlebitis) rather than a dressing. Reassigned from ventilacao: generic invasive-device (14 types; tracheostomy is 1 of 14) nursing form definition with no ventilation logic; complements the backend field catalog RULE-FORMULARIOS-CLINICOS-022.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
