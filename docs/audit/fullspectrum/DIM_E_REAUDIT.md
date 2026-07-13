# DIM E — RE-AUDITORIA de Inovação e Estado da Arte em CDS de UTI

**Data:** 2026-07-12 · **Re-auditor:** agente independente (somente leitura; não implementou nada; único write é este relatório)
**Branch:** `fix/sprint-3-sepsis-governance`
**Baseline re-auditada:** `docs/audit/fullspectrum/DIM_E_INNOVATION.md` (score original **58/100**)

> Metodologia: reexecução item a item da rubrica de dedução original (§6 do baseline). Cada dedução foi
> reavaliada lendo o artefato citado como corretivo e, sempre que possível, verificando-o ao vivo (não
> apenas lendo prosa de ADR): `_work/alerts/pathways/sepse.yaml` (v4.0.0) foi lido por completo;
> `tests/test_sepse_yaml_parity.py` foi **executado** (`pytest tests/test_sepse_yaml_parity.py -q` →
> `32 passed, 1 xfailed`); `trilhas_compiler.py` foi grepado para confirmar que `temporal`/`negate`/`NOT`
> são código real, não só documentado em ADR; `README.md`, `ADR-0031`, `ADR-0033`, `ADR-0037`,
> `CLINICAL_SIGNOFF.md` foram lidos; buscas exaustivas (`grep -rn`) confirmaram ausência persistente de
> ML (`sklearn|torch|tensorflow|model.predict|risk_score`) e de padrões interoperáveis (`Arden|CQL|CDS
> Hooks`) em `src/`, `tests/`, `docs/adr/`.

---

## 1. VEREDITO EXECUTIVO

O ciclo de correção pós-auditoria portou a lógica clínica rica de `domain_sepsis.py` (SIRS, PCT
stewardship, timers de bundle SSC-2021) para o motor declarativo (`sepse.yaml` v4.0.0), validou a
paridade com um oráculo executável (31 vetores, teste real rodado nesta re-auditoria: **32 passed, 1
xfailed**), estendeu o compilador de predicados com `temporal` e `NOT`/`negate` (código real, não só
ADR), e reconciliou parcialmente a narrativa de contagem de domínios/trilhas com notas datadas em
`ADR-0031`/`ADR-0033` e uma seção nova no README. Um documento de sign-off clínico
(`CLINICAL_SIGNOFF.md`) formaliza a aprovação de um intensivista para as decisões deste ciclo.

Isso resolve substancialmente **3 das 7 deduções originais** (sepse pobre, contagens não reconciliadas,
validação clínica ausente) e resolve **parcialmente** uma quarta (tempo-de-ação estruturado, mas só para
sepse). **Duas deduções persistem integralmente e por escolha, não por lacuna de esforço**: zero
capacidade preditiva (ML) e DSL não interoperável (sem Arden/CQL/CDS Hooks) — nenhuma delas foi tocada
neste ciclo, nem deveria ter sido (são decisões arquiteturais de outro escopo, já bem fundamentadas no
baseline, ADR-0023). A dedução de gaps de cobertura clínica (glicemia, transfusão, PAV completo,
estratificação de risco em profilaxia) também **persiste quase integralmente** — nenhum destes gaps foi
fechado nem formalmente documentado como decisão consciente neste ciclo.

**NOVO SCORE: 72/100** (+14 vs. 58/100 original).

O gap competitivo nº1 remanescente frente a Epic EDI/CLEW **continua sendo a ausência total de
capacidade preditiva/lead-time** — não mudou, e não deveria ter mudado num ciclo de correção de
governança/paridade, não de pesquisa de ML.

---

## 2. Dedução a dedução

| # | Achado original (baseline) | Pontos originais | Reavaliação | Pontos novos | Delta |
|---|---|---|---|---|---|
| 1 | Nenhuma trilha tem tempo-de-ação/SLA estruturado | -10 | **Parcial.** `sepse.yaml` v4 introduz 2 critérios `type: temporal` reais (`crit-sep-bundle-atb-1h`: `within_minutes: 60, satisfied_when: overdue`; `crit-sep-bundle-reaval-3h`: `within_minutes: 180`), compilados por `_compile_temporal`/`_evaluate_temporal` em `trilhas_compiler.py` (não é texto — é um nó AST que o motor avalia e que dispara `severity: critical`). Isto é tempo-de-ação estruturado e acionável pelo motor, exatamente o que a recomendação #1 do baseline pedia. **Mas é local a 1 de 12 trilhas** — `grep -l "type: temporal" _work/alerts/pathways/*.yaml` retorna só `sepse.yaml`; as outras 11 trilhas continuam com tempo-de-ação só em texto livre em `evidence.recommendations`. O `pathway.schema.json` também ganhou `within_minutes`/`satisfied_when`/`negate`/`NOT` como capacidade genérica do schema (não amarrada à sepse), então a infraestrutura está pronta para replicação — mas a replicação em si não aconteceu. | **-6** | +4 |
| 2 | Zero capacidade preditiva/analítica (ML) | -8 | **Persiste integralmente.** Busca exaustiva (`sklearn\|torch\|tensorflow\|model.predict\|risk_score`) em `src/`, `tests/`, `scripts/` retorna zero hits, idêntico ao baseline. Não houve — nem deveria haver neste ciclo de governança/paridade — nenhum trabalho de ML. Continua sendo escolha deliberada e bem fundamentada (ADR-0023), mas o gap competitivo real (Epic EDI 24h, CLEW 8h de lead-time) não mudou nem um milímetro. | **-8** | 0 |
| 3 | Sepse-bandeira servida é a implementação mais pobre das duas (`domain_sepsis.py` código morto) | -7 | **Cai quase inteiramente.** `sepse.yaml` evoluiu de v3.0.0 (7 critérios, sem SIRS/PCT/timers) para **v4.0.0** (15 critérios: os 7 originais + 8 novos portados de `domain_sepsis.py` — screening SIRS/qSOFA, choque séptico, timers de bundle 1h/3h, sequenciamento culturas-antes-ATB, PCT rising/de-escalation). Paridade contra o oráculo `domain_sepsis.py` validada por teste diferencial real, **executado nesta re-auditoria**: `pytest tests/test_sepse_yaml_parity.py -q` → `32 passed, 1 xfailed` (1 xfail documentado, `strict=True`, referente à única lacuna real: tendência delta-lactato/hora, que não é portável por falta de input de lactato anterior no vocabulário declarativo — reconhecida honestamente, não escondida). `domain_sepsis.py`/`/deterioration` permanecem no ar como "release de convivência" (ADR-0035, decisão deliberada, não resíduo esquecido) até um ciclo de depreciação formal. A trilha servida à UI hoje **é** a rica — a UI já lê `sepse.yaml`, então este ganho chega ao intensivista imediatamente, não é apenas um teste passando isolado. | **-1** | +6 |
| 4 | Gaps de cobertura clínica não documentados como decisão consciente (glicemia, transfusão, PAV, TEV/UGE sem escore de risco) | -6 | **Persiste quase integralmente.** Nenhuma trilha nova foi adicionada (glicemia, transfusão continuam com zero ocorrência em qualquer um dos 12 YAMLs, confirmado por grep nesta re-auditoria). `profilaxia.yaml` continua com checagem booleana simples, sem Padua/IMPROVE (confirmado — nenhuma menção a `padua`/`improve`/estratificação de risco no arquivo). `docs/plan/product/product-spec.md` (a seção WON'T-HAVE citada no baseline) não foi tocada neste ciclo (`git log` não mostra commits no arquivo desde antes do ciclo de correção). Não há nova seção "fora do MVP, e por quê" cobrindo estes gaps especificamente. | **-6** | 0 |
| 5 | Quatro contagens de domínio/trilha não reconciliadas (27/9/12/7) | -4 | **Cai parcialmente, não integralmente.** A confusão mais grave — "9 trilhas" no ADR-0031/ADR-0033/`HANDOFF.yaml` G2 vs. 12 arquivos reais — está genuinamente resolvida: ambas as ADRs ganharam notas datadas (`[Reconciliado em 2026-07-12] "9 trilhas" era a contagem... M7 adicionou 3 trilhas... totalizando 12 trilhas YAML ativas hoje`), e o próprio `DIM_A_TRACEABILITY.md` (§4.4, citado pelas notas) investigou e documentou a origem exata da divergência. O README ganhou uma seção nova ("Domínios Clínicos") que nomeia explicitamente e distingue as 3 taxonomias: **25 clusters de regras legadas** (extração), **24 serviços de domínio** (`services/domain_*.py`), **12 trilhas declarativas** (YAML) — isto é exatamente a "fonte única que reconcilia" que a recomendação #5 do baseline pedia. **Ressalva:** persiste uma discrepância residual e nova — `docs/rules/README.md:1066` ainda lista **27** clusters legados (incluindo `cadastros-ui`), enquanto o README principal fala em **25** (a tabela de 25 omite `cadastros-ui`, que aparece só como contrato OpenAPI separado) — um "quase-reconciliado" que introduz uma pequena divergência nova em vez de eliminar a antiga por completo. O "7" de `docs/product/vision.md:38` ("7 domínios clínicos de monitoramento inteligente") também **não foi tocado nem referenciado** pela reconciliação — é um conceito de uma fase de planejamento diferente, mas continua solto sem nota cruzada. | **-2** | +2 |
| 6 | Motor de regras é DSL proprietário não interoperável (sem Arden/CQL/CDS Hooks) | -4 | **Persiste integralmente — mas com uma extensão de expressividade genuína no caminho.** Busca (`grep -rli "arden\|cql\|cds.hooks"`) em `src/` e `docs/adr/` retorna zero hits — nenhuma adoção de padrão HL7. Isso não muda a portabilidade zero para outro EHR via CDS Hooks. **Nuance qualitativa (não pontuada como redução):** o predicado `temporal` declarativo (duração pré-computada vs. orçamento, sem relógio interno) e o combinador `NOT` são uma extensão real de expressividade do motor — mais perto de como Arden/CQL modelam janelas de tempo e negação — mas isso é maturidade da linguagem interna, não interoperabilidade com terceiros. O gap que a dedução original penaliza (não é Arden/CQL, não expõe CDS Hooks) continua verdadeiro ao pé da letra. | **-4** | 0 |
| 7 | Sem validação clínica publicada (sensibilidade/PPV/AUC); feedback loop sem recalibração | -3 | **Cai parcialmente.** `docs/audit/fullspectrum/CLINICAL_SIGNOFF.md` (novo) é uma aprovação clínica formal e datada, assinada como "Médico intensivista / code-owner do repositório", cobrindo especificamente `RAT-SEPSE-V4` ("Paridade validada contra domain_sepsis.py (oráculo, 30/31 vetores)") e outras 6 decisões clínicas do ciclo, mais dois gates de release (G1/G2). Isto é validação clínica de **processo/decisão de design** (um humano credenciado revisou e aprovou as regras codificadas), que é exatamente o tipo de "revisão independente da base da recomendação" que a isenção de CDS da FDA exige (ver §4.3 do baseline) — um ganho real e não trivial. **Mas não é** validação de **desempenho estatístico** (sensibilidade/especificidade/PPV/AUC) das 12 trilhas em dados reais de pacientes, que é o que a dedução original penaliza comparando com Etiometry/CLEW — essa lacuna continua intocada; não há estudo de validação populacional nem recalibração automática de threshold documentada. | **-1.5** | +1.5 |
| **Total perdido** | | **-42** | | **-28.5 (arred. -28)** | **+13.5 (arred. +14)** |
| **Nota final** | | **58/100** | | **72/100** | **+14** |

---

## 3. O que caiu, o que persiste — resumo direto

**Caíram (substancialmente):**
- **#3 — sepse pobre servida.** `sepse.yaml` v4.0.0 tem paridade testada e verificada ao vivo (32 passed, 1 xfail documentado e honesto) com o oráculo rico `domain_sepsis.py`. A UI já consome a versão rica hoje. Este era o achado mais citado do baseline (a "trilha-bandeira do produto é a versão mais pobre") e está, na prática, resolvido.
- **#7 — validação clínica ausente.** Existe agora um sign-off formal, datado, de um intensivista/code-owner cobrindo as decisões deste ciclo (parcial: cobre revisão de decisão, não validação estatística de desempenho).

**Caíram parcialmente:**
- **#5 — contagens não reconciliadas.** O caso mais grave (9 vs. 12) está resolvido com notas cruzadas datadas e uma seção nova de README distinguindo 3 taxonomias. Uma discrepância residual menor (25 vs. 27 clusters legados) e um número solto (7 em vision.md) permanecem sem nota cruzada.
- **#1 — tempo-de-ação não estruturado.** Os timers de bundle SSC-2021 (1h/3h) da sepse são agora dado estruturado real (`type: temporal`), não texto — mas isso vale só para 1 de 12 trilhas; a infraestrutura de schema está pronta para as outras 11, mas a replicação não aconteceu.

**Persistem integralmente (por escolha ou por falta de trabalho neste ciclo, não por lacuna deste ciclo especificamente):**
- **#2 — zero capacidade preditiva/ML.** Não houve, nem deveria ter havido, trabalho de ML num sprint de governança/paridade. Continua sendo o gap competitivo estrutural nº1 do produto.
- **#4 — gaps de cobertura clínica não documentados.** Glicemia e transfusão continuam ausentes de todas as 12 trilhas; profilaxia continua sem estratificação de risco (Padua/IMPROVE); nenhuma nova seção de "fora do escopo, e por quê" foi escrita.
- **#6 — DSL não interoperável.** Zero adoção de Arden/CQL/CDS Hooks. O ganho de expressividade interna (`temporal`/`NOT`) é real, mas não é interoperabilidade — não muda a portabilidade para outro EHR.

---

## 4. O gap nº1 remanescente

**Ausência de capacidade preditiva/lead-time (ML).** É o mesmo gap nº1 do baseline e continua sendo o
mais estruturalmente sério frente aos concorrentes pesquisados (Epic EDI: lead-time mediano ~24h; CLEW:
até 8h, FDA-cleared). Nenhuma correção deste ciclo o tocou — corretamente, dado que o ciclo era de
governança de sepse (paridade, fail-fast, RBAC), não de pesquisa preditiva, e a ADR-0023 já documenta
por que essa é uma escolha deliberada e faseada (threshold determinístico no MVP; ML pós-MVP como camada
consultiva, nunca gatilho único, condicionado a re-registro regulatório). O produto não está pior neste
eixo — só não está melhor. Continua sendo, junto com a extensão incompleta do tempo-de-ação estruturado
para as outras 11 trilhas, a principal fronteira de trabalho restante para fechar a distância frente ao
estado da arte comercial.

---

## 5. Evidência de verificação ao vivo (não apenas leitura de prosa)

- `pytest tests/test_sepse_yaml_parity.py -q` → **`32 passed, 1 xfailed`** (rodado nesta re-auditoria, não apenas citado do ADR).
- `grep -n "type: temporal\|_compile_temporal\|_evaluate_temporal" src/intensicare/services/trilhas_compiler.py` → confirma código real (linhas 256-257, 468-528, 678+), não apenas declaração de ADR.
- `grep -l "type: temporal" _work/alerts/pathways/*.yaml` → só `sepse.yaml` (confirma que o ganho #1 é local, não sistêmico).
- `git show fd4df65 -- docs/adr/ADR-0031-mvp-pathway-sepsis.md docs/adr/ADR-0033-pathway-view-generic-pattern.md` → confirma as notas de reconciliação "[Reconciliado em 2026-07-12]" foram de fato adicionadas, com texto exato citado acima.
- `grep -rn "sklearn|torch|tensorflow|model.predict|risk_score"` em `src/`, `tests/`, `scripts/` → zero hits, idêntico ao baseline.
- `grep -rli "arden|cql|cds.hooks"` em `src/`, `docs/adr/` → zero hits.
- `grep -rn "glicemia|glucose|transfus"` em `_work/alerts/pathways/*.yaml` → zero hits.
- `docs/audit/fullspectrum/CLINICAL_SIGNOFF.md` lido por completo — sign-off datado e nominal, cobrindo 7 decisões clínicas incluindo `RAT-SEPSE-V4`.

---

## Apêndice — Artefatos lidos nesta re-auditoria

- `docs/audit/fullspectrum/DIM_E_INNOVATION.md` (baseline)
- `_work/alerts/pathways/sepse.yaml` (v4.0.0, completo)
- `tests/test_sepse_yaml_parity.py` (completo + execução)
- `docs/adr/ADR-0035-sepsis-declarative-port.md`
- `docs/adr/ADR-0037-pathway-failfast-policy.md`
- `docs/audit/fullspectrum/CLINICAL_SIGNOFF.md`
- `src/intensicare/services/trilhas_compiler.py` (predicados `temporal`/`negate`/`NOT`)
- `README.md` (seção "Domínios Clínicos")
- `docs/adr/ADR-0031-mvp-pathway-sepsis.md`, `docs/adr/ADR-0033-pathway-view-generic-pattern.md` (notas de reconciliação)
- `docs/rules/README.md:1066` (27 clusters — discrepância residual com README principal)
- `docs/product/vision.md:38` ("7 domínios" — não reconciliado)
- `docs/audit/fullspectrum/DIM_A_TRACEABILITY.md` §4.4 (investigação 9 vs. 12, referenciada pelas ADRs)
- `docs/audit/fullspectrum/DIM_D_REAUDIT.md` (referência de formato/metodologia de re-auditoria)
