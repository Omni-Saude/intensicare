# RULE-TENANCY-ORGANIZACAO-038 — Sector clinical indicator aggregation across care pathways (indicadores action)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | decision-tree |
| Status | OK |
| Verification | UNVERIFIABLE |
| Confidence | medium |
| Cluster | tenancy-organizacao |

## Rule
SetorViewSet.indicadores computes VERMELHO/AMARELO alert counts and how many are 'assistido' (attended), summed across every trilha (care-pathway) type applicable to the sector's tipo. For 'homecare' sectors it uses Leito.get_trilhas_homecare(); for 'automatica' it uses Leito.get_trilhas_automaticas(); 'manual' sectors are explicitly unsupported and raise a ValidationError. Per-pathway row selection differs: homecare picks the single MOST RECENT record (max criado_em) per patient/atendimento (DISTINCT ON pattern); automatica assumes the pathway model's primary key IS the nr_atendimento value itself (no separate lookup needed).

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| setor.tipo | string enum (manual\|automatica\|homecare) |  |  |
| setor.leitos (ocupado=True) | queryset of Leito |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| vermelhos_assistidos | integer |  |
| amarelos_assistidos | integer |  |
| amarelos | integer |  |
| vermelhos | integer |  |

## Logic
```text
nrs_atendimentos = setor.leitos.filter(ocupado=True).values_list("nr_atendimento", flat=True)
if setor.tipo == "homecare":
    trilhas = Leito.get_trilhas_homecare()
elif setor.tipo == "automatica":
    trilhas = Leito.get_trilhas_automaticas()
else:
    raise ValidationError("Indicadores da manuais ainda não foi configurado!")

totals = {vermelhos_assistidos:0, amarelos_assistidos:0, amarelos:0, vermelhos:0}
for trilha_model in trilhas:
    if setor.tipo == "homecare":
        # one row per atendimento: the most recently created (max criado_em)
        ids = trilha_model.objects.filter(nr_atendimento__in=nrs_atendimentos) \
                  .order_by("nr_atendimento", "-criado_em") \
                  .distinct("nr_atendimento").values_list("id")
    else:  # automatica
        ids = nrs_atendimentos    # ASSUMPTION: trilha pk == nr_atendimento for automatica pathway tables
    rows = trilha_model.objects.filter(pk__in=ids).annotate(
        assistido_por_vermelho=Case(When(assistido=True, alerta="VERMELHO", then=1), default=0),
        assistido_por_amarelo=Case(When(alerta="AMARELO", assistido=True, then=1), default=0),
        amarelo=Case(When(alerta="AMARELO", then=1), default=0),
        vermelho=Case(When(alerta="VERMELHO", then=1), default=0),
    ).aggregate(
        vermelhos_assistidos=Sum("assistido_por_vermelho"), amarelos_assistidos=Sum("assistido_por_amarelo"),
        amarelos=Sum("amarelo"), vermelhos=Sum("vermelho"))
    totals["vermelhos_assistidos"] += rows.get("vermelhos_assistidos", 0)
    totals["amarelos_assistidos"] += rows.get("amarelos_assistidos", 0)
    totals["amarelos"] += rows.get("amarelos", 0)
    totals["vermelhos"] += rows.get("vermelhos", 0)
```

## Edge cases (as implemented)
Sum() over an empty/None-only queryset would yield None, not 0, but the code uses .get(key, 0) as a default only for a MISSING dict key, not for a None value actually present - if the aggregate returns {'vermelhos_assistidos': None, ...}, 'totals[...] += None' would raise TypeError. This is a latent null-handling risk when a given trilha type has zero matching rows for the sector's atendimentos.

## Verification
- Verdict: UNVERIFIABLE
- Reference: None. SetorViewSet.indicadores is a proprietary data-aggregation routine that counts internal VERMELHO/AMARELO alert flags (the `alerta` and `assistido` fields already stored on each trilha/care-pathway model) across every pathway type applicable to the sector, scoped to occupied beds. The VERMELHO/AMARELO alert bands are internal to the trilhas product; their derivation is outside this rule, and no published clinical guideline or MDCalc-documented calculator defines how to sum red/yellow attended-alert counts across pathway tables. Not a clinical equation despite the 'clinical-scoring' category tag.
- Test vectors:
  - inputs: {'setor.tipo': 'manual'}; expected_reference: n/a - no authoritative source; actual_legacy: raises ValidationError('Indicadores da manuais ainda nao foi configurado!') - manual sectors explicitly unsupported; match: True
  - inputs: {'setor.tipo': 'homecare', 'occupied_bed_atendimento': 'X', 'trilha_rows_for_X': '[{criado_em: t1, alerta: AMARELO, assistido: false}, {criado_em: t2>t1, alerta: VERMELHO, assistido: true}]'}; expected_reference: n/a - no authoritative source; actual_legacy: DISTINCT ON (nr_atendimento) ORDER BY -criado_em selects only the most-recent row (t2: VERMELHO, assistido). Aggregate -> vermelhos=1, vermelhos_assistidos=1, amarelos=0, amarelos_assistidos=0. The older AMARELO row is not counted.; match: True
  - inputs: {'setor.tipo': 'automatica', 'trilha_type_with_zero_matching_rows': True}; expected_reference: n/a - no authoritative source; actual_legacy: ids_trilhas = nrs_atendimentos (assumes trilha pk == nr_atendimento). When a pathway table has zero matching rows, Sum() returns {vermelhos_assistidos: None, ...}; payload[...] += None raises TypeError (latent null-handling defect noted in edge_cases). Verified as a direct reading of the code, not a reference discrepancy.; match: True
- Internal/proprietary multi-tenancy aggregation logic; flag for internal review. No published clinical reference exists. The 'clinical-scoring' category is a misnomer here - this counts pre-existing alert flags rather than computing any clinical score. Latent TypeError null-handling risk (empty-queryset Sum returns None) and the unconfirmed automatica 'pk == nr_atendimento' assumption are internal-correctness concerns for engineering review, independent of any clinical reference.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/setor.py | 63-143 | 8166c07e | primary |

- Merged from: RULE-setor-BE-05-015
- Related rules: RULE-TENANCY-ORGANIZACAO-016, RULE-TENANCY-ORGANIZACAO-015, RULE-TENANCY-ORGANIZACAO-041, RULE-TENANCY-ORGANIZACAO-042

## Notes
The pk==nr_atendimento assumption for automatica pathway models cannot be independently confirmed from this partition (models live in trilha_automatica, out of scope) but is a direct, unambiguous reading of `ids_trilhas = nrs_atendimentos; trilha.objects.filter(pk__in=ids_trilhas)`.

---

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
