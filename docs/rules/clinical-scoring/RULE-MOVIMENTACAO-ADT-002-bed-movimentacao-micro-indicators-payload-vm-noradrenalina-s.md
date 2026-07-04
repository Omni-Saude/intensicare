# RULE-MOVIMENTACAO-ADT-002 — Bed/movimentacao micro-indicators payload (VM / noradrenalina / sedacao / LOS)

| Field | Value |
|---|---|
| Category | clinical-scoring |
| Type | formula |
| Status | DISCREPANCY |
| Verification | UNVERIFIABLE |
| Confidence | high |
| Cluster | movimentacao-adt |

## Rule
The bed/movimentacao payload surfaces a micro_indicadores object of ICU markers. Backend (manual movimentacao get_payload) emits four: length of stay, mechanical ventilation, noradrenaline (vasopressor), and sedation presence. The frontend MicroIndicadores TypeScript type declares SIX fields (adds hemodialise and mortalidade_esperada), so the two implementations do not agree on the object shape.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| dados_prontuario | DadosProntuario |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| micro_indicadores | dict |  |

## Logic
```text
# BACKEND (core/models/movimentacao.py, manual movimentacao get_payload):
vm       = dados_prontuario.verificar_uso_ventilacao_mecanica
dva      = dados_prontuario.verificar_uso_noradrenalina
sedacao  = dados_prontuario.verificar_existencia_sedativos
payload.micro_indicadores = {
  "tempo_internacao": tempo_permanencia,
  "ventilacao_mecanica": vm,
  "noradrenalina": dva,
  "sedacao": sedacao,
}
alerta_movimentacao default "NEUTRO" (max_length 8); atual default True.

# FRONTEND (src/@types/models/Ocupacao.d.ts:47-54):
interface MicroIndicadores {
  noradrenalina: boolean;
  sedacao: boolean;
  tempo_internacao: number;
  ventilacao_mecanica: boolean;
  hemodialise: boolean;          # NOT emitted by backend manual payload
  mortalidade_esperada: number;  # NOT emitted by backend manual payload (see RULE-003)
}
```

## Edge cases (as implemented)
The verificar_* implementations live in trilha_manual.models.DadosProntuario (out of partition). dva = droga vasoativa (noradrenaline as vasopressor marker).

## Divergence
Object-shape divergence between backend and frontend copies of micro_indicadores. Backend manual movimentacao get_payload() (core/models/movimentacao.py:127-133, verified) emits exactly {tempo_internacao, ventilacao_mecanica, noradrenalina, sedacao}. Frontend Models.Ocupacao.MicroIndicadores (Ocupacao.d.ts:47-54, verified) additionally declares hemodialise:boolean and mortalidade_esperada:number, which the backend manual path never populates. Likely source: the automatica/homecare micro_indicadores path (utils.micro_indicadores via RULE-005 lookup, out of partition) may supply the extra fields; the frontend uses one union type for all bed types. Recorded as a real BE/FE field-set mismatch, not corrected.

## Verification
- Verdict: UNVERIFIABLE
- Reference: Backend/frontend object-shape contract for the micro_indicadores payload - an internal API data-contract, not a clinical calculation with a published reference. Its markers (VM, noradrenaline, sedation, LOS) are presence flags / scalars, not scored against a guideline.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/models/movimentacao.py | 77-143 | 8166c07e | primary |
| trilhas-frontend | src/@types/models/Ocupacao.d.ts | 47-54 | f9656be2 | frontend-copy |
- Merged from: RULE-movimentacao-BE-04-026, RULE-ocupacao-FE-07-004
- Related rules: RULE-MOVIMENTACAO-ADT-001, RULE-MOVIMENTACAO-ADT-003, RULE-MOVIMENTACAO-ADT-004, RULE-MOVIMENTACAO-ADT-005

## Notes
Both individual captures were status OK in Phase 1; the DISCREPANCY (and new divergence) was found during BE/FE reconciliation. mortalidade_esperada is split into RULE-003.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
