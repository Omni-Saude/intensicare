# ADR-0031: Trilha Sepse como MVP e Benchmark para Replicação

**Status:** proposed  
**Data:** 2026-07-09  
**Decisão por:** Niemeyer (System Architect)  
**Supersedes:** —  
**Superseded by:** —  

> [Reconciliado em 2026-07-12] "9 trilhas" era a contagem no momento desta ADR;
> M7 adicionou 3 trilhas (antimicrobiano, desmame, estabilidade), totalizando
> **12 trilhas YAML** ativas hoje em `_work/alerts/pathways/`. Ver
> `docs/audit/fullspectrum/DIM_A_TRACEABILITY.md` §4.4.

---

## Contexto

O rebuild do frontend v3 introduz um novo componente central — o **Pathway View** — que precisa renderizar qualquer uma das 9 trilhas clínicas. Construir todas as 9 simultaneamente seria um erro: atrasaria o feedback, aumentaria o risco de retrabalho, e postergaria a validação clínica.

Precisamos de uma trilha que sirva como **MVP e benchmark**: a primeira a ser implementada, que define o padrão de componentes, e contra a qual as demais são validadas.

## Decisão

**A trilha de Sepse (`sepse.yaml`, v3.0.0) será o MVP e benchmark para o Pathway View.**

As 8 trilhas restantes replicarão o mesmo padrão de componentes, aproveitando a genericidade construída no M3.

## Critérios de Seleção

| Critério | Sepse | Renal | Resp | Vent | Equil | Nutr | Prof | Sed | Del |
|----------|-------|-------|------|------|-------|------|------|-----|-----|
| Nº de critérios | 7 | ~5 | ~4 | ~6 | ~5 | ~4 | ~4 | ~4 | ~3 |
| Tipos de predicate | graded+boolean | graded | graded | graded | graded | graded | boolean | graded | boolean |
| Nº de estados | 5 | 4 | 4 | 5 | 5 | 4 | 4 | 4 | 3 |
| Guideline documentada | ✅ SSC-2021 | ✅ KDIGO | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ CAM-ICU |
| Versão | 3.0.0 | — | — | — | — | — | — | — | — |
| Recomendações explícitas | ✅ 4 itens | — | — | — | — | — | — | — | — |
| Suppression config | ✅ | — | — | — | — | — | — | — | — |

A sepse é a trilha mais madura em todos os critérios: mais critérios, tipos de predicate mais diversos (graded com bands + boolean), guideline explícita com recomendações, suppression config. É o teste de stress ideal para os componentes genéricos.

## Alternativas Consideradas

### Alternativa A: Implementar todas as 9 trilhas juntas
- **Prós:** Entrega completa de uma vez
- **Contras:** Sem feedback intermediário, 9x o risco de retrabalho se o design de componente estiver errado
- **Rejeitada porque:** MVP primeiro, escala depois. Princípio fundamental de arquitetura.

### Alternativa B: Renal como MVP (mais simples)
- **Prós:** KDIGO é bem conhecido, endpoint pode ser mais estável
- **Contras:** Menos critérios, não cobre predicate booleano, não testa o componente completamente
- **Rejeitada porque:** Benchmark precisa estressar os componentes. Se funciona para sepse (7 critérios, 2 tipos de predicate), funciona para qualquer trilha.

### Alternativa C: Ventilação como MVP (mais complexa)
- **Prós:** Máquina de estados mais rica, critérios de desmame
- **Contras:** Endpoint está quebrado (500), complexidade pode atrasar o MVP
- **Rejeitada porque:** MVP não pode depender de endpoint quebrado.

## Consequências

### Positivas
- M3 entrega componentes genéricos validados contra a trilha mais complexa
- M7 (8 trilhas restantes) é puramente configuração — sem novos componentes
- Feedback clínico pode ser obtido mais cedo (G1 após M3)
- Tempo total reduzido: 4 dias (M3) + 6 dias (M7) = 10 dias vs potencialmente 20+ dias se cada trilha tivesse componentes específicos

### Negativas
- Se o endpoint de pathways da sepse estiver quebrado, o M3 é bloqueado
- A sepse é a trilha mais complexa — se o design de componentes for superdimensionado para ela, as trilhas mais simples podem parecer "vazias"

### Riscos e Mitigações
- **Risco:** `GET /patients/{mpi_id}/pathways/{pp_id}/progress` não retorna dados para sepse → **Mitigação:** Validar no M0, antes de começar M3
- **Risco:** Componentes superdimensionados → **Mitigação:** Design minimalista. Cada componente mostra o que o YAML define, nada mais.

---

## Referências

- `_work/alerts/pathways/sepse.yaml` (v3.0.0, SSC-2021)
- pathways-openapi.yaml § `PathwayProgress` schema
- FRONTEND_REBUILD_PLAN.md § 5.4 (FASE 3 — Pathway View MVP)
