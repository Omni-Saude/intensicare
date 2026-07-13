# 🛡️ DS Governance — Re-Auditoria v2 (flywheel, pós-uplift)

**Data:** 2026-07-13
**Auditor:** Hermes Agent (DS Guardian / Gatekeeper) — rodada v2
**Fonte validada (v1 deste mandato):** `responsive-ds-governance.md` (Hermes, mesma data, score 88.0/100)
**Baseline de hardcodes pré-existentes:** `ds-governance-v2.md` (10/Jul, 89 arquivos, M1–M16 + N1–N44)
**Branch:** `feat/responsive-alerts-uplift`
**Escopo:** re-medição estática (grep/read, sem browser) do código ATUAL contra as 6 violações V1–V6 + varredura completa de hardcodes + avaliação dos 3 tokens novos do ciclo
**Metodologia:** idêntica à v1 — leitura direta dos arquivos fonte, grep exaustivo, cruzamento com `globals.css` e histórico git dos commits do ciclo

---

## 1. Score de Conformidade — v1 → v2

| Categoria | v1 (13/Jul manhã) | v2 (13/Jul, pós-uplift) | Peso | Nota v1 | Nota v2 | Δ |
|---|---|---|---|---|---|---|
| Cores (uso de tokens `var(--*)`) | 99/100 | **98/100** | 30% | 29.7 | 29.4 | −0.3 |
| Tipografia (ausência de `text-[Npx]`) | 62/100 | **79/100** | 25% | 15.5 | 19.75 | +4.25 |
| Spacing (uso de escala Tailwind) | 95/100 | **94/100** | 15% | 14.3 | 14.1 | −0.2 |
| Breakpoints responsivos | 100/100 | **100/100** | 15% | 15.0 | 15.0 | 0 |
| Padrões de layout (grid, wrap, overflow) | 90/100 | **92/100** | 15% | 13.5 | 13.8 | +0.3 |
| **TOTAL** | | | | **88.0** | **92.05 / 100** | **+4.05** |

**Leitura:** o ganho é quase inteiramente em Tipografia (+4.25 ponderado) — a categoria que a v1 chamou de "AUSENTE" ganhou seu primeiro token real (`--text-2xs`) e viu o hardcode de font-size cair de 16 para 9 instâncias no codebase inteiro (não só no escopo das 6 violações). Layout sobe marginalmente por craftsmanship (flex-wrap implementado, fade-gradient com detecção condicional de overflow). Cores cai levemente: o bug de alpha-blend inválido (N4) foi corrigido, mas em paralelo 5 novas repetições do literal `#0a0e14` (não `var(--surface-canvas)`) entraram no código para resolver contraste AA — ver §3 e §4.4. Spacing cai marginalmente porque a nova `AlertGroupTable` reproduz o mesmo idioma de `w-[Npx]` fixo por coluna que já existia (não é regressão de padrão, é replicação do padrão aceito).

---

## 2. Tabela de Violações V1–V6 — Status v2

| ID | Componente | Achado original | Status v2 | Evidência arquivo:linha |
|---|---|---|---|---|
| **V1** | StatsBar | Sem `flex-wrap` | ✅ **CORRIGIDO** | `components/dashboard/stats-bar.tsx:24` — `className="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 rounded-[var(--radius-md)]"` (era `flex items-center gap-4...` sem wrap) |
| **V2** | AlertTable | `hidden sm:flex` header | ⚠️ **MANTIDO + REFORÇADO** | `components/alerts/alert-table.tsx:154,214` — header `hidden sm:flex` intacto (padrão já considerado válido na v1); **novo**: `components/alerts/alert-row.tsx:84,102,121,129,139` adiciona labels inline `sm:hidden` por campo (`Paciente`, `Trilha`, `Data`, etc.) — decisão de UX da v1 ("se decidir por labels inline mobile, usar `sm:hidden`") foi implementada. Mesmo padrão replicado em `alert-group-row.tsx:262,275,284,291`. |
| **V3** | BedCard | `text-[10px]` (staleness) | ✅ **CORRIGIDO** | `components/dashboard/bed-card.tsx:116` — `className="text-2xs font-medium"` (token, era `text-[10px]` na linha 109/118 conforme relatório) |
| **V4** | VitalReadout | `text-[10px]` (timestamp) | ✅ **CORRIGIDO** | `components/patient/vitals-panel.tsx:71` — `className={cn('text-2xs', showDate && 'font-semibold')}` — migração no lugar, mesma linha do arquivo |
| **V5** | StateFlow | `text-[10px]` (badge terminal) | ✅ **CORRIGIDO** | `components/pathway/state-flow.tsx:166` — `className="text-2xs opacity-80"` (era `text-[10px] opacity-70`; opacidade também subiu 70→80 por legibilidade, commit `92b8658`) |
| **V6** | AppShell | `p-6` fixo | ✅ **CORRIGIDO** | `components/app-shell.tsx:334` — `className="flex-1 overflow-auto p-4 sm:p-6"` (exatamente o fix sugerido pela v1, implementado como "melhoria opcional de UX") |

**5 de 6 corrigidas integralmente; a 6ª (V2) não exigia correção pela v1 (era heurística, não violação) e ainda assim recebeu reforço de acessibilidade.** Zero regressões encontradas nas 6 localizações originais.

### Bônus — condições C1-C4 da v1, status:
- **C1** (criar `--text-2xs`): ✅ feito, `app/globals.css:50` — mas como 11px (`0.6875rem`), não 10px como a v1 sugeriu; ver §4.3 para avaliação dessa escolha.
- **C2** (substituir os 8×`text-[10px]`+1×`text-[8px]` catalogados): ✅ feito para os 8 do escopo responsivo (V3,V4,V5,A1-A5); ❌ NÃO feito para 9 outras instâncias fora desse escopo original (`text-[0.625rem]`×5 em `pathway-detail.tsx`, `text-[10px]`×3 em `severity-glow.stories.tsx`, `text-[0.8rem]`×1 em `ui/button.tsx`) — ver §3.1.
- **C3** (flex-wrap no StatsBar): ✅ feito.
- **C4** (alpha-blend inválido em `state-label.tsx`, marcado BLOQUEANTE): ✅ **CORRIGIDO** — `components/patient/state-label.tsx:20-24` agora consome `severityWash()`/`severityColor()`/`severityRing()` de `severity-glow.tsx`, eliminando a concatenação `var(--severity-*)+"33"`.

---

## 3. Varredura Completa de Hardcodes — Contagens v1 → v2

### 3.1 `text-[N...]` (fonte) — `grep -rn "text-\[[0-9]" frontend-v3/components frontend-v3/app`

| Baseline | Contagem | Fonte |
|---|---|---|
| **Baseline "v2" original** (`ds-governance-v2.md`, 10/Jul, 89 arquivos, catálogo M1–M16) | **16** | catálogo completo do codebase |
| **v1 deste mandato** (`responsive-ds-governance.md`, escopo dos 6 achados + "5 adicionais" A1-A5) | 8 reportadas (subconjunto; não recontou M1/M8-M12) | escopo parcial |
| **v2 (agora, recontagem total do codebase)** | **9** | grep atual |

**Delta real (baseline completo 16 → 9): −7 instâncias (−44%)**, todas migradas para `text-2xs` com o token novo. As 9 remanescentes:

| # | Arquivo:linha | Valor | Migrável para `text-2xs`? |
|---|---|---|---|
| 1 | `components/ui/button.tsx:26` | `text-[0.8rem]` (12.8px, botão `sm`) | Não trivial — é maior que `text-2xs` (11px) e maior que `text-xs` (12px); não é o mesmo caso de uso (texto de botão legível, não metadado). Fora do escopo RF. |
| 2-6 | `components/pathways/pathway-detail.tsx:58,93,118,123,128` | `text-[0.625rem]` (10px) ×5 | Sim, seria candidato direto — 10px está abaixo do novo `--text-2xs` (11px). Não tocado neste ciclo (arquivo fora do escopo dos tickets RF-008..015/021). |
| 7-9 | `components/patient/severity-glow.stories.tsx:35,38,41` | `text-[10px]` ×3 | Sim — mas é arquivo `.stories.tsx` (Storybook, não renderizado em produção). Baixa prioridade real. |

**Honestidade:** o ciclo fechou 100% dos hardcodes que estavam no seu próprio escopo de tickets (RF-008/009/010/011/012/013/015 + V3/V4/V5), mas não fez uma varredura de fechamento total do codebase — `pathway-detail.tsx` é a maior lacuna remanescente (5 instâncias em um arquivo de produção, não Storybook).

### 3.2 Cores hex/rgb fora de `globals.css`

`rgb()`/`rgba()`: **zero ocorrências** em todo o `frontend-v3` (fonte), inalterado v1→v2.

Hex literal (`#RRGGBB`) em código executável (fora de comentários), fora de `globals.css`:

| Baseline | Contagem | Detalhe |
|---|---|---|
| v1 (implícito no score 99/100, sem listagem explícita) | não enumerado | — |
| **v2 (agora)** | **5 instâncias de código + 1 fallback órfão** | ver tabela abaixo |

| # | Arquivo:linha | Código | Avaliação |
|---|---|---|---|
| 1 | `components/app-shell.tsx:261` | `text-[#0a0e14]` | Texto escuro sobre botão de fundo `var(--severity-critical)` sólido |
| 2 | `components/alerts/filter-bar.tsx:170` | `text-[#0a0e14]` | Texto escuro sobre badge de contagem `bg-[var(--severity-urgent)]` sólido |
| 3 | `components/alerts/alert-group-row.tsx:247` | `color: '#0a0e14'` | Badge de severidade crítica sólida (grupo escalando) |
| 4 | `components/alerts/alert-group-row.tsx:253` | `backgroundColor: '#0a0e14'` | Dot decorativo dentro do badge acima |
| 5 | `components/alerts/alert-group-row.tsx:324` | `color: '#0a0e14'` | Badge "Escalando" sobre `var(--severity-critical)` sólido |
| 6 (órfã) | `components/patient/severity-glow.stories.tsx:10` | `var(--surface-base, #0a0e14)` | Fallback de um token **`--surface-base` que não existe** em `globals.css` (o token real é `--surface-canvas`) — typo/drift, arquivo Storybook |

**Avaliação honesta pedida pelo prompt — "`#0a0e14` texto sobre severidade sólida, é token?":** `#0a0e14` é literalmente o valor de `--surface-canvas` (`globals.css:22`). Semanticamente a escolha é **correta**: usar a cor de fundo mais escura da paleta como texto sobre um badge de severidade sólida e brilhante é o padrão certo para contraste AA (documentado com matemática de contraste inline em `alert-group-row.tsx:216-238` e `:297-320`, WCAG 4.483:1→7.217:1). **Mas não é um token** — é o valor duplicado como literal em 5 lugares. Deveria ser `var(--surface-canvas)`. Risco: se o tema escuro mudar esse valor no futuro (ex. suporte a light theme), essas 5 ocorrências não acompanham a mudança silenciosamente. É um hardcode real, não escondido — está bem documentado localmente, mas arquitetonicamente deveria referenciar o token existente em vez de repetir o literal. Recomendação: `s/#0a0e14/var(--surface-canvas)/g` nesses 5 pontos (5 min, risco zero) + corrigir o typo `--surface-base`→`--surface-canvas` no arquivo Storybook.

### 3.3 `w-[Npx]` / `h-[Npx]` arbitrários — `grep -rno '\b[wh]-\[[0-9]+px\]'`

| Baseline | Contagem | Fonte |
|---|---|---|
| **Baseline "v2" original** (`ds-governance-v2.md`, M17–M44, excluindo os 4 `shadow-[0_0_Npx...]` incorretamente cestados na mesma seção) | **24** (16 largura + 8 altura) | catálogo completo |
| **v2 (agora, recontagem total)** | **29** | grep atual — ver breakdown |

**Delta: +5 instâncias**, 100% explicadas por uma feature nova (não regressão): a `AlertGroupTable` (ADR-0039, agrupamento de alertas por paciente/sinal) adiciona um segundo cabeçalho de tabela em `components/alerts/alert-table.tsx:216-221` (`w-[88px]`, `w-[160px]`, `w-[90px]`, `w-[110px]`, `w-[170px]`) que replica **o mesmo idioma já existente** do cabeçalho `AlertTable` original (`w-[88px]`, `w-[140px]`, `w-[120px]`, `w-[120px]`, `w-[100px]`, `w-[180px]`, linhas 156-162). Não é um padrão novo nem uma regressão de disciplina — é reuso consistente (para o bem ou para o mal) de um idioma pré-existente que a v2 do `ds-governance-v2.md` já havia classificado como violação MAJOR de baixa severidade (M17-M44, sem token de layout/grid-column para substituir). Nenhum arquivo fora de `alert-table.tsx` mudou sua contagem. Cluster de `shadow-[0_0_Npx_...]` (4 instâncias, `severity-glow.tsx`×3 + `state-flow.tsx`×1) permanece igual, fora do escopo estrito de w/h.

### 3.4 Achado suplementar (fora do pedido explícito, por transparência) — `borderWidth`/`borderStyle` inline (N1)

Contagem via `borderWidth:` (uma ocorrência por "instância" na metodologia da v2 original): **22** agora vs **19** catalogadas em `ds-governance-v2.md`. Os arquivos com o padrão são os mesmos da baseline (componentes `admin/*`, pré-existentes desde o commit `1aa1630`, não tocados neste ciclo) — não foi possível atribuir as +3 instâncias a nenhum commit específico deste ciclo dentro do orçamento desta auditoria; **não bloqueia**, é reportado por honestidade mas não entra no score (fora do escopo dos 3 eixos pedidos).

---

## 4. Tokens Novos do Ciclo — Avaliação de Governança

### 4.1 `--text-2xs` (`app/globals.css:50-51`)

```css
--text-2xs: 0.6875rem; /* 11px */
--text-2xs--line-height: calc(1 / 0.6875);
```

- **Nomenclatura:** ✅ conforme — segue a convenção nativa do Tailwind v4 (`--text-{size}` dentro de `@theme inline` gera a utility `text-2xs` automaticamente, extensão natural da escala `xs/sm/base/...`), não uma convenção inventada.
- **Local:** ✅ correto — dentro do bloco `@theme inline` junto com as outras `--color-*`, é o único lugar onde o Tailwind v4 aceita geração de utilities a partir de tokens.
- **Documentação inline:** ✅ excelente — comentário explica a motivação (RF-008..015), por que 11px e não 10px (piso de legibilidade, não replica o valor antigo), por que `--text-3xs` (8px) foi deliberadamente rejeitado ("8px é ilegível... deve migrar PARA CIMA, não ganhar um token que o legitima") e a justificativa do line-height (piso de 16px, mesmo mínimo do `text-xs` nativo).
- **Adoção:** 6 arquivos de produção consomem a utility (`filter-bar.tsx`, `app-shell.tsx`, `bed-card.tsx`, `pathway-badges.tsx`, `state-flow.tsx`, `vitals-panel.tsx`), 13 ocorrências totais.
- **Nota de honestidade:** a v1 recomendou 10px (`--text-2xs: 0.625rem`); o time entregou 11px com justificativa documentada (piso de legibilidade), divergindo deliberadamente da recomendação da própria auditoria anterior — decisão superior à sugestão original, mas tecnicamente um desvio do pedido de C1/C2 que vale registrar.
- **Veredito:** ✅ **Exemplar** — é a peça de maior valor arquitetural do ciclo (fecha a lacuna estrutural "tipografia AUSENTE" apontada desde a v1 dos DS Governance, 09/Jul).

### 4.2 `--severity-{normal,watch,urgent,critical}-ring` (`app/globals.css:17-20`)

```css
--severity-normal-ring: color-mix(in srgb, var(--severity-normal) 24%, transparent);
/* ... watch, urgent, critical */
```

- **Nomenclatura:** ✅ conforme — segue exatamente o padrão já estabelecido por `--severity-*-wash` (mesmo prefixo, sufixo semântico novo `-ring` para "borda", paralelo a `-wash` para "preenchimento").
- **Local:** ✅ correto — agrupado com os `-wash` existentes em `:root[data-theme='dark']`, mesma seção lógica.
- **Documentação inline:** ✅ boa — comenta a motivação (substituir a concatenação hex-alpha inválida `var(--severity-*)+"33"`), por que 24% (mais forte que `-wash` por ser borda, não fill) e referencia o ticket (RF-001/QW-0).
- **Adoção — reuso orgânico além do escopo original:** consumido em 2 lugares:
  1. `state-label.tsx:23` via `severityRing()` — o consumidor originalmente planejado (fix do bug N4).
  2. `severity-dot.tsx:32-33` — consumidor **novo, não previsto no ticket original**, com comentário explícito ("Ring colors reuse the `--severity-*-ring` tokens... no new hardcoded values") mostrando que outro desenvolvedor encontrou o token e o reusou em vez de hardcodar um novo valor. Este é o sinal mais forte de governança saudável em todo o ciclo: o token sobreviveu ao seu caso de uso original.
- **Veredito:** ✅ **Exemplar** — corrige um bug real (CSS inválido) E se prova reutilizável fora do escopo original.

### 4.3 `.overflow-fade-gradient` (`app/globals.css:54-58`)

```css
.overflow-fade-gradient {
  mask-image: linear-gradient(90deg, transparent 0%, black 15%, black 85%, transparent 100%);
  -webkit-mask-image: linear-gradient(90deg, transparent 0%, black 15%, black 85%, transparent 100%);
}
```

- **Nomenclatura:** ⚠️ aceitável, mas é uma classe utilitária solta (`.overflow-fade-gradient`), não um custom property/token — categoricamente diferente dos outros dois. Não há problema em si (o DS já tem outros utilitários soltos, ex. `.severity-critical-pulse`), mas do ponto de vista de "token" puro, esta entrega é uma **classe CSS**, não uma variável reutilizável por composição (`var(--x)`); outro componente que precisar do mesmo efeito precisa aplicar a classe inteira, não pode reescalar/reparametrizar via CSS custom property.
- **Local:** ✅ correto — junto aos outros utilitários customizados (`body`, `.severity-critical-pulse`) no final do arquivo.
- **Documentação inline:** ✅ presente, mas mínima — 1 linha (`/* RF-021 — Overflow fade gradient indicator... */`), sem explicar a escolha dos breakpoints do gradiente (15%/85%) nem por que mask-image em vez de outra técnica (box-shadow inset, pseudo-elemento com gradient overlay).
- **Adoção:** 1 único consumidor (`state-flow.tsx:126`), aplicado **condicionalmente** via `ResizeObserver` (commit `fdafbbb`, refinamento pós-lançamento: a classe só é aplicada quando `scrollWidth > clientWidth`, evitando aplicar o fade quando não há overflow real — boa disciplina de craftsmanship, mostra iteração dentro do próprio ciclo).
- **Veredito:** 🔶 **Adequado, não exemplar** — tecnicamente correto e bem-consumido, mas é o único dos 3 tokens novos com um único ponto de uso (não provou reusabilidade como o `-ring`) e é uma classe, não uma variável — um auditor de governança rigoroso notaria que não há garantia de que a próxima necessidade similar (ex. fade vertical em uma lista longa) reutilize esta classe em vez de reinventar; não há decisão de nomenclatura que sinalize "isto é parametrizável" (ex. não aceita direção/tamanho via CSS var).

---

## 5. Veredito

```
╔══════════════════════════════════════════════════════════════╗
║              VEREDITO: GO (upgrade de CONDITIONAL-GO)        ║
║                                                                ║
║  Score DS: 92.05/100  (v1: 88.0/100, Δ +4.05)                ║
║                                                                ║
║  Das 4 condições da v1 (C1-C4):                               ║
║    C1 ✅ feito (com desvio positivo: 11px em vez de 10px)     ║
║    C2 ✅ feito para o escopo original; pathway-detail.tsx     ║
║         (5 instâncias) permanece fora — não bloqueante        ║
║    C3 ✅ feito                                                ║
║    C4 ✅ feito — bug de CSS inválido eliminado                ║
║                                                                ║
║  Nenhuma violação nova de severidade CRITICAL ou MAJOR foi    ║
║  introduzida. O crescimento de +5 em w/h-[Npx] e +5 em hex    ║
║  literal é rastreável a features novas (agrupamento de        ║
║  alertas, fix de contraste AA) que reusam padrões             ║
║  pré-existentes, não a regressão de disciplina.               ║
╚══════════════════════════════════════════════════════════════╝
```

**Pendências remanescentes (não bloqueantes, para o próximo ciclo):**
1. `pathway-detail.tsx` — 5× `text-[0.625rem]` não migradas para `text-2xs`.
2. 5× `#0a0e14` literal → deveriam referenciar `var(--surface-canvas)`.
3. `severity-glow.stories.tsx:10` — fallback para token inexistente `--surface-base` (typo, deveria ser `--surface-canvas`).
4. `.overflow-fade-gradient` tem um único consumidor; se um segundo caso de uso surgir, avaliar se deveria virar `mask-image: var(--fade-gradient)` parametrizável em vez de classe fixa.

---

*Relatório gerado por Hermes Agent (DS Guardian / Gatekeeper) — re-auditoria v2, 2026-07-13.*
*Fontes: `responsive-ds-governance.md` (v1 deste mandato), `ds-governance-v2.md` (baseline de hardcodes pré-existentes), código fonte atual (`frontend-v3/components`, `frontend-v3/app`), `globals.css`, histórico git do branch `feat/responsive-alerts-uplift`.*
