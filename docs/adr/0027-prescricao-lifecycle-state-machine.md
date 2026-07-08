# ADR-027: Prescrição — Máquina de Estados do Ciclo de Vida da Prescrição

**Status:** Proposed
**Data:** 2026-07-07
**Area:** Prescrição / Domínio Clínico / Arquitetura de Dados
**Referência:** ADR-026 (drug interaction safety), ADR-0013 (consumo CDC), ADR-0008 (L0-hard — decisão clínica é humana), INV-1 (trilha de auditoria completa)
**Regulado:** parcial — transições de estado da prescrição são operações de registro clínico; auditoria completa é mandatória (INV-1); segurança clínica exige guardas de transição (ex.: não reativar prescrição descontinuada sem justificativa).

## Contexto

O ciclo de vida de uma prescrição na UTI é mais complexo que um simples binário ativo/inativo. A partir da análise das 43 regras legadas (`prescricao.yaml`) e do contrato OpenAPI (`prescricao-openapi.yaml`), emergem cinco estados clinicamente significativos:

1. **`draft` (rascunho):** a prescrição está sendo elaborada pelo prescritor. Pode estar incompleta — medicamentos sendo adicionados, doses sendo ajustadas, frequências sendo definidas. O rascunho não é visível para a equipe de enfermagem e não gera aprazamento (horários de administração). Pode ser descartado sem registro de descontinuação. **Não existe no OpenAPI atual** (que só modela `active`, `completed`, `discontinued`) — é uma necessidade identificada na análise de UX: prescritores de UTI frequentemente começam uma prescrição, são interrompidos por uma emergência, e retomam minutos ou horas depois. Sem `draft`, a prescrição parcial ou é perdida (frustração) ou é salva como `active` incompleta (risco de segurança — enfermagem pode administrar uma prescrição pela metade).

2. **`active` (ativa):** a prescrição foi finalizada e está em vigor. Visível para enfermagem, gera aprazamento (horários de administração), aparece no checklist de medicação do plantão. Pode ser modificada (ajuste de dose, frequência, via) — mas modificações em prescrição ativa devem ser registradas em log de auditoria com justificativa e timestamp.

3. **`completed` (concluída):** a prescrição cumpriu seu ciclo planejado (ex.: antibioticoterapia de 7 dias concluída, todos os horários administrados). `end_time` é registrado. A prescrição concluída permanece visível no histórico do paciente mas não gera novos aprazamentos. É um estado terminal brando — a prescrição pode ser reaberta (ex.: o médico decide estender o tratamento por mais 3 dias), mas reabertura gera uma nova prescrição ou reativação documentada.

4. **`discontinued` (descontinuada):** a prescrição foi interrompida antes do ciclo planejado por decisão clínica (ex.: reação adversa, troca de antibiótico por cultura, óbito do paciente, alta da UTI). `end_time` é registrado. A descontinuação exige justificativa clínica documentada. **Clinicamente, uma prescrição descontinuada NUNCA deve ser reativada** — se o mesmo fármaco for necessário novamente, uma nova prescrição deve ser criada (nova avaliação clínica, novo contexto). Reativar uma prescrição descontinuada é um risco de segurança: a justificativa da descontinuação original (ex.: reação alérgica) pode ser esquecida se a prescrição for simplesmente "reativada".

5. **`suspended` (suspensa):** a prescrição está temporariamente pausada — o fármaco não deve ser administrado neste momento, mas a intenção é retomar. Exemplos clínicos: suspensão de anticoagulante 24h antes de procedimento cirúrgico (retoma após); suspensão de anti-hipertensivo por hipotensão aguda (retoma quando PA estabilizar); suspensão de dieta enteral por resíduo gástrico elevado (retoma quando tolerar). A diferença fundamental para `discontinued`: **suspensão tem intenção de retorno**; descontinuação é definitiva. A suspensão tem data/hora de início (`suspended_at`) e pode ter data/hora planejada de reavaliação (`suspend_until`). **Este estado é parcialmente modelado pelo legado:** as regras RULE-PRESCRICAO-002 e RULE-PRESCRICAO-003 implementam lógica de suspensão via `DT_SUSPENSAO` — mas o fazem como flag booleana (`suspenso`), não como estado explícito na máquina de estados.

O legado implementava o ciclo de vida como um **campo de status simples** (`status` com valores `active`, `completed`, `discontinued`) sem validação de transições. As regras de suspensão (RULE-PRESCRICAO-002, RULE-PRESCRICAO-003) operavam como flags booleanas sobrepostas ao status, gerando inconsistências documentadas (ex.: uma prescrição `active` poderia ter `suspenso=True` para a ordem cabeçalho mas `suspenso=False` para uma dose individual em dia diferente — divergência de escopo registrada como DISCREPANCY no catálogo).

A questão arquitetural é: **como modelar o ciclo de vida da prescrição** considerando segurança clínica (transições inválidas devem ser impossíveis), auditoria completa (INV-1: toda mudança de estado deve ser rastreável com quem, quando, e por quê), concorrência (múltiplos clínicos podem interagir com a mesma prescrição simultaneamente), e a realidade de 43 regras legadas que já operam sobre o modelo de dados existente.

Três abordagens foram consideradas:

### Opção 1: Campo de status simples (enum) sem guardas de transição

A prescrição tem um campo `status` do tipo enum (`draft`, `active`, `completed`, `discontinued`, `suspended`). Qualquer transição é permitida — o backend aceita `PUT /prescriptions/{id}` com qualquer `status` a qualquer momento. A validação de transições inválidas (ex.: `discontinued → active`) fica a cargo da disciplina do time e de code review. O log de auditoria registra a mudança, mas não a valida.

**Prós:**
- Simplicidade máxima: um campo no banco, um enum no código, zero lógica de validação de transições.
- Flexibilidade: o prescritor pode fazer qualquer transição a qualquer momento — o sistema não impõe restrições que possam entrar em conflito com a realidade clínica (ex.: "o sistema não me deixa reativar, mas eu preciso porque a descontinuação foi um erro de digitação").
- Fácil de migrar do legado: o legado já usa `status` como enum — a migração é adicionar os novos valores (`draft`, `suspended`) ao enum existente.
- Sem custo de complexidade: zero código adicional para máquina de estados.

**Contras:**
- **Risco de segurança clínica:** nada impede que uma prescrição `discontinued` (ex.: descontinuada por reação alérgica documentada) seja acidentalmente reativada para `active` — seja por erro de UI (clique errado), bug, ou concorrência (dois clínicos editando a mesma prescrição). O sistema aceita silenciosamente.
- **Auditoria insuficiente para INV-1:** o log registra "status mudou de X para Y", mas não captura a **intenção** da transição (foi uma conclusão planejada? uma suspensão temporária? uma descontinuação por evento adverso?). Sem metadados de transição, a trilha de auditoria é pobre — saber QUE mudou sem saber POR QUE e EM QUAL CONTEXTO limita investigações retrospectivas.
- **Inconsistência com regras legadas:** as regras RULE-PRESCRICAO-002/003 implementam lógica de suspensão que depende de `DT_SUSPENSAO` (data/hora) — se o status de suspensão for apenas um enum sem timestamp, as regras legadas precisam ser reescritas ou mantidas em paralelo, perpetuando a inconsistência atual.
- **Concorrência sem proteção:** dois clínicos podem estar editando a mesma prescrição simultaneamente. Sem uma máquina de estados que valide transições atômicas (ex.: "só transite para `completed` se o estado atual for `active`"), é possível cenários como: clínico A conclui a prescrição (`active → completed`) enquanto clínico B a suspende (`active → suspended`) — o estado final depende de race condition do banco de dados (last-write-wins).
- **Débito técnico inevitável:** a validação de transições que não é feita pelo sistema **será** feita ad-hoc no frontend (ex.: desabilitar botão "Reativar" se status é `discontinued`), nos serializers Django, em middleware, ou em procedimentos operacionais manuais. Essa validação fragmentada é frágil, inconsistente, e difícil de testar.

### Opção 2: Máquina de estados formal com validação de transições (state machine)

O ciclo de vida da prescrição é modelado como uma **máquina de estados finitos explícita** — com estados, transições permitidas, guardas (condições que devem ser satisfeitas para a transição), e ações (efeitos colaterais disparados pela transição). Implementação como uma biblioteca de state machine (ex.: `transitions` em Python, ou uma DSL interna) integrada ao domain service de prescrição (`domain_prescricao.py`). O banco de dados armazena o estado atual + metadados da última transição (`transition`, `transitioned_by`, `transitioned_at`, `transition_reason`).

Transições permitidas e suas guardas:

```
draft ──┬──> active   [guard: prescription_is_complete]   → ação: generate_aprazamento()
        └──> void     [guard: none]                       → ação: delete_draft()

active ──┬──> completed   [guard: none]                   → ação: set_end_time(now)
         ├──> discontinued [guard: reason_required]        → ação: set_end_time(now), notify_pharmacist()
         └──> suspended    [guard: reason_required, suspend_until_optional] → ação: clear_aprazamento()

suspended ──┬──> active       [guard: none]               → ação: regenerate_aprazamento()
            └──> discontinued [guard: reason_required]     → ação: set_end_time(now)

completed ────> active       [guard: reactivation_reason_required, creates_new_prescription_or_logs_override]
                              → ação: log_reactivation_audit(), (opcional) create_continuation_prescription()

discontinued ──> (nenhuma transição permitida — estado terminal rígido)
```

**Prós:**
- **Segurança clínica por construção:** transições inválidas são impossíveis no backend — o código rejeita `discontinued → active` em nível de domínio, não depende de disciplina humana ou validação de frontend. Se um clínico precisar re-prescrever um fármaco descontinuado, ele cria uma nova prescrição (nova avaliação clínica).
- **Auditoria completa (INV-1):** cada transição registra metadados completos: estado origem, estado destino, timestamp, usuário, justificativa (`transition_reason`), e versão da definição da máquina de estados que validou a transição (`state_machine_version`). A trilha de auditoria reconstrói o ciclo de vida completo da prescrição com intenção documentada.
- **Concorrência segura com optimistic locking:** a transição é implementada como `UPDATE prescriptions SET status=$new, version=version+1 WHERE id=$id AND status=$expected_current AND version=$expected_version`. Se dois clínicos tentarem transições conflitantes, uma delas falha com `409 Conflict` — o cliente re-lê o estado atual e reavalia. Sem race condition.
- **Consistência com regras legadas:** a máquina de estados torna explícito o que as regras RULE-PRESCRICAO-002/003 implementavam implicitamente. O estado `suspended` substitui o flag booleano `suspenso` e a lógica de `DT_SUSPENSAO` — eliminando a divergência de escopo documentada (ordem vs dose). As regras legadas são reimplementadas como guardas e ações da máquina de estados, não como lógica dispersa em serializers.
- **Testabilidade:** a máquina de estados é uma unidade pura e testável isoladamente. Testes cobrem todas as transições válidas, todas as transições inválidas, todas as guardas, e cenários de concorrência. Property-based testing pode verificar invariantes (ex.: "nenhuma transição parte de `discontinued`").
- **Versionamento da definição:** a máquina de estados é versionada (`state_machine_version`). Se no futuro uma nova evidência clínica exigir uma transição adicional (ex.: permitir `completed → suspended` para casos de reavaliação pós-conclusão), a mudança é explícita, versionada, e auditável.

**Contras:**
- Complexidade adicional: ~300-500 linhas de código para a máquina de estados + testes + integração com o domain service. Mais complexo que um simples enum.
- Rigidez: a máquina de estados formal pode ser percebida como "o sistema não me deixa fazer o que eu preciso". Exemplo: um clínico descontinua uma prescrição por engano e imediatamente percebe o erro — com a máquina de estados, ele não pode simplesmente "desfazer" a descontinuação; precisa criar uma nova prescrição. Isso é clinicamente mais seguro, mas pode gerar atrito na UX se não for bem comunicado.
- Custo de migração: o legado usa `status` como campo simples. Migrar para máquina de estados exige: (a) mapear registros existentes para os estados corretos (ex.: prescrições com `DT_SUSPENSAO` passado e `suspenso=True` → estado `suspended`); (b) backfill dos metadados de transição (`transitioned_by`, `transition_reason`) que não existem no legado; (c) adaptar as 43 regras legadas para consumir o novo modelo de estados em vez dos campos legados.
- Acoplamento com a UI: o frontend precisa refletir a máquina de estados — desabilitar botões de transições inválidas, exibir justificativa obrigatória para `discontinued` e `suspended`, tratar `409 Conflict` em concorrência. Isso exige que o frontend conheça as transições permitidas (seja via duplicação ou via metadata endpoint que exponha a definição da máquina de estados).

### Opção 3: Event sourcing — log de eventos de prescrição com projeção de estado

Cada mudança no ciclo de vida da prescrição é registrada como um evento imutável em um event log (`prescription_event_log`): `PrescriptionDrafted`, `PrescriptionActivated`, `PrescriptionCompleted`, `PrescriptionDiscontinued`, `PrescriptionSuspended`, `PrescriptionResumed`. O estado atual da prescrição é uma **projeção** derivada do replay dos eventos. A validação de transições é feita no momento da emissão do evento (o domain service verifica se o evento é válido dado o estado atual projetado). O event log é a fonte de verdade; a projeção é derivada e pode ser reconstruída a qualquer momento.

**Prós:**
- **Auditoria máxima (INV-1 com folga):** o event log é o histórico completo e imutável de todas as mudanças de estado — auditável por construção. Cada evento carrega metadados completos (timestamp, usuário, justificativa, contexto clínico). Não há como "perder" uma transição — está no log para sempre.
- **Reconstrução total:** o estado de qualquer prescrição em qualquer ponto no passado pode ser reconstruído via replay dos eventos até aquele timestamp. Isso permite auditoria retroativa (ex.: "quando exatamente a prescrição de vancomicina foi suspensa em relação ao pico de creatinina do paciente?") e correção de bugs (se a lógica de projeção tiver um bug, corrige-se a projeção e reprocessa-se o event log — os eventos originais permanecem intactos).
- **Concorrência natural:** eventos são apend-only. Conflitos de escrita não existem — dois clínicos podem emitir eventos concorrentes; a projeção resolve o estado final deterministicamente. Não há race condition de last-write-wins porque não há "write" no estado — há "append" no log.
- **Casos de uso analíticos:** o event log permite queries temporais complexas (ex.: "tempo médio entre suspensão e reativação de antibióticos na UTI", "taxa de descontinuação por reação adversa por fármaco") sem depender de snapshots de estado.
- **Desacoplamento temporal:** produtores (domain service que emite eventos) e consumidores (projeção de estado, projeção analítica, notificações para farmácia) evoluem independentemente.

**Contras:**
- **Complexidade arquitetural máxima:** event sourcing introduz conceitos (event log, projeções, snapshots, CQRS implícito, replay, consistência eventual) que exigem maturidade do time e infraestrutura adicional (Kafka ou PostgreSQL como event store, consumidores de projeção, estratégia de snapshot).
- **Consistência eventual:** a projeção do estado atual não é imediatamente consistente após a emissão de um evento — há um gap entre o evento ser apendado e a projeção ser atualizada. Para um sistema de prescrição onde a enfermagem precisa saber imediatamente se um medicamento está ativo ou suspenso, latência de projeção é inaceitável (a menos que se use projeção síncrona, o que anula parte do desacoplamento).
- **Superfície de erasure LGPD ampliada (ADR-0002):** o event log contém eventos imutáveis com PHI (qual fármaco foi prescrito, descontinuado por qual reação adversa, etc.). O direito ao esquecimento exige que esses eventos sejam apagados ou crypto-shredded — mas eventos imutáveis em um log apend-only são difíceis de apagar sem corromper a integridade do log. Soluções existem (ex.: crypto-shredding com chave por paciente), mas adicionam complexidade.
- **Overkill para o domínio:** o ciclo de vida de uma prescrição tem 5 estados e ~10 transições possíveis. Event sourcing é uma solução desenhada para domínios com dezenas de estados, centenas de transições, e requisitos complexos de reconstrução temporal (ex.: contabilidade, supply chain, jogos). Para prescrição, o ganho marginal sobre uma máquina de estados bem implementada (Opção 2) é pequeno — a auditoria da Opção 2 (metadados de transição + `transition_reason`) já satisfaz INV-1; a reconstrução temporal não é um requisito atual.
- **Custo operacional:** manter um event log + projeções + snapshots + replay para um domínio de prescrição é desproporcional ao benefício no estágio atual do IntensiCare.

## Decisão

**Opção 2 — Máquina de estados formal com validação de transições (`PrescriptionStateMachine`)**, com as seguintes características:

1. **Máquina de estados explícita, não event sourcing.** O ciclo de vida da prescrição é modelado como uma máquina de estados finitos com 5 estados (`draft`, `active`, `completed`, `discontinued`, `suspended`) e transições estritamente controladas. A implementação usa uma biblioteca de state machine em Python (ex.: `transitions`) integrada ao `domain_prescricao.py`. O estado atual é armazenado como campo `status` em PostgreSQL — não como projeção derivada de event log.

2. **Transições permitidas e guardas (versão 1.0):**

   | Transição | Guarda | Ação |
   |---|---|---|
   | `draft → active` | `prescription_is_complete`: todos os campos obrigatórios preenchidos, ao menos 1 medicamento, verificação de interações concluída (ADR-026) | `generate_aprazamento()`: calcula horários de administração; registra `start_time = now` |
   | `draft → void` | nenhuma | `delete_draft()`: remove o rascunho sem registro de auditoria (não era uma prescrição ativa) |
   | `active → completed` | nenhuma | `set_end_time(now)`, `clear_aprazamento()`: remove horários futuros não administrados |
   | `active → discontinued` | `reason_required`: justificativa clínica obrigatória (texto livre, mínimo 20 caracteres) | `set_end_time(now)`, `clear_aprazamento()`, `notify_pharmacist()`: notifica farmacêutico clínico sobre descontinuação |
   | `active → suspended` | `reason_required`: justificativa obrigatória; `suspend_until` opcional (data/hora planejada de reavaliação) | `clear_aprazamento()`: remove horários de administração; registra `suspended_at = now` |
   | `suspended → active` | nenhuma (retomada) | `regenerate_aprazamento()`: recalcula horários a partir de agora; registra `resumed_at = now`; limpa `suspended_at` |
   | `suspended → discontinued` | `reason_required`: justificativa obrigatória (ex.: "suspensão convertida em descontinuação — reação adversa confirmada") | `set_end_time(now)`, `notify_pharmacist()` |
   | `completed → active` | `reactivation_reason_required` + `creates_new_prescription`: a reabertura de prescrição concluída cria uma **nova prescrição** vinculada à original (`continuation_of`) OU, excepcionalmente, permite reativação com override documentado | `log_reactivation_audit()` registra justificativa; se nova prescrição, copia fármacos e inicia novo ciclo |
   | `discontinued → *` | **NENHUMA TRANSIÇÃO PERMITIDA** — estado terminal rígido | — |

3. **`discontinued` é um estado terminal rígido.** Clinicamente, uma prescrição descontinuada jamais deve ser reativada. Se o mesmo fármaco for necessário novamente, o prescritor cria uma nova prescrição — o que força uma nova avaliação clínica (o paciente ainda precisa desse fármaco? a dose está correta para o contexto atual? a razão da descontinuação original foi resolvida?). Essa rigidez é intencional e documentada como decisão de segurança clínica. O sistema orienta o prescritor: _"Esta prescrição foi descontinuada. Para prescrever o mesmo fármaco, crie uma nova prescrição."_

4. **`completed → active` cria nova prescrição por padrão.** Reabrir uma prescrição concluída (ex.: estender antibioticoterapia) cria uma nova prescrição vinculada (`continuation_of = prescription_id`), copiando fármacos, doses e frequências da original. Isso garante que o ciclo original permaneça íntegro (concluído) e o novo ciclo tenha seu próprio `start_time`, aprazamento e trilha de auditoria. Excepcionalmente, se o prescritor insistir em reativar a prescrição original (ex.: concluiu por engano), o sistema permite com override documentado e registro de auditoria — mas o UX desencoraja fortemente (confirmação dupla + justificativa obrigatória).

5. **Cada transição registra metadados de auditoria (INV-1).** Tabela `prescription_state_log`:

   ```sql
   CREATE TABLE prescription_state_log (
       id BIGSERIAL PRIMARY KEY,
       prescription_id INTEGER NOT NULL REFERENCES prescriptions(id),
       from_status prescription_status NOT NULL,
       to_status prescription_status NOT NULL,
       transitioned_by VARCHAR(255) NOT NULL,     -- clínico que executou a transição
       transitioned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
       transition_reason TEXT,                      -- justificativa clínica (obrigatória para discontinued, suspended, reactivation)
       state_machine_version VARCHAR(32) NOT NULL,  -- versão da definição da máquina de estados
       context JSONB                                -- metadados adicionais (ex.: suspend_until, continuation_of)
   );
   ```

   Essa tabela é apend-only (sem updates ou deletes) e particionada por mês. Satisfaz INV-1 integralmente — toda mudança de estado é rastreável com quem, quando, por quê, e sob qual versão das regras.

6. **Concorrência com optimistic locking.** A transição de estado é implementada como:

   ```sql
   UPDATE prescriptions
   SET status = $new_status,
       version = version + 1,
       updated_at = now()
   WHERE id = $id
     AND status = $expected_current_status
     AND version = $expected_version
   RETURNING id
   ```

   Se zero linhas afetadas, a transição é rejeitada com `409 Conflict` — o estado mudou entre a leitura e a escrita. O frontend re-lê o estado atual e notifica o prescritor: "Esta prescrição foi modificada por outro usuário. Por favor, revise o estado atual antes de prosseguir." Isso elimina race conditions sem bloqueio pessimista (que degradaria performance em cenários de alta concorrência).

7. **Integração com regras legadas.** As regras RULE-PRESCRICAO-002 (dose-level suspension) e RULE-PRESCRICAO-003 (order-level suspension) são **substituídas** pela máquina de estados. O estado `suspended` com `suspended_at` timestamp substitui o flag `suspenso` + `DT_SUSPENSAO` — eliminando a divergência de escopo documentada (ordem vs dose). O aprazamento é recalculado automaticamente nas transições `active → suspended` (limpa horários) e `suspended → active` (regenera horários). As demais 40 regras (captura de medicamentos, balanço hídrico, boundary de turno, validação de administração) operam sobre o campo `status` da prescrição, que agora é gerido pela máquina de estados — mas a lógica interna das regras não muda (ex.: RULE-PRESCRICAO-001 continua exportando `qtd_exportada` para balanço hídrico independentemente do estado da prescrição; apenas prescrições `active` geram aprazamento).

8. **A máquina de estados é versionada e testada.** A definição da máquina de estados é armazenada como código versionado (`domain_prescricao.py`, classe `PrescriptionStateMachine`) e referenciada por `state_machine_version` (ex.: `1.0.0`). Testes cobrem:
   - Todas as transições válidas (8 transições, cada uma com guarda satisfeita → sucesso).
   - Todas as transições inválidas (ex.: `active → draft`, `discontinued → active`, `suspended → draft` → rejeitadas).
   - Todas as guardas (ex.: `active → discontinued` sem `reason` → rejeitada; `draft → active` com prescrição incompleta → rejeitada).
   - Concorrência (dois updates simultâneos → um rejeitado com 409).
   - Idempotência (transitar para o mesmo estado → no-op ou rejeição controlada).

9. **A máquina de estados é consultável pelo frontend.** Endpoint `GET /prescriptions/state-machine` retorna a definição da máquina de estados (estados, transições permitidas, guardas) para que o frontend possa:
   - Desabilitar botões de transições inválidas (ex.: esconder "Reativar" se status é `discontinued`).
   - Exibir campos obrigatórios contextualmente (ex.: mostrar campo "Justificativa" apenas quando a transição selecionada exige `reason_required`).
   - Exibir o diagrama de estados na documentação.
   Isso evita duplicação da lógica de estados entre frontend e backend — o backend é a fonte de verdade, e o frontend consome a definição como metadata.

**Gatilho de reavaliação:** Se o volume de transições de estado ultrapassar ~50/segundo sustentados (múltiplos hospitais de grande porte), ou se surgir requisito de reconstrução temporal para auditoria retroativa (ex.: "qual era o estado desta prescrição em 2026-06-15T14:30:00?"), reavaliar a migração parcial para event sourcing (Opção 3) apenas para o `prescription_state_log`, mantendo a projeção de estado atual como está.

## Consequencias

**Positivas:**
- **Segurança clínica por construção:** transições perigosas são impossíveis. `discontinued → active` não existe no código — não depende de disciplina, code review, ou validação de frontend. Se um clínico descontinuou uma prescrição por reação alérgica, o sistema **impede** que outro clínico a reative acidentalmente.
- **Auditoria completa (INV-1):** `prescription_state_log` registra toda transição com quem, quando, justificativa, e versão da máquina de estados. A trilha de auditoria reconstrói o ciclo de vida completo da prescrição — essencial para investigação de eventos adversos e conformidade regulatória (CFM, ANVISA).
- **Eliminação de inconsistências legadas:** as regras RULE-PRESCRICAO-002/003 (suspensão de dose vs ordem, divergência de escopo) são substituídas por um modelo de estados consistente e centralizado. O estado `suspended` com `suspended_at` timestamp é semanticamente claro e não ambíguo.
- **Concorrência segura:** optimistic locking previne race conditions sem bloqueio pessimista. Múltiplos clínicos podem operar sobre a mesma prescrição simultaneamente sem risco de estado inconsistente.
- **Fundação para features futuras:** a máquina de estados explícita habilita: (a) notificações contextuais (ex.: notificar farmacêutico apenas em `active → discontinued`, não em `active → completed`); (b) SLAs de transição (ex.: alertar se prescrição está em `draft` há >30 minutos — possível interrupção do prescritor); (c) integração com FHIR MedicationRequest (que tem `status` com estados equivalentes a `draft`, `active`, `completed`, `stopped` — mapeamento direto).

**Negativas (aceitas):**
- Complexidade adicional (~500 linhas de código + testes + log) comparado a um simples enum. Justifica-se pelo risco de segurança clínica que a Opção 1 (enum simples) introduz.
- Rigidez percebida: clínicos acostumados com sistemas flexíveis podem estranhar a impossibilidade de "desfazer" uma descontinuação. Mitigação: UX que comunica claramente o porquê ("Esta prescrição foi descontinuada por reação alérgica em 2026-07-06. Para segurança do paciente, crie uma nova prescrição.") + atalho "Recriar prescrição" que copia os fármacos para um novo rascunho.
- Custo de migração do legado: mapear registros existentes (campo `status` simples + flag `suspenso`) para os 5 estados da máquina + backfill do `prescription_state_log`. A migração é um script único (não contínuo) e pode ser executada como parte do deploy da feature de prescrição v2.
- O log de transições (`prescription_state_log`) é apend-only e cresce linearmente com o uso — em hospital de 200 leitos de UTI com ~500 transições/dia, são ~180K registros/ano. Gerenciável com particionamento por mês e retenção configurável (ex.: 5 anos online, archive em S3/Glacier após).
- O estado `suspended` adiciona complexidade de UX: o prescritor precisa distinguir entre "descontinuar" (definitivo, não volta) e "suspender" (temporário, vai voltar). Se a distinção não for clara na interface, o risco é que prescrições sejam suspensas quando deveriam ser descontinuadas (ou vice-versa) — gerando aprazamento inadequado ou perda de rastreabilidade. Mitigação: UX com linguagem clara, tooltips, e dupla confirmação com explicação da diferença.

## Supersedes

— (Substitui a lógica de suspensão das regras RULE-PRESCRICAO-002 e RULE-PRESCRICAO-003 do catálogo legado, consolidando o flag booleano `suspenso` + `DT_SUSPENSAO` no estado explícito `suspended` com `suspended_at` timestamp. Referencia INV-1 para o requisito de auditoria completa. Referencia ADR-0008 para o princípio de que a decisão clínica é humana — a máquina de estados restringe transições mas não decide por que uma prescrição deve ser descontinuada ou suspensa; essa decisão é do prescritor, documentada no `transition_reason`.)
