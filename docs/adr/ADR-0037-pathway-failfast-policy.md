# ADR-0037: Política Fail-Fast para Predicados de Pathway (CI + Runtime)

**Status:** accepted
**Data:** 2026-07-12
**Decisão por:** Orquestração de correção pós-auditoria (Claude Fable 5) — ratificação pendente do arquiteto

---

## Contexto

A auditoria full-spectrum (`docs/audit/fullspectrum/`) encontrou um padrão de falha silenciosa em produção: critérios de pathway com banda (`graded`) inválida — faixas que não particionam corretamente o domínio de valores — eram descartados apenas com `logger.warning`, e a avaliação do pathway seguia em frente **sem aquele critério**. Concretamente, isso significava que trilhas de delirium e sedação podiam nunca disparar um alerta esperado, sem que ninguém — CI, logs monitorados, ou o intensivista — percebesse. Em um sistema de patient-safety, "critério clínico silenciosamente ausente" é uma classe de bug tão grave quanto "critério clínico incorreto".

O `PredicateCompiler` (`src/intensicare/services/trilhas_compiler.py`) já existia como compilador puro de predicados (`threshold`, `graded`, `boolean`, `composite`/`AND`/`OR`/`NOT`, `temporal` — ver ADR-0035), mas nada impedia um YAML de pathway com um predicado malformado de chegar a produção, nem havia uma política clara de "o que fazer em runtime quando um predicado não compila".

## Decisão

**Política híbrida em duas camadas — CI compila tudo antes do deploy; runtime nunca avalia parcialmente um pathway clínico.**

### 1. CI — Gate B (`scripts/validate_alerts.py`)

Além da checagem de partição de bandas já existente (reimplementação própria), o Gate B agora também **compila cada predicado com o `PredicateCompiler` real de produção** (`from intensicare.services.trilhas_compiler import PredicateCompiler`, `scripts/validate_alerts.py` linhas 45–57), exercitando exatamente o mesmo código que roda em runtime — não uma reimplementação que poderia divergir. A função dedicada (linhas ~316–350) instancia `PredicateCompiler()` e chama `compiler.compile(pred)` para cada predicado de cada pathway; qualquer `ValueError` de compilação real é reportado como `FAIL [Gate B/compile]`. **YAML com predicado incompilável não passa no CI, portanto não chega a produção.**

### 2. Runtime — fail-fast por pathway, nunca por critério isolado

Em `TrilhasEngine._load_all` (`src/intensicare/services/trilhas_engine.py`, linhas ~322–351): cada predicado de cada critério é compilado individualmente durante o carregamento do YAML. Se **qualquer** predicado falhar a compilação:
- `logger.error` (não mais `logger.warning`) registra o critério, o pathway e o motivo;
- o erro é anexado à lista pública `self.load_failures` (dict com `slug`, `criterion_id`, `error`);
- o **pathway inteiro** é marcado `active=False` — nunca avaliação parcial de um pathway clínico com um critério faltando silenciosamente. Os demais critérios do mesmo pathway continuam sendo tentados apenas para fins de diagnóstico (`compiled_count`), não para compor uma avaliação parcial servida ao usuário.

`load_failures` é exposto publicamente pela engine para que operação/observabilidade possa consultá-lo pós-boot.

### 3. Boot só falha se ZERO pathways compilam

No `__init__` de `TrilhasEngine` (linhas ~134–144): após carregar todos os YAML, se **nenhum** pathway ficou `active=True`, o construtor levanta `RuntimeError` — "Refusing to boot with an engine that cannot fire any alert." Isso cobre o caso extremo (YAML ausente/corrompido, ou todos os pathways com falha de compilação), mas **não** exige que 100% dos pathways compilem para o sistema subir: se, por exemplo, 7 de 8 pathways compilam e 1 (ex.: delirium) falha, o boot prossegue com 7 pathways ativos, `sedacao`/`delirium` marcado `active=False` e visível em `load_failures` — degradação parcial e visível, não travamento total nem falha silenciosa.

## Alternativas Consideradas

### Alternativa A: Só CI (sem verificação em runtime)
- **Prós:** mais simples — uma única camada de defesa.
- **Contras:** não cobre YAML gerado/editado fora do pipeline de CI (hotfix manual, seed de ambiente, arquivo corrompido em disco), nem drift entre a versão do `PredicateCompiler` no momento do CI e a versão realmente carregada em runtime.
- **Rejeitada porque:** patient-safety exige defesa em profundidade; a auditoria já havia encontrado exatamente esse tipo de gap (banda inválida chegando a runtime sem ser pega antes).

### Alternativa B: Runtime aborta o boot inteiro se QUALQUER pathway falhar
- **Prós:** máxima segurança teórica — impossível haver pathway parcialmente quebrado no ar.
- **Contras:** um único YAML malformado (ex.: trilha nova em desenvolvimento) derrubaria alertas de **todas** as outras trilhas clínicas (sepse, piora clínica, etc.), o que é pior para o paciente do que perder uma trilha.
- **Rejeitada porque:** a política adotada — boot falha só se zero pathways compilam — equilibra disponibilidade das trilhas saudáveis com a garantia de nunca avaliar uma trilha quebrada parcialmente.

### Alternativa C: Manter `logger.warning` e descartar apenas o critério inválido (comportamento anterior)
- **Prós:** máxima disponibilidade — pathway continua rodando com os critérios que compilaram.
- **Contras:** é exatamente o bug que a auditoria encontrou — avaliação parcial e silenciosa de um pathway clínico, sem visibilidade operacional.
- **Rejeitada porque:** viola o princípio de que uma trilha clínica deve ser avaliada por completo ou não ser avaliada — nunca uma versão incompleta sem sinalização.

## Consequências

### Positivas
- Falha silenciosa de critério clínico deixa de ser possível: YAML inválido é barrado no CI (Gate B); se algo escapar, o pathway inteiro fica `active=False` e visível em `load_failures`, nunca avaliado pela metade.
- CI exercita o compilador real de produção, eliminando divergência entre "o que o CI valida" e "o que roda em runtime".
- Degradação é visível e **parcial**: perder uma trilha (ex.: delirium) não derruba as demais (ex.: sepse), preservando disponibilidade do sistema como um todo.

### Negativas
- Boot pode subir "degradado" (N-1 pathways ativos) sem falhar explicitamente — exige que operação monitore `load_failures`/logs de `logger.error` ativamente, não apenas o healthcheck de boot.
- Gate B adiciona tempo de execução ao pipeline de CI (compilação real de todos os predicados de todos os pathways a cada run).

### Riscos e Mitigações
- **Risco:** `load_failures` não é observado por ninguém (alerta de log não configurado) → **Mitigação:** expor `load_failures` como métrica/healthcheck consultável, não apenas em log (acompanhamento fora do escopo desta ADR).
- **Risco:** Gate B e o `PredicateCompiler` de runtime divergirem por deploy de versões diferentes de código → **Mitigação:** Gate B importa o compilador de produção diretamente (mesmo pacote), não uma cópia.

---

## Referências

- `scripts/validate_alerts.py` (Gate B — Band Partition; seção `compiler = PredicateCompiler()` / `compiler.compile(pred)`)
- `src/intensicare/services/trilhas_compiler.py` (`PredicateCompiler`)
- `src/intensicare/services/trilhas_engine.py` (`TrilhasEngine._load_all`, `load_failures`, fail-fast de boot em `__init__`)
- `_work/alerts/schema/pathway.schema.json` (schema de predicados validado pelo Gate B)
- `docs/audit/fullspectrum/` (auditoria full-spectrum — achado de `logger.warning` silencioso em critérios de delirium/sedação)
- ADR-0035 (port declarativo de sepse — mesmo `PredicateCompiler` usado como base pura)
