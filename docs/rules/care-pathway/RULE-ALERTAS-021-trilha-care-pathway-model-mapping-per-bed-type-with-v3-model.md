# RULE-ALERTAS-021 — Trilha (care-pathway) model mapping per bed type, with v3 model migration

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
mapeamento_trilhas maps a (tipo_leito, tipo_trilha) pair to the concrete Django model used to store that pathway's data. The 'automatica' bed-type mapping shows an in-progress v3 migration: the active code uses TrilhaSepseV3Model for 'sepse' and TrilhaProfilaxiaV3Model for 'profilaxias', while the legacy TrilhaSEPSEModel and TrilhaProfilaxiasModel are commented out (not used) for the same keys.

## Inputs

- tipo_leito (automatica|manual|homecare)
- tipo_trilha (string)

## Outputs

- Model (Django model class)

## Logic

```text
mapeamento_trilhas = {
  "automatica": {
    "sedacao": TrilhaSedacaoV3Model, "estabilizacao": TrilhaEstabilidadeV3Model,
    "ventilacao": TrilhaVentilacaoModel,
    "sepse": TrilhaSepseV3Model,              # (commented alt: TrilhaSEPSEModel)
    "antimicrobiano": TrilhaAntimicrobianoModel, "nutricao": TrilhaNutricaoModel,
    "equilibrio": TrilhaEquilibrioModel,
    "profilaxias": TrilhaProfilaxiaV3Model,   # (commented alt: TrilhaProfilaxiasModel)
    "auditoria": TrilhaGlozaZeroModel, "eficiencia": TrilhaEficienciaV3Model,
  },
  "manual": {"sedacao": TrilhaSedacao, "ventilacao": TrilhaVentilacao,
             "sepse": TrilhaSepse, "estabilizacao": TrilhaEstabilidade},
  "homecare": {"piora_clinica": PioraClinica, "sepse": Sepse},
}
```

## Edge cases (as implemented)

Unrecognized tipo_trilha for a given bed type resolves to Model=None via .get(), which would raise AttributeError on subsequent Model.objects access if not validated earlier by TrilhasPermissaoMixin/serializer.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/assistido.py` | 39-64 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-assistido-BE-05-001`

**Related rules:**

- [RULE-ALERTAS-017](RULE-ALERTAS-017-assist-action-trilha-resolution-dual-movimentacao-leito-mode.md)
- [RULE-ALERTAS-022](RULE-ALERTAS-022-marking-a-trilha-as-assistido-bulk-update-for-v3-models-inst.md)

## Notes

This is the 'sepse vs sepse_v3' / 'profilaxias vs profilaxias_v3' version-variant the task calls out: the v3 models are the ACTIVE ones; the legacy models remain importable/referenced but unused (dead) in this mapping. Engine-adjacent but kept in alertas as foundational context for the assist/acknowledge workflow (RULE-ALERTAS-017/022/023).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
