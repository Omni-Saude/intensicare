# ADR-0033: Pathway View como Componente Genérico Data-Driven

**Status:** proposed  
**Data:** 2026-07-09  
**Decisão por:** Niemeyer (System Architect)  

---

## Contexto

O Pathway View (`/patient/[mpi_id]/pathway/[pathway_id]`) é o componente central do novo frontend. Ele precisa renderizar **qualquer uma das 9 trilhas clínicas**, cada uma com seu próprio conjunto de critérios, estados, e recomendações — definidos em YAML no backend.

A abordagem ingênua seria criar um componente específico para cada trilha (ex: `SepsisPathwayView`, `RenalPathwayView`). Isso seria essencialmente o mesmo erro do frontend v2 (1 domínio = 1 página), apenas renomeado.

Precisamos de uma abordagem que:
1. Funcione para as 9 trilhas atuais
2. Funcione para futuras trilhas sem código novo
3. Respeite as diferenças entre trilhas (nº de critérios, tipos de predicate, estrutura de estados)

## Decisão

**O Pathway View será implementado como um componente genérico data-driven, que renderiza exclusivamente a partir dos dados retornados pela API `GET /patients/{mpi_id}/pathways/{pp_id}/progress` e da definição YAML da trilha.**

Nenhum componente do Pathway View conterá lógica específica de uma trilha. Toda variação entre trilhas será tratada via:
1. **Dados da API** (`PathwayProgress`): estado atual, critérios avaliados, histórico, tendência
2. **Definição YAML** (`Pathway`): estados possíveis, critérios com thresholds, recomendações

### Arquitetura de Dados

```
PathwayView
  ├── recebe: { mpi_id, pathway_id }
  ├── busca:   GET /patients/{mpi_id}/pathways/{pathway_id}/progress → PathwayProgress
  ├── busca:   GET /pathways/{pathway.id} → Pathway (cache)
  │
  ├── PathwayStateMachine
  │   ├── entrada: Pathway.states[] + PathwayProgress.current_state
  │   ├── saída:   nós coloridos (atual=highlight, passado=checked, futuro=dimmed)
  │   └── genérico: funciona para N estados, qualquer nome
  │
  ├── CriteriaPanel
  │   ├── entrada: PathwayProgress.criteria[] (avaliados)
  │   ├── saída:   lista de critérios com severidade colorida
  │   └── genérico: funciona para qualquer predicate type (graded, boolean)
  │       └── CriteriaRow: adapta rendering baseado em criteria.met (bool) + criteria.severity (enum)
  │       └── CriteriaDetail (expansão): mostra criteria.value vs criteria.alert_threshold
  │
  ├── PathwayRecommendations
  │   ├── entrada: Pathway.evidence.recommendations[] (do YAML)
  │   ├── saída:   cards com recomendações da guideline
  │   └── genérico: extrai de evidence.recommendations (se existir)
  │
  └── PathwayHistory
      ├── entrada: PathwayProgress.state_history[]
      ├── saída:   timeline de transições
      └── genérico: funciona para qualquer número de transições
```

### Contrato de Dados (TypeScript)

```typescript
// Props de entrada (únicas props que o PathwayView recebe)
interface PathwayViewProps {
  mpiId: string;
  pathwayId: number;
}

// O componente NUNCA recebe props específicas da trilha.
// Toda variação vem dos dados da API.
```

## Alternativas Consideradas

### Alternativa A: Componente específico por trilha
- **Prós:** Renderização otimizada para cada contexto clínico
- **Contras:** 9 componentes para manter, nova trilha = novo componente, inconsistência entre trilhas
- **Rejeitada porque:** Viola o princípio DRY e repete o erro do v2

### Alternativa B: Componente genérico com slots configuráveis por trilha
- **Prós:** Flexibilidade para trilhas que precisam de visualização diferente
- **Contras:** Complexidade de configuração, dois níveis de abstração
- **Rejeitada porque:** As 9 trilhas atuais têm estrutura homogênea (critérios + estados + recomendações). Slots seriam overengineering. Se no futuro uma trilha precisar de visualização radicalmente diferente, reabrimos o ADR.

### Alternativa C: Server-side rendering das definições YAML → HTML
- **Prós:** Zero lógica no cliente
- **Contras:** Sem interatividade (expansão de critérios, transições animadas), latência em cada interação
- **Rejeitada porque:** O Pathway View precisa de interatividade (expandir critério, filtrar, navegar entre estados)

## Consequências

### Positivas
- 1 componente renderiza 9+ trilhas
- Nova trilha = zero código frontend (só YAML no backend)
- Consistência visual garantida entre trilhas
- Testável: mockar `PathwayProgress` e verificar renderização

### Negativas
- Se uma trilha futura tiver estrutura radicalmente diferente (ex: grafo de estados não-linear, critérios com sub-critérios), o componente genérico pode não ser suficiente
- O componente precisa tratar graceful degradation para campos opcionais (ex: `recommendation` pode ser null)

### Riscos e Mitigações
- **Risco:** YAMLs têm estruturas inconsistentes → **Mitigação:** Analisar todos os 12 YAMLs durante M3 para garantir cobertura
- **Risco:** `PathwayStateMachine` visual não funciona para trilhas com muitos estados (ex: 7+) → **Mitigação:** Fallback para lista vertical se >6 estados
- **Risco:** Performance com muitos critérios (>15) → **Mitigação:** Virtualização da lista se necessário (improvável: maior trilha tem 7)

---

## Referências

- `_work/alerts/pathways/*.yaml` (12 definições)
- pathways-openapi.yaml § `PathwayProgress`, `Pathway`, `PathwayState`, `PathwayCriteria`
- FRONTEND_REBUILD_PLAN.md § 3.1 (Árvore de Componentes), § 5.4 (FASE 3)
- ADR-0030 (pathway-centric architecture)
- ADR-0031 (sepse como benchmark)
