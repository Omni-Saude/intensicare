# PROMPT — Remediação Responsiva Completa do IntensiCare frontend-v3 (ciclo fechado, browser real multi-viewport)
## Dos 4 relatórios de auditoria responsiva a 100% das violações corrigidas na raiz e re-verificadas

**De:** Owner (via orquestração Claude Fable 5)
**Para:** Orquestrador (hive-mind queen) — sessão de remediação responsiva
**Data:** 2026-07-13
**Tipo:** Correção de código + re-verificação em Chromium real em 5 viewports (ciclo fechado)
**Status:** RASCUNHO APROVADO — não executar até ordem do owner.

---

## ═══════ ENVELOPE ═══════

| Campo | Valor |
|-------|-------|
| **Goal** | (A) Corrigir NA RAIZ 100% das violações registradas nos 4 relatórios de auditoria responsiva e provar cada correção em Chromium real nos 5 breakpoints auditados (320/375/768/1024/1440), com re-medição das matrizes de conformidade. (B) Reduzir fadiga de alertas por CONSOLIDAÇÃO por paciente (análise profunda → agrupamento/rollup sem perda de informação clínica) e HUMANIZAR a linguagem dos alertas (texto natural e explicativo: o que aconteceu, por que importa, o que verificar), ponta a ponta (backend → UI), provado no browser. |
| **Contexto** | `frontend-v3` (Next.js 16, Tailwind, DS próprio com tokens em `app/globals.css`) no `main` pós-PRs #45/#47. Stack local: backend :8000, frontend :3000 (ver E2E_HANDOFF.yaml). Harness Playwright hydration-safe e script de sweep axe parametrizado já existem no scratchpad da sessão E2E (reutilizar/replicar padrões). |
| **Insumos** | EXATAMENTE estes 4 arquivos (o diretório contém outros relatórios v1/v2 de ciclos distintos — IGNORÁ-LOS): `frontend-v3/audit-results/responsive-audit.md` (matriz 5 breakpoints × 5 dimensões), `responsive-ds-governance.md` (validação V1–V6 + conformidade DS), `responsive-a11y-review.md` (WCAG 1.4.4/2.5.8/1.3.1/2.1.1 por issue), `responsive-ux-review.md` (score Nielsen + jornadas 320px/split-screen). |
| **Constraints** | Sem workarounds: causa raiz sempre (token do DS, não px hardcode; padrão APG, não `tabIndex` solto; labels semânticos, não CSS-only). 1 fix-agent por grupo de mecanismo, ≤3 arquivos/agente, worktree isolado por agente escritor. Nenhuma mudança de comportamento clínico. `tsc --noEmit`, eslint nos arquivos tocados e suíte local devem permanecer verdes. |
| **Done-When** | (1) Matriz consolidada de violações 100% em FIXED com evidência por viewport (screenshot antes/depois + axe); (2) matrizes dos 4 relatórios re-medidas por gatekeeper que não implementou; (3) axe = 0 violations nos 5 breakpoints nas telas afetadas, incluindo zoom 200% (WCAG 1.4.4); (4) jornada 320px do intensivista (responsive-ux-review §1) reproduzida PASS; (5) Workstream B: métrica de fadiga medida antes/depois (itens visíveis em /alerts e no painel do paciente para o dataset seed), consolidação provada no browser SEM perda de informação (todo alerta original alcançável), textos humanizados renderizados e cobertos por teste; (6) PR aberto para `main` com relatório `RESPONSIVE_FIX_REPORT.md`; (7) memória do projeto atualizada. |
| **Risk** | L2 — altera componentes de UI compartilhados; dev server local; sem produção. |

---

## ═══════ REGRAS DE OURO (herdadas das sessões E2E/estabilização — LEIA) ═══════

1. **Você orquestra, agentes executam.** Roteamento: Haiku para mudanças mecânicas 1-linha bem especificadas; Sonnet para diagnóstico/implementação/gatekeeping; você adjudica conflitos entre relatórios e sintetiza.
2. **Worktrees isolados** para todo agente que escreve código (`git worktree add <scratchpad>/wt-X -b fix/<slug> <branch-base>`); NUNCA troque de branch no checkout principal com agentes ativos; NUNCA `git stash` (é global entre worktrees).
3. **NUNCA confie em self-report**: após cada agente, verifique commit/diff/grep no filesystem você mesmo; evidência visual re-inspecionada pelo orquestrador nas peças-chave.
4. **Gatekeeper ≠ implementador**, e a prova é o BROWSER em CADA viewport alvo — não o diff, não o tsc. Lint estático de JSX (Edge Tools/webhint) NÃO é evidência: já produziu falso-positivos E mascarou bugs reais; use axe em runtime.
5. **Auditoria ≠ verdade absoluta**: os 4 relatórios podem conter achados desatualizados (código mudou nos PRs #45/#47 — ex.: `alert-row`/tablist/breadcrumb já foram reestruturados), duplicados entre si ou tecnicamente errados. FASE 0 adjudica cada achado contra o código ATUAL antes de despachar fixes. Achado já corrigido = marcar OBSOLETO com evidência, não re-corrigir.
6. **Processos longos** (suíte completa, sweeps): sempre com output redirecionado a arquivo + acompanhamento por `until grep`; nunca deixe um agente estagnar no watchdog. pytest concorrente no mesmo Postgres de teste gera falhas-fantasma de DDL race — serialize ou isole DB.
7. **Estado no filesystem**: matriz consolidada, relatório final e handoff em `docs/audit/` (versionáveis). Screenshots/artefatos no scratchpad, referenciados por caminho.

---

## ═══════ FASE 0 — CONSOLIDAÇÃO E ADJUDICAÇÃO (você + 1 agente leitor) ═══════

1. Leia os 4 relatórios e produza a **MATRIZ CONSOLIDADA** (`docs/audit/RESPONSIVE_FIX_MATRIX.md`): uma linha por violação única com — ID canônico (RF-001…), arquivo:linha ATUAL (re-localizar: o código mudou desde a auditoria), viewport(s) afetado(s), regra violada (WCAG x.x.x / token DS / heurística Nielsen), severidade adjudicada (CRITICAL = bloqueia uso clínico no viewport; MAJOR = degrada; MINOR = polish), relatórios de origem (dedupe: V2 do ds-governance == §3.3 do a11y == §3 do ux → 1 linha, 3 fontes), prescrição técnica de 1 frase, e status inicial (PENDING/OBSOLETO-com-evidência).
2. Casos de adjudicação obrigatória: (a) `StateFlow` — se o componente for somente-leitura, a prescrição correta é semântica de lista/scroll acessível, NÃO `tabIndex={0}` cego (foco em elemento não-interativo viola boas práticas); decida pelo código real; (b) `text-[10px]` — a prescrição é token de escala tipográfica do DS com unidade relativa (rem) que sobreviva a zoom 200%, não "trocar 10 por 12 hardcoded"; (c) touch targets — medir o alvo REAL renderizado (padding incluso), não o ícone.
3. Anexe à matriz o **plano de agrupamento por mecanismo** (Fase 2) com colisões de arquivo mapeadas (dois grupos não tocam o mesmo arquivo; senão, funde ou sequencia).

**Gate de saída da FASE 0:** matriz revisada por você, com contagem total declarada (N violações: X CRITICAL / Y MAJOR / Z MINOR / W OBSOLETO).

---

## ═══════ FASE 1 — QUICK-WINS NOMEADOS (1 agente, 1 worktree, ≤5 arquivos por exceção justificada) ═══════

As 5 ações imediatas do owner — implementar com a forma CORRETA de cada uma, não a literal:

| # | Alvo | Ação | Forma correta exigida |
|---|------|------|----------------------|
| QW-1 | `components/dashboard/stats-bar.tsx` | wrap responsivo | `flex-wrap` + gap coerente com tokens; verificar que a ordem de leitura (DOM) continua fazendo sentido ao quebrar linha em 320px |
| QW-2 | `components/pathway/state-flow.tsx` | alcançabilidade por teclado | Conforme adjudicação da FASE 0: se somente-leitura, container rolável focável com `role` adequado + `aria-label` (padrão WAI para regiões roláveis); se interativo, padrão APG completo — `tabIndex={0}` NUNCA sozinho |
| QW-3 | `components/app-shell.tsx` | focus trap no drawer/sidebar mobile | Reusar o padrão de trap já existente no app (dialog de atalhos / CreateUserDialog): Tab cíclico, Esc fecha, foco retorna ao trigger, `aria-modal` quando overlay |
| QW-4 | QuickActions (localizar em `components/alerts/`) | rótulos visíveis em mobile | Remover `hidden sm:inline` dos labels OU garantir alternativa acessível equivalente por viewport — decidir pela densidade da tela em 320px medida no browser; nunca ícone-só sem `aria-label` |
| QW-5 | `components/alerts/alert-table.tsx` | dados compreensíveis <sm | Labels inline por célula no mobile (padrão "stacked table" com cada valor rotulado), preservando a semântica de lista/tabela para AT — o header `hidden sm:flex` não pode ser a única fonte de significado (WCAG 1.3.1) |

Verificação do agente: `tsc --noEmit` + eslint nos arquivos tocados + screenshot próprio em 320px e 1440px por item. Gatekeeper re-verifica na FASE 3.

---

## ═══════ FASE 2 — REMEDIAÇÃO TOTAL POR MECANISMO (swarm em worktrees, paralelo onde sem colisão) ═══════

Agrupamento previsto (ajustar pela matriz da FASE 0; 1 agente por grupo; ≤3 arquivos ou dividir):

- **G-TYPO** — tipografia fora da escala do DS (`text-[10px]`, `text-[Npx]`, `text-[Nrem]` arbitrários; M1–M16 do ds-governance): migrar para tokens de escala tipográfica (criar o token que faltar em `globals.css`/config Tailwind — mudança de DS é 1 arquivo + consumidores), garantindo rem-based e legível a zoom 200%.
- **G-TOUCH** — touch targets < 44×44 (WCAG 2.5.8/2.5.5): corrigir por padding/hit-area nos componentes apontados; medir o alvo renderizado no browser.
- **G-LAYOUT** — quebras de integridade por breakpoint apontadas na matriz 5×5 do responsive-audit (overflow, colisão, truncamento não intencional): fix por container/grid com tokens de spacing.
- **G-DS** — dívidas de governança restantes (ex.: N4 alpha-blending em `state-label.tsx`, width/height px fixos M13–M18): resolver via tokens/utilitários do DS; PROIBIDO introduzir novo hardcode.
- **G-UX-320** — achados da jornada 320px noturna e split-screen (~512px) do ux-review que não caírem nos grupos acima (densidade, hierarquia de criticidade, carga cognitiva): cada um com prescrição própria da matriz.

Regras por agente: bug pré-carregado (linha da matriz + screenshot do relatório), fix na raiz, commit no worktree, self-check tsc/eslint + screenshot local. Nenhum agente altera contrato de API ou comportamento clínico.

---

## ═══════ FASE 2B — WORKSTREAM B: CONSOLIDAÇÃO DE ALERTAS + HUMANIZAÇÃO (paralelo à FASE 2; swarm próprio) ═══════

Motivação clínica: fadiga de alertas é risco de segurança do paciente — o dataset seed já produz ~53 alertas para 5 pacientes; um intensivista em plantão dessensibiliza. Dois eixos, ambos ponta a ponta (backend → UI), com prova no browser.

### 2B.0 — Análise profunda (1 agente analista; NÃO escreve código)
1. **Inventário do dado real**: via API/DB do ambiente seed, distribuição de alertas por paciente/tipo/severidade/status; sobreposição temporal; quantos são o MESMO sinal clínico re-disparado (ex.: NEWS2 crítico recalculado a cada ingestão) vs sinais distintos.
2. **Inventário do código**: caminho único de criação (`alert_engine.check_score_against_thresholds`), campos existentes de correlação (`dedup_key` — PARSEADO MAS NUNCA APLICADO, achado C#14 das auditorias; `correlation-engine.yaml` e vetores TV-* em `tests/rules/`), modelo `Alert` (colunas disponíveis p/ agrupar), contrato `alerts-openapi.yaml`, componentes de UI (`alert-table/alert-row/filter-bar/alerts-panel`).
3. **Entregável**: `docs/audit/ALERT_CONSOLIDATION_ANALYSIS.md` com métrica de fadiga BASELINE (itens visíveis em /alerts default e no painel do paciente, por paciente), taxonomia dos duplicados, e 2–3 desenhos de consolidação com trade-offs — para adjudicação do orquestrador ANTES de qualquer implementação.

### 2B.1 — Consolidação (após adjudicação; agentes backend + frontend em worktrees separados)
Requisitos invioláveis (segurança clínica):
- **Zero perda de informação**: todo alerta original permanece persistido, auditável e alcançável pela UI (grupo expansível / trilha de detalhe). Consolidação é de APRESENTAÇÃO e de re-disparo, nunca de descarte.
- **Escalação sempre fura o rollup**: um sinal que PIORA (severidade sobe, novo tipo crítico) gera destaque novo imediato; rollup só comprime repetição do MESMO sinal em severidade igual/menor.
- **Estado clínico ≠ estado de notificação**: ack/resolve de um grupo exige semântica explícita (ack do grupo = ack de todos os membros? decidir na adjudicação com registro em ADR curto).
- Backend: aplicar finalmente o `dedup_key`/correlação no ponto único de criação (atualizar alerta aberto do mesmo sinal em vez de criar N iguais — com `occurrence_count`/`last_seen_at` — OU agregação na leitura; decidir no 2B.0 pela opção de menor risco/contrato). Contrato: mudanças em `alerts-openapi.yaml` regeneradas do `app.openapi()` + drift check verde.
- Frontend: /alerts agrupado por paciente (grupo com nome, contagem, severidade máxima, expandir para membros — reusar padrão disclosure APG já implementado no ciclo anterior); painel do paciente com rollup coerente; WebSocket `alert.raised` continua funcionando com grupos.
- Métrica de fadiga re-medida DEPOIS (mesmo dataset): alvo = redução material de itens default visíveis (reportar número exato antes/depois), sem esconder nenhum crítico ativo.

### 2B.2 — Humanização da linguagem (agente de copy clínico + agente backend; worktrees separados)
- Substituir títulos/corpos crus (ex.: `"NEWS2 CRITICAL: 10"`) por template natural e explicativo em PT-BR clínico, no padrão já validado do card CDS: **o que aconteceu** (sinal + valor + tendência), **por que importa** (interpretação clínica curta, ex.: "NEWS2 ≥ 7 indica risco elevado de deterioração"), **o que verificar** (próxima ação objetiva). Campos estruturados continuam disponíveis (título curto para listas densas + corpo explicativo).
- Fonte da verdade dos textos: templates centralizados no backend (junto do ponto de criação/threshold config), parametrizados por score/severidade/valores — NUNCA string solta espalhada; cobertos por teste unitário (um por score type × banda).
- Tom: sóbrio, clínico, sem alarmismo nem diminutivos; terminologia consistente com os pathways/recomendações existentes; revisão de consistência pelo gatekeeper.
- UI: renderização do corpo explicativo no expandir do alerta (não inflar a linha compacta — densidade importa em mobile, amarrar com QW-4/QW-5).

### Gates do Workstream B
`tsc`/eslint/suíte verdes (incluindo testes novos de consolidação + templates); drift de contrato verde; gatekeeper dedicado prova no browser: grupo expande para membros, escalação fura rollup, ack de grupo com semântica adjudicada, textos humanizados renderizados, WebSocket vivo, e a métrica antes/depois documentada.

---

## ═══════ FASE 3 — GATEKEEPER MULTI-VIEWPORT (agentes que NÃO implementaram) ═══════

Após integração dos worktrees num branch único (você integra, resolve colisões, roda gates):

1. **Sweep responsivo**: Playwright em 320×568, 375×667, 768×1024, 1024×768, 1440×900 — para CADA tela afetada (dashboard, patient, pathway, alerts, admin, login): screenshot + axe.run() por viewport + verificação específica de cada RF-ID da matriz (o elemento corrigido, no viewport onde falhava). Zoom 200% (emular com viewport/2 ou page.zoom) nas telas com achados WCAG 1.4.4.
2. **Teclado em mobile**: jornada core operável por teclado no viewport 320 (drawer com focus trap QW-3, StateFlow QW-2, tablist já corrigida no ciclo anterior — provar que não regrediu).
3. **Jornada 320px do intensivista** (responsive-ux-review §1) reproduzida passo a passo com evidência.
4. Veredito por RF-ID: FIXED / STILL-BROKEN / REGRESSION. STILL-BROKEN volta para a FASE 2 (novo agente, contexto do gatekeeper). **Loop até 100% FIXED ou reclassificação justificada por você.**
5. Regressão funcional: rodar a suíte local completa 1× (deve manter 2930+ passed / 0F / 0E) + `axe-sweep` desktop do ciclo anterior (deve manter 0 violations).

---

## ═══════ FASE 4 — FLYWHEEL DE FECHAMENTO (você) ═══════

1. `docs/audit/RESPONSIVE_FIX_REPORT.md`: matriz final com veredito por RF-ID + evidências, before/after das matrizes dos 4 relatórios (re-medidas), débitos reclassificados com justificativa.
2. PR para `main` (branch protection: deixar pronto para review humana; CI required verde; NUNCA force-merge).
3. Memória do projeto: atualizar `e2e-live-verification` ou criar `responsive-fix-cycle` com achados duráveis (padrões de DS criados, decisões de adjudicação, armadilhas novas).
4. Flywheel: registrar no relatório o delta de score (matriz 5×5, WCAG matrix, Nielsen, DS conformidade) para alimentar o próximo ciclo de auditoria — auditar → triagem → fix isolado → gatekeeper browser → integrar → documentar → memorizar → re-medir.

---

## ═══════ ANTI-PATTERNS (desta base — NÃO REPETIR) ═══════

- ❌ `tabIndex={0}` em elemento sem role/handler — teatro de acessibilidade.
- ❌ Trocar `text-[10px]` por `text-[12px]` — o hardcode É a violação; a correção é token.
- ❌ Esconder informação clínica para "caber" no mobile sem alternativa acessível equivalente.
- ❌ Confiar em lint estático de JSX como veredito de a11y (falso-positivos E falso-negativos comprovados) — axe em runtime decide.
- ❌ Re-corrigir achado OBSOLETO sem checar o código atual (os PRs #45/#47 já mexeram em alert-row, tablist, breadcrumb, contraste, headings).
- ❌ Orquestrador codando; gatekeeper = implementador; agente com >3 arquivos; `git stash`; troca de branch no checkout principal com agentes ativos.
- ❌ Processo longo em foreground sem log em arquivo (estagna watchdog); pytest concorrente no mesmo DB.
- ❌ Screenshot desktop como prova de fix mobile — a prova é NO viewport da violação.

---

## ═══════ REFERÊNCIAS RÁPIDAS ═══════

- Stack: backend `.venv/bin/uvicorn intensicare.main:app --port 8000 --app-dir src` (sem `--reload`); frontend `cd frontend-v3 && npm run dev`; seed `make seed-demo`; credenciais admin/admin (login form-urlencoded).
- Harness Playwright hydration-safe + sweep axe parametrizado: padrões em `scratchpad/e2e-live/harness.mjs` e `axe-sweep.mjs` da sessão E2E (replicar se o scratchpad tiver expirado; o axe-core vem de `frontend-v3/node_modules/axe-core`).
- Tokens do DS: `frontend-v3/app/globals.css` (`--severity-*`, `--surface-*`, `--text-*`, `--border-*`); breakpoints Tailwind padrão (`sm:640 md:768 lg:1024 xl:1280`).
- Gates: `npx tsc --noEmit` (frontend-v3), eslint por arquivo, suíte `PYTHONPATH=src .venv/bin/python -m pytest tests/ -q --no-cov` (baseline: 2930 passed/0F/0E), drift `scripts/ci/check_openapi_drift.py` (se tocar contrato — não deveria).
- Pacientes-chave: DEMO-001 (sepse critical), DEMO-002 (sedação urgent), DEMO-004 (normal), LEITO-06 (stale 16d, banner de staleness — não regredir).
