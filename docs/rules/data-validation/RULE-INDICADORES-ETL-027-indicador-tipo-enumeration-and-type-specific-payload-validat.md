# RULE-INDICADORES-ETL-027 — Indicador tipo enumeration and type-specific payload validation (backend enum/dispatch vs frontend type)

| Field | Value |
|---|---|
| Category | data-validation |
| Type | validation |
| Status | DISCREPANCY |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | indicadores-etl |

## Rule
Backend defines two valid Indicador 'tipo' values (interacao_notificacao, entrada_videochamada) in IndicadorChoices.tipos(), enforced as the model field's choices; on save(), the model dispatches to a type-specific DRF serializer (InteracaoNotificacaoSerializer / EntradaVideochamadaSerializer) keyed on tipo to validate the JSON 'dados' payload before persisting. The frontend TypeScript model (Models.Indicador) only declares a single literal for Tipo ('entrada_videochamada') and a matching single-key Dados payload shape (setor_id) -- it has no type/shape at all for 'interacao_notificacao', even though the backend actively accepts, validates, and persists that tipo.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| tipo | string |  | interacao_notificacao\|entrada_videochamada |
| dados | json |  |  |
| Models.Indicador.Tipo (frontend) | string literal union |  | "entrada_videochamada" only -- interacao_notificacao is not represented |

## Outputs

| Name | Type | Unit |
|---|---|---|
| persisted_indicador | Indicador |  |
| Models.Indicador (frontend) | object |  |

## Logic
```text
# core/models/choices/indicador.py -- backend enum (RULE-indicador-BE-04-009)
IndicadorChoices.tipos() -> (
  ("interacao_notificacao", "Interação com notificaçãos"),
  ("entrada_videochamada", "Entrar em video chamada"),
)

# core/models/indicador.py -- backend save-time dispatch (RULE-indicador-BE-04-018)
class Indicador(SetUpModel):
    tipo = models.CharField(max_length=64, choices=IndicadorChoices.tipos())
    dados = models.JSONField(blank=True, default=dict)

    def save(self, *args, **kwargs):
        switch_validators = {
            "interacao_notificacao": serializers.InteracaoNotificacaoSerializer,
            "entrada_videochamada": serializers.EntradaVideochamadaSerializer,
        }
        dados = self.dados.copy()
        serializer = switch_validators.get(self.tipo)
        serializer = serializer(data=dados)
        serializer.is_valid(raise_exception=True)
        super(Indicador, self).save(*args, **kwargs)

# src/@types/models/Indicadores.d.ts -- frontend type (RULE-indicador-FE-07-001)
namespace Models {
  interface Indicador {
    tipo: Models.Indicador.Tipo
    dados: Models.Indicador.Dados[Models.Indicador.Tipo]
  }
  namespace Indicador {
    type Tipo = "entrada_videochamada"                 // only ONE of the two backend tipos
    interface Dados { entrada_videochamada: { setor_id: string } }
  }
}
```

## Edge cases (as implemented)
Backend: if tipo is not one of the two choices, switch_validators.get(self.tipo) returns None and None(data=dados) raises an unhandled TypeError at save() time (dados defaults to {}). Frontend: because Models.Indicador.Dados is keyed only by the single Tipo literal, the TypeScript type system cannot express or type-check an 'interacao_notificacao' indicator payload at all -- any frontend code path that tried to POST that tipo would have to bypass/assert past the type system. Verified directly against both legacy repos at the cited commits: choices/indicador.py lines 1-7, models/indicador.py lines 1-27, and Indicadores.d.ts lines 1-17.

## Divergence
Backend enumerates and actively validates TWO Indicador tipos (interacao_notificacao, entrada_videochamada), each with its own DRF serializer. The frontend TypeScript model only declares ONE literal ('entrada_videochamada') for Tipo and only one corresponding Dados payload shape -- 'interacao_notificacao' is entirely absent from the frontend type surface, even though nothing on the backend prevents that tipo from being created and validated. This was not flagged as a discrepancy by either originating Phase-1 capture (both individually recorded status OK); found only by directly comparing the backend choices/dispatch against the frontend type union.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/models/indicador.py` | 15-24 | `8166c07e` | primary |
| ahlabs-trilhas | `core/models/choices/indicador.py` | 1-7 | `8166c07e` | duplicate |
| trilhas-frontend | `src/@types/models/Indicadores.d.ts` | 1-17 | `f9656be2` | frontend-copy |

- Merged from: RULE-indicador-BE-04-009, RULE-indicador-BE-04-018, RULE-indicador-FE-07-001
- Related rules: RULE-INDICADORES-ETL-020, RULE-INDICADORES-ETL-021

## Notes
Merge of three Phase-1 captures of the same underlying rule: RULE-indicador-BE-04-009 captured the choices/enum declaration (category billing-administrative), RULE-indicador-BE-04-018 captured the model's save()-time validator dispatch that consumes the same enum (category data-validation, kept as primary logic since it is the most precise/reimplementable capture -- it names the exact serializer classes), and RULE-indicador-FE-07-001 captured the frontend TypeScript mirror of the same tipo/dados contract (category scheduling-operational). All three describe the same logical rule (valid Indicador tipos and their payload shapes) from three different code artifacts. See also RULE-INDICADORES-ETL-020/021 (the ViewSet actions that construct Indicador instances consumed by this save() dispatch).

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
