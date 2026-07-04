# RULE-DOCUMENTACAO-FATURAMENTO-002 — Glosa-Zero automatic alert engine — 16-criteria billing/documentation-compliance catalog, dual (and divergent) alert computation

| Field | Value |
|---|---|
| Category | billing-administrative |
| Type | decision-tree |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
TrilhaGlozaZeroModel (db_table AMH_TM_SINTETICO_09_V, verbose_name "Trilha Auditoria" / "Auditoria") is the automatic "Glosa Zero" billing-integrity pathway: 16 boolean criterio_1..criterio_16 flags, each with a fixed alert label + recommendation text (payload_trilha_glosa_zero, re-exported as payload_glosa_zero_automatica), covering late medication checks, missing/late signatures, physician-note timing, VM humidifier-filter compliance, antimicrobial-parecer requirements, and dispensed-not-prescribed items. The SAME model exposes TWO independently computed alert classifications from this criteria set, and they disagree (see divergence).

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| criterio_1..criterio_16 | int flag (1) per criterion, 16 total |  |  |
| atraso na checagem de medicacao | float | hours |  |
| atraso na assinatura | float | hours |  |
| troca de filtro VM interval | float | hours |  |
| hora do dia (evolucao diurna) | float | hour-of-day |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| alerta | enum {VERMELHO, AMARELO, NEUTRO}, persisted field via calcular_alerta() |  |
| tipo_alerta | enum {VERMELHO, AMARELO, NEUTRO}, view-computed via generate_view_data() |  |
| criterios / recomendacoes | list of {nome, alerta, recomendacoes} for triggered criteria (get_detalhe) |  |

## Logic
```text
# --- (A) 16-criteria catalog (core/facade/trilha_glosa_zero.py:1-101, payload_trilha_glosa_zero,
#     re-exported unchanged as trilha_automatica/facade/glosa_zero.py:payload_glosa_zero_automatica) ---
criterio_1  checagem de medicacao atrasada > 1h -> verificar cancelamento ou administrar/registrar.
criterio_2  checagem de medicacao atrasada > 2h -> administrar de imediato e registrar.
criterio_3  ausencia de assinatura do registro > 1h E < 6h apos liberacao -> assinar digitalmente.
criterio_4  troca do filtro umidificador da VM com < 72h sem justificativa (formulario TASY).
criterio_5  ausencia de evolucao medica diurna ate 14h -> realizar antes do fim do plantao de 12h.
criterio_6  ausencia de evolucao medica noturna do periodo anterior -> comunicar coordenador.
criterio_7  filtro umidificador de VM usado sem indicacao -> registrar inicio de VM.
criterio_8  ausencia de assinatura -> relogar, digitar PIN, liberar.
criterio_9  ausencia de assinatura (plantao anterior) -> envolver coordenacao.
criterio_10/11 inicio de antimicrobiano sem parecer de infectologista -> registrar/parecer.
criterio_12 ausencia de parecer apos solicitacao ao inicio do ciclo de antimicrobiano
            (especialmente > 7 dias de duracao).
criterio_13 ausencia de evolucao medica diurna (matutino) -> realizar/envolver coordenacao.
criterio_14 ausencia de evolucao medica noturna -> realizar/envolver coordenacao.
criterio_15 ausencia de evolucao do medico intensivista (diaria) -> realizar/envolver coordenacao.
criterio_16 material/medicamento dispensado e nao prescrito -> realizar prescricao do item.

# --- (B) PRIMARY predicate code: persisted `alerta` field
#     (trilha_automatica/models/trilha9.py:128-146, called from save() at line ~106-110) ---
def calcular_alerta():
    escores = {
        "vermelho": [],                                            # ALWAYS EMPTY
        "amarelo": [criterio_1, criterio_3, criterio_5, criterio_6],  # only 4 of the 16 criteria
    }
    vermelho = escores["vermelho"].count(1)   # always 0
    amarelo  = escores["amarelo"].count(1)
    if vermelho:      return "VERMELHO"       # unreachable (0 is falsy)
    elif amarelo:     return "AMARELO"        # any of criterio_1/3/5/6 truthy(1)
    else:             return "NEUTRO"
# get_detalhe() (lines 175-184) only ever surfaces criteria [1,3,5,6] text/recommendations in "criterios".

# --- (C) SECOND, independent predicate: view-computed `tipo_alerta`
#     (trilha_automatica/models/trilha9.py:120-126 generate_view_data();
#      trilha_automatica/utils.py:75-81 define_tipo_alerta) ---
_CRITERIOS_ALERTA = {"amarelo": 2, "vermelho": 3}          # class attribute on TrilhaGlozaZeroModel
def conta_criterios_automatica():
    return count(criterio_i for i in 1..16 if criterio_i truthy)   # ALL 16 criteria, not just 1/3/5/6
def define_tipo_alerta(total_alertas, criterios):
    if total_alertas >= criterios["vermelho"]:        return "VERMELHO"   # >=3 of 16 criteria true
    elif 0 < total_alertas <= criterios["amarelo"]:    return "AMARELO"   # 1-2 of 16 criteria true
    else:                                              return "NEUTRO"
tipo_alerta = define_tipo_alerta(conta_criterios_automatica(), _CRITERIOS_ALERTA)
```

## Edge cases (as implemented)
Timing cutoffs (from catalog text): med check >1h (c1) / >2h (c2); signature window >1h AND <6h (c3); VM filter change <72h flagged (c4); daytime physician note deadline 14h / within 12h shift (c5); antimicrobial-parecer emphasis when duration >7 days (c12). Criteria 1&2 form a graded med-check delay escalation; 3,8,9 and 5,6,13,14,15 are documentation-signature/evolution duplicates (same underlying event, different wording/severity). `alerta` uses truthiness of list counts (not >= threshold) and its 'vermelho' list is permanently empty, so `alerta` can never be "VERMELHO" no matter which/how many criteria are true. `tipo_alerta` instead counts truthy values across ALL 16 criterio_* fields against class-level thresholds {amarelo:2, vermelho:3} and CAN reach "VERMELHO". get_detalhe() hardcodes payload["inconsistencia"] = True unconditionally.

## Divergence
The same TrilhaGlozaZeroModel record exposes two independently-computed, disagreeing alert classifications for the identical set of 16 criteria: (1) the PERSISTED `alerta` field (calcular_alerta(), run on every save()) only inspects criterio_1/3/5/6 and has a permanently-empty 'vermelho' bucket, so it can be at most "AMARELO" (if any of those 4 flags is set) and can NEVER be "VERMELHO", regardless of how many of the other 12 criteria (2,4,7,8,9,10-16) are also true. (2) The VIEW-COMPUTED `tipo_alerta` (generate_view_data() -> define_tipo_alerta) counts truthy values across ALL 16 criterio_* fields against the model's own _CRITERIOS_ALERTA thresholds ({"amarelo": 2, "vermelho": 3}) and DOES reach "VERMELHO" once 3+ of the 16 criteria are true. A record with, say, criterio_2, criterio_4 and criterio_16 all true (0 of the 1/3/5/6 subset) would show alerta="NEUTRO" but tipo_alerta="VERMELHO" for the exact same underlying data — originally flagged (RULE-auditoria-BE-03-020) only as "VERMELHO unreachable for `alerta`"; reconciliation against the same file's generate_view_data()/define_tipo_alerta() surfaced the second, disagreeing computation as an additional, previously-uncaptured divergence.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | trilha_automatica/models/trilha9.py | 128-146, 175-184 | 8166c07e | primary |
| ahlabs-trilhas | core/facade/trilha_glosa_zero.py | 1-101 | 8166c07e | duplicate |
| ahlabs-trilhas | trilha_automatica/facade/glosa_zero.py | 1-4 | 8166c07e | duplicate |
| ahlabs-trilhas | trilha_automatica/utils.py | 75-81 | 8166c07e | duplicate |
- Merged from: RULE-auditoria-BE-03-020, RULE-glosa-BE-01-020
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-010, RULE-DOCUMENTACAO-FATURAMENTO-007, RULE-DOCUMENTACAO-FATURAMENTO-008, RULE-DOCUMENTACAO-FATURAMENTO-009, RULE-DOCUMENTACAO-FATURAMENTO-024, RULE-DOCUMENTACAO-FATURAMENTO-025, RULE-DOCUMENTACAO-FATURAMENTO-015

## Notes
criteria 1&2 form a graded med-check delay escalation; 3,8,9 and 5,6,13,14,15 are documentation-signature/evolution duplicates. Domain = auditoria/faturamento; verbose_name "Trilha Auditoria" refers to this billing/glosa-zero compliance pathway specifically, NOT the generic audit-log subsystem (compare RULE-audit-BE-02-007, misrouted to auditoria-logs). trilha_automatica/facade/glosa_zero.py:payload_glosa_zero_automatica is a pure re-export (`= payload_trilha_glosa_zero`) of the core/facade module, confirmed identical, not an independent copy.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
