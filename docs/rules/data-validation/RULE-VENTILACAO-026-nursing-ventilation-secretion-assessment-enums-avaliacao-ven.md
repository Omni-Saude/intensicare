# RULE-VENTILACAO-026 — Nursing ventilation / secretion assessment enums (avaliacao_ventilacao)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | ventilacao |

## Rule

Respiratory secretion, cough, chest-tube and dressing-aspect enums including flogistic-signs classification.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| avaliacao_ventilacao.* (enum/boolean/date) | | | |

## Outputs

| Name | Type | Unit |
|---|---|---|
| ventilation assessment (object) | | |

## Logic

```text
secrecao_traqueal {pouca, media, grande, aspiracao_ausente}
aspecto {mucoide, purulenta, mucopurulenta, sanguinolenta}
tosse {eficaz, nao_eficaz, ausente}
expansibilidade_pulmonar {simetrica, assimetrica}
dreno_de_torax {esquerdo, direito, bilateral, ausente}
oscilacao(boolean)
aspecto_da_secrecao {espessa, purulenta, serosa, fluida_hialina, hematica, sendimentos}
aspecto_do_curativo {limpa_seca, flogisticos_secrecao, flogisticos_sem_secrecao, sanguinolento_sem_flogisticos}
ausculta {murmurios_vesiculares, pulmoes_livres, roncos, sibilos, estertores}
data_troca_selo(date)
```

## Verification

Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormEnfermagem.ts` | 634-752 | `f9656be2` | primary |

- Merged from: RULE-resp-FE-01-046
- Related rules: RULE-VENTILACAO-019, RULE-VENTILACAO-020

## Notes

aspecto_do_curativo flogistic-signs enum is reused in every invasive-device group (the device-management form was misrouted out of this cluster - see dropped RULE-devices-FE-01-047).

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
