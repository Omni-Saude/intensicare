# FULLSPECTRUM_VERDICT — Auditoria Full-Spectrum IntensiCare

**Orquestrador/Gatekeeper:** Claude (Fable 5) — síntese independente dos 5 relatórios dimensionais
**Data:** 2026-07-12
**Método:** 5 agentes auditores independentes (relatórios em `docs/audit/fullspectrum/DIM_*.md`) + verificação adversarial de 5 achados pivotais por agente verificador independente + cross-validation pelo orquestrador. Nenhum achado pivotal aceito por self-report.

---

## 1. Scoring Summary

| Dimensão | Nota | Peso | Nota Ponderada |
|----------|------|------|----------------|
| A — Rastreabilidade Produto→Spec | 58/100 | 15% | 8.70 |
| B — UX e Jornada | 78/100 | 30% | 23.40 |
| C — Backend (correção clínica) | 46/100 | 25% | 11.50 |
| D — Integração Frontend↔Backend | 72/100 | 20% | 14.40 |
| E — Inovação e Diferenciação | 58/100 | 10% | 5.80 |
| **TOTAL** | | | **63.8/100** |

## 2. Veredito: 🔴 **NO-GO** (63.8 < 70)

A plataforma **não está pronta para produção clínica**. A decisão não é marginal: as duas dimensões de maior peso clínico direto (Backend 46, Rastreabilidade 58) carregam achados CRITICAL verificados de forma independente que tocam patient safety — fórmula de score divergente da literatura na direção que mascara gravidade, critérios clínicos silenciosamente mortos, estado clínico volátil, e zero validação por médico real.

O NO-GO **não significa** que o produto seja ruim em concepção. A UX (78) valida a tese do rebuild v3 — jornada em 2 cliques, densidade correta, zero páginas standalone — e a Dimensão E confirma um diferencial de produto genuíno e defensável. O problema é o núcleo clínico do motor: exatamente a parte que precisa estar certa antes de qualquer paciente real.

---

## 3. Top 10 Achados (CRITICAL primeiro, cross-validados)

| # | Sev | Achado | Evidência | Dimensões convergentes |
|---|-----|--------|-----------|------------------------|
| 1 | 🔴 CRITICAL | **Critérios clínicos silenciosamente mortos**: RASS (delirium) e RASS+BPS (sedação) falham na compilação (banda final com range fechado `[1, 5]` em vez de aberto) e são descartados com apenas `logger.warning` — esses pathways **nunca disparam alerta** em produção, sem sinalização operacional. | `sedacao.yaml:53`, `delirium.yaml` (crit-del-agitacao), `trilhas_engine.py:283-297`. **Verificado independentemente ✅** | C (achados 2+9); mecanismo de engolimento de erro é sistêmico |
| 2 | 🔴 CRITICAL | **MEWS diverge da literatura (Subbe 2001) na direção clinicamente perigosa**: Temp=38.5°C exata pontua 1 em vez de 2 — subestima febre exatamente no limiar de escalada; estrutura de bandas de temperatura inteira difere; FC=40 off-by-one. Testes unitários certificam o comportamento errado. | `services/mews.py:151` (`elif value <= MEWS_TEMP_MILD_FEVER_MAX: pts = 1`), `:145-154`, `:68-79`; `tests/test_mews.py:33,127`. **Verificado ✅** | C (achado 1) |
| 3 | 🔴 CRITICAL | **A trilha-bandeira (sepse, MVP/benchmark por ADR-0031) servida ao usuário é a implementação mais pobre das duas existentes**: `domain_sepsis.py` (SIRS, PCT stewardship, timers de bundle SSC-2021, 31 vetores de teste) só é alcançável via `api/v1/deterioration.py` — endpoint que **nenhuma das 14 funções do frontend v3 chama**. O Pathway View de sepse consome `sepse.yaml`/TrilhasEngine, sem esses critérios. *Correção do gatekeeper: não é código morto literal (import vivo em `domain_piora_clinica.py:46` → `deterioration.py:25`), mas é inalcançável pela superfície de produto pathway-centric.* | `DIM_A` §achado 2; cadeia de imports verificada pelo orquestrador ✅ | A + E convergem; D confirma que /deterioration não está em lib/api.ts |
| 4 | 🔴 CRITICAL | **Motor de trilhas não validável e volátil**: 0 pathways ativos em 7/7 pacientes; `pathways`/`patient_pathways`/`pathway_criteria` vazias no Postgres (verificado em 3 pacientes ✅); estado de enrolamento/transições vive num `dict` Python (`trilhas_state.py`) perdido a cada restart. O coração do produto nunca foi observado processando um paciente. | `trilhas_state.py:7-19,95-119`; `GET /patients/{mpi_id}/pathways` → `{items:[],total:0}` ×7 | A (achado 4) + C (achados 3+4) + D (consistência) — convergência tripla |
| 5 | 🔴 CRITICAL | **Zero validação clínica real**: gates G1/G2 exigiam "Arquiteto + Médico intensivista"; nenhum score clínico registrado; `signoffs: []` vazios; ratificação de 269 decisões feita por personas de IA por delegação. Nenhuma evidência de que um intensivista viu o produto. | `HANDOFF.yaml:200-206`; `panels/*/decision.yaml:48-51`; `ratification-decisions.yaml:2-9` | A (achado 1) + E (nenhuma validação publicada) |
| 6 | 🔴 CRITICAL | **RBAC incoerente em sistema clínico**: enforcement é binário (`is_admin`); campo `role` é inerte (admin roda com `role:"readonly"` e acesso total); `require_abac` chamado com `"admin"` hardcoded; frontend não tem admin guard no cliente. ABAC de 7 papéis clínicos existe mas só cobre `admin.py`. | `auth/dependencies.py:92-123`; `admin.py:182,213,294`; `abac.py:33-43`; JWT real do admin (recon) | Recon + A (achado 3) + C (achados 7+19) + D (AUTH-3) — convergência quádrupla |
| 7 | 🟠 MAJOR | **WebSocket quebrado em 4 camadas** (rota `/ws` vs `/api/v1/ws`; sem `?token=`; `{type:"auth"}` vs `{action:"subscribe"}`; envelope de eventos incompatível): "tempo real" não existe — todos os usuários vivem em polling de 30s. Pior do que a baseline WIRING_GAPS reportava (1 camada). | `DIM_D` §3; confirmado ao vivo | D + A (achado 13); baseline do Parreira subestimava |
| 8 | 🟠 MAJOR | **Cadeia de dados stale → telas clinicamente enganosas**: seed com 16 dias de atraso colide com cutoff hardcoded de 24h (`dashboard.py:368-403`) → `vitals:[]`/`scores:[]` sempre; `severity: null` em 5/7 pacientes — paciente com MEWS 13 renderiza **sem cor de severidade**. | `DIM_C` achado 6; `DIM_D` DASH-1 | C + D + B (telas vazias) + recon — convergência quádrupla |
| 9 | 🟠 MAJOR | **Contrato de auth violado + erro 500 onde deveria ser 401**: `LoginResponse.user` sem `name`/`role` (real: `{id, username, email, display_name, is_admin, is_active}` — verificado ✅); Bearer malformado → 500 (`jwt.get_unverified_claims` fora do try, `auth/jwt.py:45`), neutralizando o auto-redirect para /login. | `DIM_D` AUTH-1/AUTH-2; verificação independente do shape ✅ | D; contradiz WIRING_GAPS (que dava #1 como ✅ OK) |
| 10 | 🟠 MAJOR | **Governança de spec furada**: 38% (31/81) dos endpoints vivos sem contrato OpenAPI; 5 operações contratadas nunca implementadas; contagem de domínios não reconciliada (27/12/9/7 em docs distintos); `content_hash` fake nos 12 pathways (rastreabilidade de alerta aponta para hash placeholder). | `DIM_A` achados 6-8; `DIM_C` achado 5; `DIM_E` §5 | A + C + E — convergência tripla |

Menções: WCAG — badge urgente 2.87:1 e logout 3.51:1 (B, CRITICAL/MAJOR dentro da dimensão); ausência total de capacidade preditiva vs Epic EDI/CLEW/Etiometry (E, estruturalmente atrás do mercado); `ventilacao.yaml` stub (C-8).

---

## 4. Cross-Validation (convergências que elevaram severidade)

1. **"O motor nunca rodou de verdade"** — A(4) storage volátil + C(3) tabelas vazias + C(4) dict em memória + D(consistência: pathways vazios em runtime) + B(Pathway View sem dados para renderizar). Cinco leituras independentes do mesmo fato estrutural. É o achado mais corroborado da auditoria.
2. **Sepse dual** — A(2) descobriu, E(4) reconfirmou por ângulo de produto, D confirma que a superfície v3 não alcança a versão rica, gatekeeper corrigiu o alcance ("morto" → "inalcançável pela UI"). 
3. **RBAC** — recon (JWT anômalo) + A(3) + C(7,19) + D(AUTH-3). Quatro fontes.
4. **Staleness → dado clínico enganoso** — recon + C(6) + D(DASH-1) + B(caveat). O que parecia "dados velhos" (operacional) é na verdade **severidade nula em pacientes MEWS 13** (clínico).
5. **Self-reports internos otimistas** — WIRING_GAPS dizia 13/14 OK; D re-testou e achou MISMATCH no próprio login + 500 em token malformado + WS 4× pior. HANDOFF dizia "all milestones completed" com WCAG 88/100; B achou 1 CRITICAL de contraste novo e 3 gaps herdados abertos. Lição de processo: gates auto-reportados sem revisor independente não seguram qualidade.

**Divergência resolvida pelo gatekeeper:** o verificador rotulou o Claim 5 (login sem name/role) como "refutado", mas sua própria evidência lista `user` sem `name` e sem `role` — o achado de D está **confirmado**; o rótulo do verificador foi erro de leitura. Claim 2 ("código morto") foi o único parcialmente refutado, e o veredito incorpora a correção sem alterar a severidade clínica do achado.

---

## 5. Recomendações Acionáveis (CRITICAL/MAJOR → dono → milestone)

| Achado | Ação | Dono sugerido | Milestone |
|--------|------|---------------|-----------|
| #1 Critérios mortos | Corrigir bandas finais (`[1, null]`) em sedacao/delirium; **fail-fast na compilação** (erro → pathway inativo + alerta operacional, nunca warning silencioso); validar os 12 YAMLs contra `pathway.schema.json` no CI | Backend/Trilhas | **M7 (imediato)** |
| #2 MEWS | Corrigir bandas de temperatura para Subbe 2001 (38.5 → 2 pts; 3 bandas); corrigir testes que certificam o erro; revisão médica assinada de TODAS as tabelas de score | Backend + Médico | **M7 (imediato)** |
| #4 Motor volátil | Migrar `trilhas_state.py` para as tabelas ORM já existentes; seed de enrolamentos + progress; rodar 1 paciente sintético ponta-a-ponta como teste de aceitação | Backend | **M7** |
| #6 RBAC | Tornar `role` efetivo (remover override incondicional de `is_admin`), remover `"admin"` hardcoded do `require_abac`, adicionar guard de admin no cliente | Backend + Frontend | **M7** |
| #8 Staleness | Pipeline de ingestão ou seed fresco + tratar `severity: null` no frontend (nunca renderizar paciente crítico sem cor) | Dados + Frontend | **M7/M8** |
| #3 Sepse dual | Decisão de arquitetura: ou portar SIRS/PCT/bundle-timers para `sepse.yaml`/engine, ou expor `domain_sepsis` na superfície pathway; eliminar a duplicação | Arquiteto + Médico | **M8** |
| #9 Auth | Alinhar `LoginResponse` (name/role) ou o tipo TS; mover `get_unverified_claims` para dentro do try → 401 | Backend | **M8** |
| #7 WebSocket | Alinhar as 4 camadas (rota, token, handshake, envelope) — já estava prometido para M8 | Frontend + Backend | **M8** |
| #5 Validação clínica | Sessão formal com intensivista real: G1/G2 re-executados com signoff nominal; protocolo de validação das 12 trilhas | Product Owner | **M8/M9 (gate de produção)** |
| #10 Governança | Contratos para os 31 endpoints órfãos; implementar `content_hash` real (SHA-256 do YAML); reconciliar contagem de domínios nos docs | Arquiteto | **M9** |
| WCAG (B) | Corrigir os 3 pares de contraste reprovados; fechar UX-M1 (breadcrumb com nomes) | Frontend | **M8** |
| Preditivo (E) | Roadmap explícito: documentar "regras-primeiro" como decisão (explicabilidade/SaMD) E planejar camada preditiva (lead-time) — é o gap competitivo nº 1 | Product | **M9+** |

## 6. Inovação Real vs Percebida

**A plataforma é genuinamente inovadora na camada de produto — e é exatamente por isso que o NO-GO importa.** Nenhum dos concorrentes pesquisados (Epic Deterioration Index, Philips IntelliVue Guardian, Etiometry, CLEW) organiza a UTI como um conjunto de trilhas de guideline completas renderizadas por um único componente genérico verificadamente data-driven (zero ocorrências de nomes de trilha no código do frontend — `ADR-0033:68` cumprido); todos giram em torno de 1-2 índices únicos. Esse diferencial é real, defensável e incomum. Mas a inovação declarada é "motor de decisão clínica confiável", e hoje o motor: nunca processou um paciente real (tabelas vazias, estado volátil), descarta critérios silenciosamente, e pontua febre errado no limiar de escalada. **A inovação percebida (arquitetura) existe; a inovação entregue (decisão clínica confiável em produção) ainda não.** Com os itens de M7 fechados, a distância entre as duas é curta — a fundação de engenharia (parser, contiguidade de bandas, semântica de intervalos, suppression, SOFA/qSOFA/NEWS2 perfeitos) é sólida.

---

*Relatórios-fonte: `DIM_A_TRACEABILITY.md` (58), `DIM_B_UX.md` (78), `DIM_C_BACKEND.md` (46), `DIM_D_INTEGRATION.md` (72), `DIM_E_INNOVATION.md` (58). Verificação adversarial: 4/5 claims pivotais confirmados, 1 corrigido em precisão (sepse "código morto" → "inalcançável pela superfície de produto").*

---

# ADENDO — VEREDITO REVISADO PÓS-CORREÇÃO (2026-07-12, mesmo dia)

**Contexto:** os gaps automatizáveis do plano aprovado (M7+M8+M9) foram fechados em 3 sprints
automatizados (PRs #40, #41, #42 empilhados) executados por ~40 agentes especialistas com gates
independentes. As dimensões C e D foram **formalmente re-auditadas por agentes novos** com os
protocolos originais (`DIM_C_REAUDIT.md`, `DIM_D_REAUDIT.md`); A, B e E não foram re-medidas
(seus scores originais são mantidos no cálculo primário, por conservadorismo).

## Scoring revisado (primário — conservador)

| Dimensão | Original | Revisado | Peso | Ponderado |
|----------|----------|----------|------|-----------|
| A — Rastreabilidade | 58 | 58 (não re-medida) | 15% | 8.70 |
| B — UX e Jornada | 78 | 78 (não re-medida) | 30% | 23.40 |
| C — Backend | 46 | **80** (re-auditada) | 25% | 20.00 |
| D — Integração | 72 | **93** (re-auditada) | 20% | 18.60 |
| E — Inovação | 58 | 58 (não re-medida) | 10% | 5.80 |
| **TOTAL** | **63.8** | | | **76.5** |

## Veredito revisado: 🟡 **GO-WITH-ISSUES** (76.5, faixa 70–84)

Nota: estimativa secundária ~83 se A/B/E fossem re-medidas (sepse dual resolvida, 82/82 contratos,
contrastes AA, CSP/hidratação, breadcrumb — gaps dessas dimensões materialmente fechados), ainda
GO-WITH-ISSUES. O NO-GO original foi revertido por evidência independente, não por decreto.

## O que foi fechado (verificado por re-auditoria/gates independentes)
- MEWS = Subbe 2001 exata (v3.0.0); critérios RASS/BPS vivos e avaliando paciente real
- Motor de trilhas persistente em Postgres com restart-survival provado; content-hash real 12/12
- Sepse declarativa v4 em paridade com o oráculo (30/31 vetores + 1 xfail estrito documentado)
- WebSocket FUNCTIONAL (evento em ~130ms, 4 camadas alinhadas); CSP nonce → hidratação restaurada
- RBAC efetivo (role real, 403 limpo, backfill); matriz de endpoints 13 FULL_MATCH / 1 PARTIAL / 0 BROKEN
- 82/82 endpoints contratados + drift-check no CI; severidade derivada nunca-null; WCAG AA nos pares críticos

## Pendências (donos humanos)
1. **Sign-off clínico** (bloqueador de produção): MEWS v3 (RAT-MEWS-SUBBE-2001-R2), thresholds 0038,
   sepse.yaml v4, e validação G1/G2 por intensivista real — nenhuma automação substitui isto.
2. **Aprovação dos PRs #40→#41→#42** (code-owner review obrigatória pela branch protection).
3. Dívida documentada fora de escopo: estabilização da suíte de testes no CI (~95 falhas pré-existentes,
   job restaurado a não-bloqueante com documentação), pipeline CDC/ADT (AWS), camada preditiva (roadmap E),
   residuais MINOR das re-auditorias (stub ventilacao.yaml, inputs órfãos em 5 pathways, MPI-001 no dashboard).

## Nota de processo (flywheel)
Gates independentes vetaram 3 vezes (G-S1 poluição de schema; G-S2 severidade inflada + enum; G-S3 rótulo
ambíguo) — todos os vetos eram reais e nenhum sobreviveu ao ciclo de correção. Dois defeitos foram achados
por acidente instrumentado: hidratação quebrada por CSP (mascarada desde M8) e boot quebrado mascarado por
`--reload` stale. Regra nova: gates devem incluir **import fresco do app** (o drift-check do CI já o faz).
