# ADR-0030: Arquitetura de Frontend Orientada a Trilhas (Pathway-Centric)

**Status:** proposed  
**Data:** 2026-07-09  
**Decisão por:** Niemeyer (System Architect)  
**Stakeholders:** Product-Design-Orchestrator, Parreira, Rodrigo Aquino  

---

## Contexto

O frontend v2 foi construído com o modelo mental `1 domínio clínico = 1 página independente`, resultando em 33 páginas onde 17 são domínios standalone (desconexos). O intensivista precisa navegar entre múltiplas páginas para entender o estado de um único paciente — o oposto de um centro de comando clínico.

O backend tem a arquitetura correta: **trilhas clínicas (care pathways)** → motor de avaliação → scores → alertas. As trilhas são a unidade organizadora natural porque:
1. Agrupam critérios, scores e alertas em torno de um **tema clínico** (ex: sepse, renal)
2. Guiam o cuidado proativo (cada trilha tem estados, recomendações, guidelines)
3. São a camada de mais alto valor clínico — o intensivista pensa em termos de "este paciente está na trilha de sepse, em tratamento ativo, com PAM crítica"

## Decisão

**O frontend v3 será reconstruído com arquitetura orientada a trilhas (pathway-centric).**

- A trilha (pathway) é a unidade organizadora central da experiência
- 6 páginas core substituem as 33 atuais: Dashboard, Patient Detail, Pathway View, Alert Triage, Care Pathways Catalog, Admin
- Zero páginas standalone de domínio clínico
- Componentes genéricos (`PathwayStateMachine`, `CriteriaPanel`, `PathwayRecommendations`) renderizam qualquer trilha a partir da definição YAML

## Alternativas Consideradas

### Alternativa A: Refatorar o v2 incrementalmente
- **Prós:** Menor investimento inicial, sem risco de regressão em funcionalidades existentes
- **Contras:** O modelo mental errado está enraizado na estrutura de rotas e componentes. Refatorar 17 páginas para um modelo diferente exigiria reescrever a camada de roteamento e estado — essencialmente o mesmo esforço de um rebuild, com o custo adicional de carregar dívida técnica
- **Rejeitada porque:** O custo de refatoração incremental é comparável ao rebuild, mas o resultado seria inferior

### Alternativa B: Manter páginas de domínio + adicionar camada de trilhas
- **Prós:** Aproveita investimento existente, adiciona a funcionalidade de trilhas como "feature"
- **Contras:** Duas fontes de verdade (página standalone vs trilha). Intensivista continua tendo que navegar entre dois modelos mentais. Complexidade de manter 33 páginas + novas páginas de trilha
- **Rejeitada porque:** Viola o princípio de simplicidade. Duas formas de ver a mesma informação clínica = confusão

### Alternativa C: Single Page Application com tudo em uma tela
- **Prós:** Máxima densidade de informação
- **Contras:** Sobrecarga cognitiva, problemas de performance, difícil de manter, não funciona em mobile
- **Rejeitada porque:** A separação em 6 páginas com navegação hierárquica (Dashboard → Patient → Pathway) oferece o equilíbrio certo entre densidade e foco

## Consequências

### Positivas
- Intensivista vê todas as trilhas de um paciente em uma única tela (Patient Detail)
- Navegação Dashboard → Patient → Pathway em 2 cliques
- Componentes genéricos = nova trilha não requer novo desenvolvimento de UI
- Arquitetura alinhada com o backend (spec canônica)

### Negativas
- Rebuild do zero requer 28 dias de desenvolvimento
- Migração de componentes reutilizáveis do v2 requer cuidado (extrair, não reescrever)
- Risco de perda de funcionalidades periféricas durante a transição

### Riscos e Mitigações
- **Risco:** Endpoints de pathways não estão implementados no backend → **Mitigação:** Validar antes do M0
- **Risco:** State machine visual complexa → **Mitigação:** Versão 1 é lista de estados com highlight; visual é stretch
- **Risco:** Resistência dos intensivistas à mudança de interface → **Mitigação:** Envolver médico no approval gate G1 (após M3)

---

## Referências

- FRONTEND_REBUILD_HANDOFF.md (Parreira, 2026-07-09)
- pathways-openapi.yaml (docs/contracts/)
- `_work/alerts/pathways/sepse.yaml` (trilha benchmark)
- Frontend v2 audit (forensics, 2026-07-09): 34/100 integration score
