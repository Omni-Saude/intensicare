# RULE-MOVIMENTACAO-ADT-034 — New movimentacao - carry-forward of clinical data from previous

| Field | Value |
|---|---|
| Category | care-pathway |
| Type | workflow |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | medium |
| Cluster | movimentacao-adt |

## Rule
Creating a subsequent movimentacao deactivates the prior one and clones its prontuario and clinical sub-records (noradrenalina, PCR, ventilacao, sedativos, SOFA), applying any newly supplied values, then regenerates pathways. Test-asserted: omitted sub-collections (e.g. sedativos) inherit from the previous movimentacao; provided sub-collections fully replace (not merge); the new movimentacao links to its predecessor via ultima_movimentacao.

## Inputs

| Name | Type | Unit | Range |
|---|---|---|---|
| dados_prontuario | dict incl. ultima_movimentacao, movimentacao, noradrenalina, parada_cardiorrespiratoria, sedativos, ventilacao_mecanica |  |  |

## Outputs

| Name | Type | Unit |
|---|---|---|
| new DadosProntuario + sub-records + trilhas | side-effect |  |

## Logic
```text
order: get_atributos -> get_ultima_movimentacao(404) -> get_movimentacao(404)
  -> desativar_ultima_movimentacao (ultima.atual=False)
  -> gerar_novo_dado_prontuario: clone DadosProntuario(pk of ultima_movimentacao.id) with id/pk=None,
       movimentacao=new, save; then apply new data via DadosProntuarioSerializer(instance=clone)
  -> for noradrenalina/parada/ventilacao: if new==empty dict skip; else clone prior tuple
       (trocar_prontuario_do_atributo) then update with new data if provided
  -> sedativos: if list provided create each; elif prior sedativos exist clone all
  -> gerar_novo_escore_sofa: clone prior SOFA, call sofa.atualizar_atributos_sofa(), save
  -> gerar_trilhas: CriarTrilhas(new prontuario)
  -> atualizar_alerta_movimentacao(new.movimentacao.pk)

# test-asserted (test_movimentacao.py:297-376):
# nova without sedativos -> new mov.sedativos == prior mov.sedativos (same count, quantidade, nome_sedativo)
# nova with sedativos=[{nome:"Sedativo Teste", quantidade:25}] -> new mov.sedativos == exactly that (len 1)
# new mov.ultima_movimentacao == prior movimentacao
```

## Edge cases (as implemented)
Cloning uses id=None/pk=None to force INSERT. gerar_novo_dado_prontuario fetches DadosProntuario by ultima_movimentacao.id (assumes shared pk with prontuario). Empty {} / [] payloads are treated as "no new data, keep clone". Provided sub-collections fully replace (not merge).

## Verification
- Verdict: NOT_APPLICABLE
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/use_cases/movimentacao/cadastrar_nova_movimentacao.py` | 47-231 | `8166c07e` | primary |
| ahlabs-trilhas | `core/tests/test_movimentacao.py` | 297-376 | `8166c07e` | duplicate |

- Merged from: RULE-movimentacao-BE-04-036, RULE-CAREPATH-BE-12-029
- Related rules: RULE-MOVIMENTACAO-ADT-035, RULE-MOVIMENTACAO-ADT-056, RULE-MOVIMENTACAO-ADT-039

## Notes
Serializers/models (trilha_manual) out of partition. SOFA regeneration re-runs the scoring via atualizar_atributos_sofa (out of partition). The ultima_movimentacao linkage assertion also relates to the viewset field-injection in RULE-035. Test capture (test_movimentacao.py:297-376) folded here as a duplicate of the carry-forward semantics.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
