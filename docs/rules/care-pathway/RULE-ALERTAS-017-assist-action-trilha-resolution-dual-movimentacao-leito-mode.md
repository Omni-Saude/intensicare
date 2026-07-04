# RULE-ALERTAS-017 — Assist-action trilha resolution: dual Movimentacao/Leito mode with per-tipo selection strategy

| Field | Value |
|---|---|
| Cluster | alertas |
| Category | care-pathway |
| Type | decision-tree |
| Status | OK |
| Confidence | high |
| Verification verdict | NOT_APPLICABLE |
| Clinical impact |  |

## Rule
AssistidoViewSet.create resolves the target trilha record via the overloaded 'ocupacoes__pk' URL kwarg: first tries to interpret it as a Movimentacao pk (manual bed) and looks up the manual trilha model matching dados_prontuario=str(movimentacao.pk) via .get() (assumes exactly one match); if no such Movimentacao exists, falls back to treating the kwarg as a Leito pk - for 'automatica' beds it fetches the trilha .get() by nr_atendimento (assumes uniqueness); for other (homecare) beds it fetches ALL matching records ordered by criado_em ascending and takes .last() (most recently created).

## Inputs

- kwargs.ocupacoes__pk (uuid)
- request.data.tipo (string)
- request.data.id (uuid)

## Outputs

- trilha (object)

## Logic

```text
try:
    movimentacao = Movimentacao.objects.get(pk=kwargs["ocupacoes__pk"])
    Model = mapeamento_trilhas["manual"][tipo_trilha]
    trilha = Model.objects.get(dados_prontuario=str(movimentacao.pk))
    leito, paciente = movimentacao.leito, movimentacao.paciente
except Movimentacao.DoesNotExist:
    leito = get_object_or_404(Leito, pk=kwargs["ocupacoes__pk"])
    paciente = leito.paciente
    if leito.tipo == "automatica":
        Model = mapeamento_trilhas["automatica"][tipo_trilha]
        trilha = Model.objects.get(nr_atendimento=leito.nr_atendimento)
    else:
        Model = mapeamento_trilhas["homecare"][tipo_trilha]
        trilha = Model.objects.filter(nr_atendimento=leito.nr_atendimento).order_by("criado_em").last()
save_assistido(Model, trilha_pk=request.data["id"], request=request)
```

## Edge cases (as implemented)

The 'automatica' branch's .get() raises MultipleObjectsReturned if more than one trilha record shares the same nr_atendimento for that pathway type (uniqueness assumed, not enforced/handled). The 'manual' branch's .get() similarly assumes exactly one trilha per dados_prontuario reference.

## Sources

| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | `core/api/v1/views/assistido.py` | 107-137 | `8166c07eae` | primary |

## Provenance

**Merged from** (legacy pre-reconciliation rule ids):

- `RULE-assistido-BE-05-003`

**Related rules:**

- [RULE-ALERTAS-021](RULE-ALERTAS-021-trilha-care-pathway-model-mapping-per-bed-type-with-v3-model.md)
- [RULE-ALERTAS-022](RULE-ALERTAS-022-marking-a-trilha-as-assistido-bulk-update-for-v3-models-inst.md)
- [RULE-ALERTAS-023](RULE-ALERTAS-023-assistidopor-audit-snapshot-created-only-when-marking-as-ass.md)

## Notes

Same 'ocupacoes__pk means Movimentacao-or-Leito' overload pattern as RULE-observacao-BE-05-007 (other cluster). permission_trilhas=('can_assist_ocupacao',), exceto_metodo='POST' - i.e., create itself DOES require the permission (opposite of the GET-exempted pattern on other viewsets).

---

*Audited snapshots: `ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f`, `trilhas-frontend@f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`. Audit date 2026-07-03.*
