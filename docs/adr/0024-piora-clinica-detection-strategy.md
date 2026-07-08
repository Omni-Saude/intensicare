# ADR-024: Estratégia de Detecção de Piora Clínica — 13 regras com pontuação graduada

**Status:** Proposed
**Data:** 2026-07-07
**Area:** Agentes / Dados / Clinico
**Regulado:** parcial — a pontuação de deterioração sinaliza risco e NUNCA decide conduta clínica (L0-hard, ADR-0008); o outcome é sempre roteamento para avaliação humana.

## Contexto

A detecção precoce de piora clínica é uma das funções críticas dos agentes de acompanhamento de
pacientes (Helena e agentes de cuidado). O domínio exige:

- **13 regras de deterioração** cobrindo sinais vitais, resultados laboratoriais, e marcadores
  clínicos (ex.: variação de creatinina, queda de saturação O₂, alteração de nível de consciência,
  taquipneia, oligúria, etc).
- **Pontuação graduada** em 5 níveis por regra:
  - `0` — sem alteração relevante (estável);
  - `1+` — piora leve com sinal positivo (ex.: creatinina subiu levemente);
  - `1-` — melhora leve com sinal negativo (ex.: saturação O₂ subiu levemente);
  - `3+` — piora severa com sinal positivo (ex.: queda abrupta de saturação, oligúria franca);
  - `3-` — melhora significativa com sinal negativo (ex.: normalização de marcador).
- O **escore agregado** (soma ponderada das 13 regras) dispara níveis de alerta: escore baixo
  permanece em monitoramento; escore intermediário gera notificação ao time assistencial; escore
  alto escala para avaliação médica imediata.
- **Restrição L0-hard**: o sistema sinaliza e rotina — nunca decide conduta nem produz diagnóstico.
  A decisão clínica é exclusiva do profissional de saúde (ADR-0008, ADR-0005).

Há três abordagens arquiteturais para implementar essa detecção:

### Opção 1: Serviço standalone de detecção (PioraDetectionService)

Um microsserviço dedicado, desacoplado de qualquer outro runtime. Expõe endpoint REST/gRPC.
Consome eventos CDC do `amh-data-platform` (ADR-0013) — resultados de exames, sinais vitais,
evolução clínica. Mantém estado interno mínimo (janela de observação por paciente). Aplica as
13 regras e emite `PioraScoreCalculated` para um tópico Kafka.

**Prós:**
- Desacoplamento total: falha no alert engine ou no EWS runner não afeta a detecção.
- Deploy, escala e observabilidade independentes.
- Superfície de código reduzida e testável isoladamente.

**Contras:**
- +1 serviço para operar (build, deploy, monitorar, escalar).
- Duplica a lógica de consumo CDC (já existe em `fhir_sync` e potencialmente no alert engine).
- Latência adicional de rede entre a detecção e a ação (precisa publicar evento e aguardar consumo).

### Opção 2: Estender o alert engine existente (AlertEngine + regras de piora)

Adicionar as 13 regras de deterioração como um módulo dentro do alert engine já existente na
plataforma. O alert engine já consome eventos, mantém estado de janela, aplica condições e emite
alertas. As regras de piora seriam mais um "tipo de condição" no catálogo do engine.

**Prós:**
- Reuso de infraestrutura existente (consumo CDC, janelas, emissão de alertas).
- Single source of truth para todos os alertas clínicos (consolidado num só engine).
- Menor custo operacional (menos um serviço para manter).

**Contras:**
- Acoplamento: o engine de alertas genérico cresce para um domínio especializado (piora clínica).
  Risco de o engine virar um "big ball of mud" com regras de naturezas distintas (administrativas
  vs clínicas, urgência vs rotina).
- O alert engine pode ter SLAs diferentes dos exigidos para piora clínica (latência de detecção
  de piora severa exige near-real-time; alertas administrativos podem tolerar batch horário).
- Testabilidade: as 13 regras com pontuação graduada têm complexidade combinatorial que polui o
  plano de testes do engine genérico.

### Opção 3: Integrar ao runner de EWS/NRT (Early Warning System / Near Real-Time)

A detecção de piora é implementada como uma **stage function** dentro do pipeline de EWS/NRT que
já processa eventos de sinais vitais e resultados laboratoriais em tempo real. O runner invoca a
função de scoring como parte do fluxo normal de ingestão — o mesmo stream que alimenta o dashboard
de beira-leito também alimenta as 13 regras.

**Prós:**
- Latência mínima: a detecção acontece no mesmo fluxo de ingestão, sem hop adicional.
- Consistência: o dado que aparece no dashboard é o mesmo que alimenta as regras (single source).
- Custo de infraestrutura próximo de zero adicional (roda no mesmo runner).

**Contras:**
- Acoplamento forte ao pipeline de ingestão: mudanças no EWS runner (ex.: troca de tecnologia
  de stream processing) arrastam as regras de piora junto.
- O runner de EWS é tipicamente otimizado para throughput e latência de ingestão — adicionar
  13 regras com lógica de janela e pontuação ponderada degrada o caminho crítico.
- Dificuldade de versionamento independente: uma melhoria na regra de creatinina não deveria
  exigir redeploy do pipeline inteiro de EWS.

## Decisão

**Opção 1 — Serviço standalone `PioraClinicaService`**, com as seguintes características:

1. **Serviço dedicado, desacoplado do alert engine e do EWS runner.** O `PioraClinicaService` é
   um consumer Kafka autônomo que assina os tópicos CDC relevantes do `amh-data-platform`
   (`cdc.amh.tasy.resultado_exame`, `cdc.amh.tasy.sinais_vitais`, `cdc.amh.tasy.evolucao_clinica`
   e tópicos análogos), aplica as 13 regras de deterioração com pontuação graduada, e publica
   `PioraScoreCalculated` em `cdc.amh.tasy.piora-clinica.score`.

2. **As 13 regras são implementadas como DMN (ADR-0012).** Cada regra é uma `decisionTable`
   versionada que recebe o valor atual, o baseline (valor anterior ou referência), e a janela
   temporal, retornando o score `{0, 1+, 1-, 3+, 3-}`. A agregação ponderada (escore total e
   nível de alerta) também é uma DMN. O LLM **nunca** substitui a DMN na pontuação — raciocina
   sobre o resultado (ADR-0012).

3. **Escore agregado com thresholds versionados.** O escore total é comparado contra thresholds
   configuráveis (por tenant, por unidade, por perfil de paciente):
   - `score < THRESHOLD_LOW`: monitoramento contínuo, sem alerta.
   - `THRESHOLD_LOW ≤ score < THRESHOLD_MID`: notificação ao time assistencial (Helena agenda
     follow-up).
   - `score ≥ THRESHOLD_MID`: alerta de piora severa — `PioraAlertaSevero` publicado, roteamento
     para avaliação médica imediata (User Task humana, ADR-0005).

4. **Janela de observação deslizante configurável.** Cada regra opera sobre uma janela de
   observação (ex.: 6h, 12h, 24h, 48h dependendo do marcador). A janela é parametrizável por
   tenant e por regra, permitindo ajuste clínico sem redeploy.

5. **O serviço é stateless com estado de janela em Redis.** O estado da janela de observação
   por paciente (últimos N valores do marcador) é mantido em Redis com TTL. A reconstrução do
   estado a partir do CDC é possível (replay do tópico). Nenhum estado local em disco.

6. **O alerta é um sinal — nunca uma decisão.** O output do `PioraClinicaService` é um evento
   de pontuação. A decisão clínica subsequente (avaliar, intervir, ajustar conduta) é de
   responsabilidade exclusiva do profissional de saúde (L0-hard, ADR-0008). O serviço é
   classificado como **Zona PHI** (ADR-0006) — manipula PHI integral e não atravessa o gateway
   de pseudonimização.

**Gatilho de reavaliação:** Se o alert engine existente já cobrir >80% dos padrões de consumo
CDC e janela necessários para as regras de piora, reavaliar a Opção 2 como refatoração (extrair
o motor de regras como biblioteca compartilhada, mantendo serviços separados).

## Consequencias

**Positivas:**
- Desacoplamento total: a detecção de piora clínica evolui, escala e falha independentemente do
  alert engine administrativo e do pipeline de EWS.
- DMN como fonte canônica: as 13 regras são versionadas, auditáveis e testáveis isoladamente
  (consistente com ADR-0012); o LLM raciocina sobre o escore, nunca o calcula.
- Latência previsível: um consumer dedicado pode ser tunado para near-real-time sem competir por
  recursos com ingestão (EWS) ou alertas batch (alert engine).
- Testabilidade combinatorial: as 13 regras × 5 scores × janelas geram um espaço de teste que
  pode ser coberto com property-based testing focado, sem poluir suites de outros componentes.
- Conformidade L0-hard estrutural: o serviço não tem caminho de decisão clínica — é um calculador
  de score que publica evento. A fronteira com o humano é arquitetural, não convencional.

**Negativas (aceitas):**
- +1 serviço no portfólio operacional (build, deploy, monitoramento, escalabilidade).
- Duplica a lógica de consumo CDC (mas o consumer é fino — desserializa envelope Debezium e
  alimenta as DMNs; não duplica o pipeline CDC em si, consistente com ADR-0013).
- Dependência de Redis para estado de janela (ponto adicional de falha; mitigado por TTL curto
  e reconstrução via replay CDC).
- As 13 regras em DMN podem divergir de outros escores clínicos usados na instituição (ex.:
  MEWS, NEWS2); a calibração dos pesos e thresholds exige validação clínica e sign-off do
  corpo clínico — não é uma decisão puramente técnica.
- A separação entre "piora clínica" e "outros alertas" pode gerar duplicidade de sinal para o
  time assistencial (ex.: um mesmo evento dispara alerta no PioraClinicaService E no alert
  engine); requer deduplicação ou consolidação no agente consumidor (Helena).

## Supersedes

—
