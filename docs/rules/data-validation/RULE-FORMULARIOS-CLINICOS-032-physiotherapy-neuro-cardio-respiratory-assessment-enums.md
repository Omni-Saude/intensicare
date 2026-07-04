# RULE-FORMULARIOS-CLINICOS-032 — Physiotherapy neuro/cardio/respiratory assessment enums

| Field | Value |
|---|---|
| Cluster | formularios-clinicos |
| Category | data-validation |
| Type | validation |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
Physiotherapist neuro, cardiovascular and respiratory exam enums (adds peripheral-perfusion, ventilatory rhythm/pattern, adventitious sounds, cough efficacy).

## Inputs

| name | type | unit | range |
|---|---|---|---|
| avaliacao_respiratoria.* | enum[]/enum |  | see logic |

## Outputs

| name | type | unit |
|---|---|---|
| exam enums | object |  |

## Logic

```text
neuro: pupilas {isocoricas, miose, midriase}; orientacao {ativo, sonolento, torporoso, comatoso, reativo};
       emocional {calmo, agitado, agressivo, letargico, nsa}; abertura_ocular {espontanea, ao_comando, a_dor, nenhuma}
cardio: pressao_arterial {normotenso, hipotensao, hipertensao, instavel}; frequencia_cardiaca {normocardio, bradicardico, taquicardio};
        drogas_vasoativas(bool); perfusao_periferica multicheck {regular, irregular, hipocorado, icterico}
resp: ritmo_ventilatorio multicheck {repouso, eupneico, dispneico, bradipneico, taquipneico, pequenos_esforcos, medios_esforcos, grandes_esforcos};
      padrao_ventilatorio {apical, superficial, diafragmatico, misto}; murmurio_vesicular {presente, diminuido, abolido};
      local_murmurio_vesicular {base_direita, base_esquerda, abolido, bases, htxd, htxe, difusos};
      estados_respiracao multicheck {estertores_crepitantes, estertores_bolhosos, estridor, sibilos, ronco};
      secrecao_traqueal {pouca, media, grande, aspiracao_ausente}; aspecto {mucoide, purulenta, mucopurulenta, sanguinolenta};
      tosse {eficaz, nao_eficaz, ausente}; expansibilidade_pulmonar {simetrica, assimetrica};
      dreno_de_torax {esquerdo, direito, bilateral, ausente};
      aspecto_da_secrecao {espessa, purulenta, serosa, fluida_hialina, hematica, sendimentos};
      ausculta {murmurios_vesiculares, pulmoes_livres, roncos, sibilos, estertores}
```

## Edge cases (as implemented)

_None documented._

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| trilhas-frontend | `src/utils/dataForms/dataFormFisioterapeuta.ts` | 79-330 | `f9656be266` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-physio-FE-01-052`

**Related rules:**

- [RULE-FORMULARIOS-CLINICOS-005](../alert-threshold/RULE-FORMULARIOS-CLINICOS-005-nursing-cardiovascular-assessment-enums-with-capillary-refil.md)
- [RULE-FORMULARIOS-CLINICOS-031](RULE-FORMULARIOS-CLINICOS-031-nursing-neurological-assessment-enums.md)
- [RULE-FORMULARIOS-CLINICOS-033](RULE-FORMULARIOS-CLINICOS-033-physiotherapy-motor-function-enums.md)

## Notes

_None._

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
