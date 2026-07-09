# ADR-025: Padrão de Integração Movimentação-ADT — 74 regras de movimento

Status: accepted
**Data:** 2026-07-07
**Area:** Integração / Dados / Agentes
**Referência:** ADR-001 (hospitalar) — `amh-data-platform` como plataforma de dados de registro e
source of truth para ADT.

## Contexto

ADT (Admission, Discharge, Transfer) é o núcleo operacional de qualquer HIS (Hospital Information
System). A operadora AMH opera o Tasy como HIS, e o `amh-data-platform` já publica eventos CDC dos
registros de movimentação de pacientes (internação, alta, transferência entre unidades, mudança de
leito, bloco cirúrgico, etc.) — a plataforma de dados é o **source of truth** para ADT, conforme
estabelecido pelo ADR-001 do repositório hospitalar (`ADR-001-amh-data-platform-consumer`) e
reforçado pelo ADR-0013 deste repositório (consumo CDC como contrato de integração).

O domínio de movimentação hospitalar é complexo:

- **74 regras de movimento** capturam todo o ciclo de vida do paciente no hospital: admissão
  (eletiva, urgência, transferência externa), movimentação interna (unidade de internação ↔ UTI,
  bloco cirúrgico, recuperação pós-anestésica, isolamento), alta (domiciliar, transferência para
  outro hospital, óbito), e situações de borda (alta a pedido, evasão, reinternação <24h,
  readmissão programada).
- As regras incluem validações de negócio (ex.: não é possível transferir para UTI sem vaga
  registrada; alta sem prescrição de medicamentos de continuidade requer notificação; reinternação
  em <24h pelo mesmo CID dispara alerta de qualidade).
- **Restrição arquitetural (ADR-0013):** o Maezo **nunca escreve** no Tasy nem no
  `amh-data-platform`. Somos consumidores do CDC, não produtores de eventos ADT. O registro
  canônico de movimentação está no Tasy → replicado via CDC → consumido pelo Maezo.
- **Temporalidade**: agentes como Helena precisam saber o estado atual do paciente (onde está
  agora? está internado? há quanto tempo?) para iniciar jornadas de acompanhamento, follow-up
  pós-alta e detecção de reinternação precoce.

Três abordagens foram consideradas:

### Opção 1: Consumidor passivo (stateless, consulta CDC sob demanda)

O Maezo **não mantém estado próprio de ADT**. A cada interação de agente que precise de contexto
de movimentação, consulta-se o último snapshot do tópico CDC relevante ou uma API de projeção
exposta pelo `amh-data-platform`. O consumidor é stateless: lê, processa a regra, age, descarta.

**Prós:**
- Simplicidade máxima: zero estado mantido no Maezo.
- Consistência garantida com o source of truth (CDC) — cada consulta reflete o estado mais recente.
- Sem risco de divergência entre estado calculado e real.

**Contras:**
- Latência: cada interação de agente depende de um fetch externo (CDC consumer lag ou API call
  ao `amh-data-platform`).
- Impossibilidade de queries temporais complexas (ex.: "todos os pacientes que tiveram alta nos
  últimos 7 dias e NÃO tiveram follow-up") sem varrer o histórico CDC.
- O SLA da interação do agente fica acoplado ao SLA da plataforma de dados upstream.
- As 74 regras de movimento precisariam ser reavaliadas a cada interação — custo computacional
  repetido e sem cache.

### Opção 2: Estado ativo — materialized view própria (state store local)

O Maezo mantém uma **projeção materializada** do estado de movimentação: uma tabela/state store
(`patient_location_current`, `admission_history`, `transfer_log`) populada pelo consumo contínuo
dos tópicos CDC de ADT. As 74 regras são aplicadas sobre esse estado local. Agentes consultam
a projeção local com latência de banco de dados, não de rede externa.

**Prós:**
- Latência de consulta baixa e previsível (leitura local vs fetch remoto).
- Suporte a queries temporais e analíticas (ex.: "tempo médio de permanência em UTI por CID",
  "taxa de reinternação em 7 dias") — a projeção local pode ser indexada para o domínio do Maezo.
- As 74 regras podem ser aplicadas incrementalmente (a cada evento CDC), não sob demanda.
- Resiliência: o agente funciona mesmo se o `amh-data-platform` estiver momentaneamente
  indisponível (a projeção local está atualizada até o último evento processado).

**Contras:**
- Estado duplicado: o Maezo passa a manter uma cópia derivada do registro de movimentação — risco
  de divergência com o source of truth (CDC).
- Superfície de erasure LGPD ampliada: a projeção local contém dados de movimentação por paciente
  que precisam ser apagados em cascata no direito ao esquecimento (ADR-0002).
- Custo operacional: banco de dados ou state store adicional para manter a projeção, com
  estratégia de recuperação (snapshot + replay CDC).
- Complexidade de consistência: é necessário um mecanismo de reconciliação (health check de
  divergência vs source of truth) e estratégia de bootstrap (carga inicial a partir de snapshot).

### Opção 3: Event sourcing completo (event log próprio + projeções)

O Maezo mantém um **event log próprio** de movimentação (tópico Kafka interno, ex.:
`maezo.adt.movimentacao`), alimentado pelo consumo do CDC do `amh-data-platform`. Cada evento
CDC é traduzido para um evento de domínio Maezo (`PacienteInternado`, `PacienteTransferido`,
`PacienteAlta`, etc.) e apendado ao log. Projeções (`patient_location_projection`,
`admission_analytics_projection`) são derivadas do log via KStreams/KSQL ou consumidores
dedicados.

**Prós:**
- Auditabilidade completa: o event log é o histórico imutável de todas as movimentações
  processadas pelo Maezo — base sólida para auditoria e não-repúdio (ADR-0007).
- Projeções independentes: cada consumidor (agente Helena, dashboard operacional, analytics de
  ocupação) deriva sua própria projeção otimizada para seu caso de uso.
- Reconstrução total: qualquer projeção pode ser reconstruída do zero via replay do event log.
- Desacoplamento temporal: produtores (tradução CDC → evento de domínio) e consumidores
  (projeções) evoluem independentemente.

**Contras:**
- Complexidade arquitetural máxima: event sourcing introduz conceitos (event log, projeções,
  snapshots, CQRS implícito) que o time precisa dominar e operar.
- Duplicação de estado mais profunda que a Opção 2: além da projeção, mantém-se o event log
  completo — a superfície de erasure LGPD é ainda maior (eventos contêm PHI e precisam ser
  crypto-shredded ou truncados no erasure).
- Custo de infraestrutura: tópicos Kafka adicionais, armazenamento do event log, processamento
  de streams.
- Overkill para o escopo atual: as 74 regras de movimento são determinísticas e o volume de
  eventos ADT em um hospital de porte médio (~200-500 leitos) não justifica a complexidade do
  event sourcing completo — o ganho marginal sobre a Opção 2 é pequeno frente ao custo de
  complexidade.

## Decisão

**Opção 2 — Estado ativo com materialized view local (`MovimentacaoStateStore`)**, com as
seguintes características:

1. **Projeção materializada local, não event sourcing.** O Maezo mantém uma **projeção
   materializada** do estado de movimentação, populada incrementalmente pelo consumo dos
   tópicos CDC ADT do `amh-data-platform` (`cdc.amh.tasy.internacao`,
   `cdc.amh.tasy.movimentacao_paciente`, `cdc.amh.tasy.alta`, e tópicos análogos). A projeção
   NÃO é um event log completo — é uma **view materializada** com o estado atual + histórico
   agregado necessário para as 74 regras e para as queries dos agentes.

2. **O `amh-data-platform` permanece o source of truth; a projeção é um cache derivado.**
   Consistente com ADR-001 (hospitalar) e ADR-0013 (este repo): o Maezo **nunca escreve**
   no Tasy nem no `amh-data-platform`. A projeção local é um **cache read-only** — se houver
   divergência, o source of truth (CDC) prevalece. A reconstrução da projeção é feita via
   snapshot + replay CDC, não via backup/restore independente.

3. **As 74 regras de movimento são DMN (ADR-0012), aplicadas incrementalmente.** Cada evento
   CDC recebido dispara a avaliação das regras pertinentes (ex.: um evento de alta dispara
   as regras de validação de alta — medicamentos de continuidade, follow-up agendado,
   reinternação precoce). Regras que dependem de janela temporal (ex.: "reinternação em <24h")
   consultam a projeção local, não o CDC remoto.

4. **Esquema da projeção (`MovimentacaoStateStore`):**
   - `patient_location_current` — localização atual de cada paciente internado (unidade,
     leito, especialidade responsável, data/hora de admissão na unidade).
   - `admission_episode` — episódio de internação (data admissão, tipo, CID principal, status).
   - `transfer_log` — histórico de transferências (origem → destino, data/hora, motivo).
   - `discharge_summary` — sumário de alta (data, tipo de alta, destino pós-alta).
   - Armazenamento: PostgreSQL (mesmo cluster do runtime, schema `movimentacao`), com índices
     otimizados para as queries dos agentes (por `fhir_patient_id`, por unidade, por janela
     temporal).

5. **Bootstrap: snapshot + replay CDC.** A carga inicial da projeção é feita via snapshot do
   estado atual do `amh-data-platform` (API de exportação batch ou snapshot S3 do lake,
   consistente com ADR-0019) + replay dos eventos CDC a partir do offset do snapshot.
   O snapshot é versionado e o offset é registrado para garantir consistência.

6. **Reconciliação periódica com o source of truth.** Um health check diário compara a
   projeção local com o estado mais recente do CDC (amostragem de pacientes, checagem de
   localização atual, status de internação). Divergências são logadas como warning e
   corrigidas automaticamente (reprocessamento do range de offsets divergentes).

7. **Erasure LGPD (ADR-0002):** A projeção de movimentação é particionada por
   `fhir_patient_id`. O direito ao esquecimento deleta em cascata as linhas correspondentes
   nas 4 tabelas da projeção. A reconstrução pós-erasure é segura: o replay CDC não
   reintroduz o paciente apagado porque o erasure também notifica o `amh-data-platform`
   (que trunca ou suprime os eventos CDC do paciente).

8. **As 74 regras NÃO escrevem no Tasy.** Nenhuma regra de movimento dispara escrita no HIS.
   Se uma regra detectar uma condição que exigiria ação no Tasy (ex.: notificar a operadora
   sobre alta sem medicamentos de continuidade), o Maezo publica um evento de domínio
   (`AltaSemContinuidadeDetectada`) que é consumido por um agente ou processo SP-OP — e este,
   por sua vez, pode disparar uma User Task humana que resultará em ação no Tasy (via
   interface padrão do HIS, não via escrita direta no banco).

**Gatilho de reavaliação:** Se o volume de eventos ADT ultrapassar ~500 eventos/segundo
sustentados, ou se surgir um caso de uso que exija reconstrução de estado em um ponto
arbitrário no passado (time travel para auditoria retroativa), reavaliar a migração parcial
para a Opção 3 (event sourcing para o event log, mantendo as projeções como estão).

## Consequencias

**Positivas:**
- Latência de consulta baixa e previsível para os agentes (leitura local em PostgreSQL,
  ~5ms vs ~50-200ms de chamada remota ao `amh-data-platform`).
- Suporte nativo a queries temporais (permanência em UTI, taxa de reinternação) — a projeção
  local pode ser modelada e indexada para o domínio do Maezo, sem dependência do schema
  interno do `amh-data-platform`.
- As 74 regras são aplicadas incrementalmente (evento a evento), não sob demanda — o custo
  computacional é amortizado e a latência de detecção é mínima.
- Resiliência operacional: o agente Helena continua funcionando (com estado até o último
  evento CDC processado) mesmo durante indisponibilidade temporária do `amh-data-platform`.
- Conformidade com ADR-001/ADR-0013: o source of truth permanece no `amh-data-platform`; a
  projeção local é explicitamente derivada e reconciliável.
- DMN como fonte canônica das 74 regras (ADR-0012): versionadas, auditáveis, testáveis
  isoladamente.

**Negativas (aceitas):**
- Estado duplicado: a projeção local é uma cópia derivada e, como toda cópia, pode divergir
  do source of truth. Mitigação: reconciliação diária automatizada + alerta em divergência.
- Ampliação da superfície de erasure LGPD: mais tabelas para apagar em cascata no direito ao
  esquecimento (ADR-0002). Mitigação: particionamento por `fhir_patient_id` desde o schema;
  procedimento de erasure testado em CI.
- Custo operacional: tabelas adicionais no PostgreSQL (mesmo cluster, schema separado) +
  consumer CDC dedicado para ADT. Volume de dados: ~50-200 eventos/minuto em hospital de
  porte médio — crescimento controlado com particionamento por mês e retenção configurável.
- Complexidade de bootstrap: a carga inicial via snapshot + replay CDC é um procedimento
  operacional que precisa ser documentado e testado (não é complexo, mas não é trivial —
  exige coordenação com o time do `amh-data-platform` para o snapshot inicial).
- As 74 regras em DMN exigem validação de domínio com o time assistencial e de qualidade —
  não são puramente técnicas (regras como "reinternação <24h mesmo CID → alerta de qualidade"
  têm semântica clínica que precisa de sign-off).

## Supersedes

— (referencia o ADR-001 do repositório hospitalar `Omni-Saude/Maezo` —
`ADR-001-amh-data-platform-consumer.md` — que estabelece o `amh-data-platform` como
plataforma de dados de registro e source of truth para todos os domínios, incluindo ADT.
Estende o ADR-0013 deste repositório para o domínio específico de movimentação hospitalar.)
