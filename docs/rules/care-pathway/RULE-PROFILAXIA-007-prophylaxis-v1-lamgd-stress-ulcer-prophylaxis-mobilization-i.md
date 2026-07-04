# RULE-PROFILAXIA-007 — Prophylaxis v1 - LAMGD (stress-ulcer) prophylaxis, mobilization & invasive-device catalog

| Field | Value |
|---|---|
| Cluster | profilaxia |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
profilaxia v1 recommendation catalog for the non-dosing criteria: stress-ulcer (LAMGD) prophylaxis start/stop, early mobilization, insertion bundles, and device-dwell reassessment (criteria 1, 2, 3, 6, 9, 10, 11).

## Inputs

| name | type | unit |
|---|---|---|
| criterio flags 1/2/3/6/9/10/11 | bool |  |
| cateter vascular dwell time | float | days |

## Outputs

| name | type | unit |
|---|---|---|
| alerta + recomendacoes | string |  |

## Logic

```text
criterio_1 ausencia de profilaxia LAMGD -> IBP (esomeprazol VO/SNE, ou
           pantoprazol VO, ou omeprazol VO/SNE diluido em bicarbonato).
criterio_2 alto risco lesao gastrica sem profilaxia -> IBP (esomeprazol
           preferencialmente, ou pantoprazol, ou cimetidina EV, ou omeprazol VO/EV).
criterio_3 profilaxia LAMGD sem indicacao formal -> avaliar SUSPENDER
           (uso intrahospitalar aumenta pneumonia nosocomial e PAVM);
           dieta oral/enteral em pacientes estaveis dispensa a profilaxia.
criterio_6 indicacao de mobilizacao precoce -> deambular, sedestacao em
           poltrona, cicloergometro ativo, levar ao banheiro.
criterio_9 procedimento invasivo -> aplicar bundle do Protocolo Institucional
           de Prevencao de IRAs (presencial ou teleUTI).
criterio_10 avaliar retirada de cateter vascular implantado ha mais de 10 dias
           (avaliar integridade, sinais flogisticos, hemocultura 2 amostras);
           SVD sem sedoanalgesia continua -> preferir sondagem de alivio 4/4h-6/6h.
criterio_11 procedimento invasivo -> monitorar (enfermeira a distancia) e
           preencher bundles de insercao (corrente sanguinea, cateter urinario, PAVM).
```

## Edge cases (as implemented)

Device reassessment cutoff strictly > 10 days (criterio_10, "ha mais de 10 dias").

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/facade/trilha_profilaxia.py` | 1-22, 37-84 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-profilaxia-BE-01-007`

**Related rules:**

- [RULE-PROFILAXIA-008](RULE-PROFILAXIA-008-prophylaxis-v3-reduced-active-criteria-set-facade-lamgd-inse.md)
- [RULE-PROFILAXIA-003](../alert-threshold/RULE-PROFILAXIA-003-prophylaxis-v1-alert-aggregation-amarelo-vermelho-scoring.md)
- [RULE-PROFILAXIA-001](../drug-dosing/RULE-PROFILAXIA-001-prophylaxis-v1-hyperglycemia-subcutaneous-insulin-nph-slidin.md)
- [RULE-PROFILAXIA-002](../drug-dosing/RULE-PROFILAXIA-002-prophylaxis-v1-vte-anticoagulation-dosing-by-renal-function.md)
- [RULE-PROFILAXIA-005](RULE-PROFILAXIA-005-prophylaxis-v3-criterio-1-gi-stress-ulcer-lamgd-prophylaxis.md)
- [RULE-PROFILAXIA-006](RULE-PROFILAXIA-006-prophylaxis-v3-criterio-9-invasive-device-prescribed-vermelh.md)

## Notes

This is the v1 facade recommendation catalog (payload_trilha_profilaxia); = profilaxia_automatica. Criteria 4/5 (VTE dosing) are RULE-PROFILAXIA-002 and criteria 7/8 (insulin) are RULE-PROFILAXIA-001 (extracted separately by Phase 1). v1 variant of the reduced v3 facade RULE-PROFILAXIA-008.

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
