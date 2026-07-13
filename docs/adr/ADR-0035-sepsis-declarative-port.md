# ADR-0035: Port da Lógica Rica de Sepse para o Motor Declarativo (sepse.yaml)

**Status:** accepted
**Data:** 2026-07-12
**Decisão por:** Orquestração de correção pós-auditoria (Claude Fable 5) — ratificação pendente do arquiteto

---

## Contexto

A auditoria full-spectrum (`docs/audit/fullspectrum/`) encontrou **duas implementações paralelas de sepse** divergindo silenciosamente:

1. **`src/intensicare/services/domain_sepsis.py`** — implementação rica e clinicamente ratificada: 6 alertas (`ALERT-SEPSIS-SCREEN-01` a `ALERT-SEPSIS-PCT-DEESC-06`), SIRS/qSOFA, estewardship de PCT (procalcitonina), timers de bundle SSC-2021 (Surviving Sepsis Campaign, hour-1 bundle), validada contra **31 vetores de teste** (`tests/test_domain_sepsis.py`, docstring: "6 alerts, 31 test vectors"; `docs/plan/_work/alerts/sepsis.yaml` como fonte dos vetores). Alcançável apenas via `/deterioration` (`src/intensicare/api/v1/deterioration.py`).
2. **`_work/alerts/pathways/sepse.yaml`** (atualmente `version: "3.0.0"`, linha 7) avaliado pelo `TrilhasEngine` (`src/intensicare/services/trilhas_engine.py`) — implementação empobrecida (sem PCT stewardship, sem os mesmos timers), mas é a **única** que o frontend v3 pathway-centric consome (ADR-0030, ADR-0031). O frontend v3 não chama `/deterioration`.

Resultado: o intensivista vendo a trilha de sepse na UI v3 recebe uma avaliação clínica inferior à que o backend já sabe fazer. Duas fontes de verdade para a mesma decisão clínica é o mesmo antipadrão que a ADR-0030 rejeitou para o frontend (Alternativa B), agora no backend.

### Habilitadores técnicos já disponíveis

- **Predicate `temporal`** e **`negate`/`NOT`** no `PredicateCompiler` (`src/intensicare/services/trilhas_compiler.py`, linhas 470–528 para `_compile_temporal`/`_evaluate_temporal`, linhas 132/406–419 para `negate` em predicados booleanos, linhas 430+ para o combinador `NOT`). São predicados **puros**: o `temporal` compara uma duração **pré-computada** (minutos) contra um orçamento (`within_minutes`, `satisfied_when: within|overdue`) — nunca lê o relógio internamente. O schema (`_work/alerts/schema/pathway.schema.json`) já foi estendido para `temporal`/`negate`/`NOT`/`within_minutes`/`satisfied_when`/`severity`.
- **`src/intensicare/services/sepsis_input_provider.py`** (novo, ainda não mesclado — `git status` mostra `A`): computa os inputs relativos que os avaliadores de `domain_sepsis.py` já esperam (`sirs_count`, `qsofa`, `minutes_since_accept_atb`, `minutes_since_accept_culturas`, `delta_pct_24h`, ...) a partir do que está de fato persistido (`VitalSign`, `LabResult`, `StabilityAssessment`, `PatientPathway`), com `now` injetado pelo chamador (determinístico, sem `datetime.now()` interno). O SIRS/qSOFA são reaproveitados **verbatim** de `domain_sepsis._compute_sirs_count`/`_compute_qsofa_points` (não reimplementados).
- O próprio `sepsis_input_provider.py` documenta lacunas de dados conhecidas: não há sinal persistido de confirmação de administração de antibiótico (`atb_ativa_horas`), nem de hemocultura (`culturas_antes_atb`), nem de suspeita de infecção (`infeccao_suspeita`) — esses inputs ficam **omitidos** (não zerados/adivinhados) até que a ingestão correspondente exista.

## Decisão

**Portar a lógica rica de `domain_sepsis.py` para o motor declarativo, tornando `sepse.yaml` a fonte de verdade única para a avaliação clínica de sepse consumida pela UI.**

1. `sepse.yaml` evolui de `3.0.0` (estado atual) para **`4.0.0`**, expressando SIRS, qSOFA, PCT stewardship e os timers de bundle SSC-2021 como predicados `graded`/`temporal`/`negate`/`NOT` compiláveis pelo `PredicateCompiler` real — os mesmos habilitadores já testados no schema.
2. `sepsis_input_provider.py` é a camada de fronteira: computa os inputs relativos upstream (fora do YAML), preservando o contrato "sem relógio dentro do predicado" e "input ausente = critério pendente" (fail-silent **correto**, não fail-silent por omissão de erro — ver ADR-0037 para a distinção com predicado inválido).
3. Paridade é validada por **teste diferencial** — `tests/test_sepse_yaml_parity.py` (a criar; ainda não existe no repositório nesta data) — usando `domain_sepsis.py` como **oráculo**: os mesmos 31 vetores de `tests/test_domain_sepsis.py` são re-executados contra `sepse.yaml` v4.0.0 via `TrilhasEngine`, exigindo resultado idêntico.
4. **Uma release de convivência**: `domain_sepsis.py`/`/deterioration` permanecem no ar em paralelo a `sepse.yaml` v4.0.0 por pelo menos um ciclo de release após a paridade ser confirmada, antes de `domain_sepsis.py` ser formalmente depreciado.

## Alternativas Consideradas

### Alternativa A: Enriquecer `sepse.yaml` diretamente, sem provider de inputs
- **Prós:** menos um módulo intermediário.
- **Contras:** obrigaria o YAML/`PredicateCompiler` (puro, por design) a acessar timestamps absolutos e estado de persistência diretamente, quebrando a garantia de "predicado sem relógio" que sustenta o Gate B de CI (ADR-0037).
- **Rejeitada porque:** violaria a separação pura/impura que já existe e é testável isoladamente.

### Alternativa B: Fazer o frontend v3 chamar `/deterioration` em vez de portar a lógica
- **Prós:** zero mudança no backend; reaproveita `domain_sepsis.py` como está.
- **Contras:** perpetua duas fontes de verdade (a UI teria que reconciliar o modelo de trilha do `TrilhasEngine` com a saída de `/deterioration`, que não fala o vocabulário de `PathwayDefinition`/estados que o frontend v3 pathway-centric espera — ADR-0030).
- **Rejeitada porque:** o product owner decidiu que trilha declarativa é o modelo mental correto para toda avaliação clínica exposta à UI, não apenas sepse.

### Alternativa C: Depreciar `domain_sepsis.py` imediatamente ao publicar `sepse.yaml` v4.0.0
- **Prós:** elimina a duplicação mais rápido.
- **Contras:** sem release de convivência, qualquer divergência de paridade não capturada pelos 31 vetores vira incidente de produção direto, sem rede de segurança.
- **Rejeitada porque:** patient-safety exige um período de operação lado a lado antes de remover a implementação oráculo.

## Consequências

### Positivas
- Uma única fonte de verdade clínica para sepse, consumida pela UI v3 sem gap de funcionalidade.
- Timers de bundle e lógica de PCT tornam-se **auditáveis** em YAML versionado e verificáveis em CI (Gate B — ver ADR-0037), em vez de enterrados em código Python.
- `sepsis_input_provider.py` isola a fronteira "dados impuros → inputs relativos puros", reaproveitável por outras trilhas que venham a precisar de timers.

### Negativas
- Dependência de dados de prescrição/hemocultura ainda não ingeridos (documentada em `sepsis_input_provider.py`) significa que critérios de bundle relacionados a `atb_ativa_horas`/`culturas_antes_atb`/`infeccao_suspeita` ficam **pendentes** (input ausente) em `sepse.yaml` v4.0.0 até que a ingestão correspondente exista — comportamento fail-silent correto (critério não avaliado ≠ critério que falhou), mas reduz cobertura clínica real até lá.
- Custo de manter dois sistemas (`domain_sepsis.py` + `sepse.yaml` v4.0.0) durante a release de convivência.
- `tests/test_sepse_yaml_parity.py` e `sepse.yaml` v4.0.0 ainda não existem nesta data — esta ADR registra a decisão e o desenho; a implementação é rastreada separadamente.

### Riscos e Mitigações
- **Risco:** paridade dos 31 vetores mascarar um caso de borda não coberto pelo conjunto original → **Mitigação:** release de convivência com `domain_sepsis.py` ativo como fallback observável.
- **Risco:** `sepsis_input_provider.py` computar um input relativo incorretamente sem que isso apareça como erro de compilação → **Mitigação:** teste diferencial cobre o pipeline ponta a ponta (dados persistidos → provider → YAML → resultado), não apenas o compilador.

---

## Referências

- `src/intensicare/services/domain_sepsis.py` (docstring: "WO-024: Implements 6 sepsis alerts (31 vectors)")
- `tests/test_domain_sepsis.py` ("Tests for Sepsis domain service (WO-024) — 6 alerts, 31 test vectors")
- `src/intensicare/api/v1/deterioration.py`
- `_work/alerts/pathways/sepse.yaml` (versão atual: `3.0.0`)
- `src/intensicare/services/trilhas_engine.py` (`TrilhasEngine`)
- `src/intensicare/services/trilhas_compiler.py` (`PredicateCompiler`, `_compile_temporal`, `negate`, `NOT`)
- `src/intensicare/services/sepsis_input_provider.py` (novo — build_sepsis_inputs)
- `_work/alerts/schema/pathway.schema.json` (extensão do schema para `temporal`/`negate`/`NOT`)
- `docs/audit/fullspectrum/` (auditoria full-spectrum)
- ADR-0030 (arquitetura pathway-centric do frontend v3)
- ADR-0037 (política fail-fast de pathways — Gate B de CI)
