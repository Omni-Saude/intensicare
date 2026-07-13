# RESPONSIVE FIX REPORT — Remediação Responsiva + Consolidação/Humanização de Alertas
## Ciclo fechado em Chromium real, multi-viewport — 2026-07-13

**Base:** `feat/responsive-alerts-uplift` (empilhado em `fix/e2e-live-runtime`/PR #47)
**Ordem de operação:** [RESPONSIVE_FIX_PROMPT.md](RESPONSIVE_FIX_PROMPT.md) · Matriz: [RESPONSIVE_FIX_MATRIX.md](RESPONSIVE_FIX_MATRIX.md) · Análise: [ALERT_CONSOLIDATION_ANALYSIS.md](ALERT_CONSOLIDATION_ANALYSIS.md) · Decisão: [ADR-0039](../adr/ADR-0039-alert-group-read-aggregation.md)
**Método:** hive-mind — 2 analistas + 20 fix-agents em worktrees isolados + 2 gatekeepers independentes (implementador ≠ revisor) + loop STILL-BROKEN→fix→re-verificação até 100%; toda alegação com prova em browser (screenshot/computed style/axe/estatística).

---

## 1. VEREDITO

**Workstream A (responsivo): 100% da matriz resolvida.** 21 de 23 achados FIXED e re-verificados em 5 viewports (320/375/768/1024/1440); 1 refutado na consolidação (RF-023 — empty-state já existia); 1 adiado por decisão (RF-022, nice-to-have de fonte). axe-core = **0 violations** em 7 telas × 5 viewports (após loop). Zoom 200% (WCAG 1.4.4) PASS. Jornada 320px do intensivista: **9/9 passos PASS** (o único FAIL intermitente foi adjudicado como artefato de seletor posicional do próprio teste — ver §4).

**Workstream B (fadiga + humanização): entregue ponta a ponta com invariantes clínicos provados.**
- **Fadiga na CRIAÇÃO: −81%** — o burst de seed que gerava 53 alertas gera 10 (raiz: `cooldown_minutes` 0→15 no seed; o gate anti-burst de `alert_engine.py:77` estava desligado por config).
- **Fadiga na APRESENTAÇÃO:** /alerts default 12 alertas → **9 grupos**; DEMO-001 filtrado 5 → **2 grupos**; painel do paciente com rollup ("● Crítico · MEWS · 3 ocorrências" + badge "Escalando").
- **Humanização viva:** título curto na linha ("NEWS2 crítico — 17"), corpo 3-partes no expandir (o que aconteceu / por que importa / o que verificar) com referências extraídas do código (RCP 2017, Subbe QJM 2001); testes por score×banda.
- **Invariantes verificados no browser:** zero perda de informação (Σ membros = total flat = 19/19); escalação NUNCA suprimida (badge no colapsado, `escalating` na API, chegando sem reload via WS); ack de grupo = N acks individuais auditáveis com confirmação de contagem; máquina de estados intacta (409 real capturado e legível); visão plana preservada como fallback.

---

## 2. MATRIZ — VEREDITO POR RF-ID (gatekeeper GK-RESP, 5 viewports)

18 FIXED diretos + RF-015/RF-021 fechados no loop + RF-019 verificado a 512px (cap `max-w-md` = 448px medido) = **21 FIXED**. Destaques:

| RF | Item | Prova |
|---|---|---|
| RF-001 (CRITICAL, fora da lista do owner) | Pílulas de severidade sem cor (`var()+hex` inválido) | `color-mix()` válido computado nos 5 viewports; tokens `--severity-*-ring` criados |
| RF-002..006 (QW-1..5) | stats-bar wrap · state-flow região focável · focus trap drawer · labels QuickActions · stacked-table mobile | 14/14 checks + trap cíclico Tab/Esc/retorno medidos |
| RF-007 | Críticos primeiro no grid | Ordem `Crítico×6→Urgente→Observação→Normal` nos 5 viewports |
| RF-008..015 | `text-[10px]`/`text-[8px]` → token `text-2xs` (11px rem) | font-size 11px computado; token de 8px deliberadamente rejeitado |
| RF-016/017 | Padding móvel + hit-areas 40×40px | Bounding boxes medidos |
| RF-018 | Severidade sem cor (daltonismo) | 4 níveis distinguíveis: tamanho+anel+pulso (closeups) |
| RF-020 | Troca de filtro sem flash | `keepPreviousData` + skeleton gateado (prova com API throttled) |
| RF-021 | Fade de overflow | Dupla causa: regra ausente do bundle (cache Turbopack — rebuild) + fade permanente lavando pílula sem overflow (regressão flagrada pelo orquestrador) → `ResizeObserver` condicional; provado nos 2 casos |

## 3. LOOP DE GATEKEEPING (achados novos além da matriz — todos fechados)

| Achado | Causa raiz | Fix | Prova |
|---|---|---|---|
| NOVO A: contraste 4.48:1 no badge de grupos em escalação | **Dois washes 16% empilhados** compõem `#522b31` sob `#ff7077` (conta no commit) | Fundo sólido `--severity-critical` + texto `#0a0e14` = **7.22:1** | axe 0 em /alerts nos 2 viewports |
| NOVO B: contraste da tab Thresholds | **REFUTADO** — luminância calculada à mão = 5.64:1 (bate com cálculo do ciclo anterior); axe ao vivo = 0 em /admin | nenhum (instabilidade de medição do axe entre viewports) | — |
| NOVO C: "botão travado" pós-ack (~25%) | **Refutado como corrida de produto**: (a) backend nunca publica `alert.updated` (eco impossível); (b) o seletor posicional do teste re-resolvia para o irmão após mutação do DOM — artefato determinístico. **Porém** havia defeito latente real: Map otimista sem limpeza + GET incondicional podendo gravar dado stale | Migração ao padrão canônico SWR (`mutate(fn, {populateCache, revalidate:false, rollbackOnError})`), sem GET de eco | 0 falhas / 30 tentativas válidas (id-keyed), ≤250ms; artefato reproduzido idêntico pré/pós-fix |
| GK-ALERTS #1: linha compacta mostrava o corpo, título só no trace (inverso do ADR §6) | Integração UI ficou atrás do backend | Swap title/message + corpo `whitespace-pre-line` no expandir | Screenshots nas 2 visões × 2 larguras |
| GK-ALERTS #2: painel do paciente sem rollup + `limit:50` global pré-filtro | `fetchAlerts` flat + filtro client-side; `mpi_id` nunca exposto no client (gap de wiring) | `fetchAlertGroups({mpi_id})` server-side + painel agrupado (count=1 renderiza item puro) | Screenshot rollup DEMO-002 verificado pelo orquestrador |
| RF-015 (loop): dígito 11px estourava círculo 12px | Sweep de 6 variantes: `leading-none` JÁ vencia; causa era caixa intrínseca do glifo | `size-3.5` (14px) | Contenção medida (0px overflow) |

## 4. FORENSE E REFUTAÇÕES (valor institucional)

A operação **corrigiu as próprias auditorias** em 5 pontos: WCAG 2.5.8 AA exige 24px (não 44px — os alvos de 28px já passavam; melhorados a 40px por ergonomia); RF-023 empty-state já existia; NOVO B era instabilidade do axe; o FAIL do passo 9 da jornada era seletor do teste; e a prescrição da matriz para tokens Tailwind v4 usava namespace inexistente (`--font-size-*` → corrigido para `--text-*` contra o pacote instalado). Gatekeeping adversarial + medição direta > confiança em relatório, inclusive nos nossos.

## 5. GATES FINAIS

- Suíte completa: **2975+ passed / 0 failed / 0 errors** (ver §7 do PR); tsc limpo; eslint 0 erros nos arquivos tocados; ruff check/format limpos; drift de contrato 87/87 PASS (endpoint `group_by` contratado do `app.openapi()` vivo).
- Console: 0 pageErrors em ~20 execuções de verificação (warnings de 1ª conexão WS = padrão conhecido de dev/StrictMode).

## 6. BACKLOG DOCUMENTADO (não são regressões)

RF-022 (nice-to-have de fonte em alert-row); campo estruturado `unit` em `Alert`/`AlertResponse` (perdido do corpo humanizado — follow-up de contrato); resolve de grupo (POR DESIGN individual — exige enum por alerta, ADR §4); fade por borda com posição de scroll (avaliado e rejeitado como complexidade sem ganho); label mobile "Mensagem" agora rotula o título (cosmético); opção (i) do ADR (dedup na escrita/`occurrence_count`) como evolução futura; atualizar `debug-ack5-ab.mjs` do gatekeeper para seletores id-keyed.

## 7. FLYWHEEL — para o próximo ciclo de auditoria

As 4 dimensões auditadas devem ser re-medidas pelos auditores originais contra este branch: layout multi-viewport (era 6 violações → 0 pendentes), DS governance (hardcodes de cor/fonte → tokens; 2 tokens novos documentados), a11y responsiva (axe 0 × 35 células tela/viewport; teclado 320px completo), UX 320px (jornada 9/9; críticos-primeiro; sem flash de filtro). Métrica de fadiga de alertas passa a ser re-medível por script (`group_by=signal` na API + contagem de itens default).
