# DIM B — UX Clínica & Acessibilidade — RE-AUDITORIA (independente)

**Data:** 2026-07-12
**Escopo:** `/Users/familia/intensicare/frontend-v3/` (Next.js 16), branch `fix/sprint-3-sepsis-governance`
**Auditor:** Agente de re-auditoria independente (Claude) — não implementou nada neste ciclo.
**Baseline:** `docs/audit/fullspectrum/DIM_B_UX.md` (score 78/100: 1 CRITICAL + 5 MAJOR + 3 MINOR).

## Metodologia

Ao contrário da auditoria original (inspeção estática apenas — frontend estava fora do ar), este
ciclo teve **frontend `:3000` UP e backend `:8000` UP** com seed DEMO carregado. Cada um dos 9
achados foi re-testado com evidência de execução real, não apenas leitura de código:

- Cálculo de contraste WCAG 2.1 (luminância relativa) via script Python para os hex codes atuais.
- `npx @axe-core/cli` contra `/login`.
- `E2E_BACKEND=1 npx playwright test e2e/smoke.spec.ts` (suite existente, 9 testes).
- 3 specs Playwright ad-hoc temporários (login real com `admin/admin`, navegação por clique,
  reload de página) para observar comportamento de runtime que a auditoria original não pôde
  observar — removidos após uso, não commitados.
- `curl` autenticado contra `POST /api/v1/auth/login` (form-urlencoded — a rota JSON em
  `/api/v1/auth/login` exige `application/x-www-form-urlencoded`, não JSON puro, ao contrário do
  que um teste ingênuo assumiria) e `GET /api/v1/patients/MPI-DEMO-001`.

Único write deste ciclo: este arquivo de relatório.

---

## 1. Achados originais — status item a item

### B-C1 (CRITICAL) — Badge de contagem urgente, contraste 2.87:1

`components/alerts/filter-bar.tsx:163`: `bg-[var(--severity-urgent)] text-[10px] text-[#0a0e14]`
(antes: `text-white`).

Cálculo: urgent `#F96F06` vs texto escuro `#0a0e14` → **6.73:1** (PASS AA texto 4.5:1, PASS AAA
large 3:1... na verdade também passa AAA texto 7:1 está próximo, mas 6.73 já supera AA com folga).

**FECHADO.** Confirmado por leitura de código e cálculo independente.

*Nota de estilo (não é regressão de acessibilidade):* o valor é hardcoded como `#0a0e14` em vez de
`var(--surface-canvas)` (mesmo valor, token existente em `app/globals.css:16`). Funcionalmente
correto, mas reintroduz um hex literal fora do sistema de tokens — pequena inconsistência de DS,
sem impacto de contraste.

### B-M1 (MAJOR) — Logout "Sair", contraste 3.51:1

`components/app-shell.tsx:166`: `bg-[var(--severity-critical)] text-[#0a0e14] font-medium`
(antes: `text-white`).

Cálculo: critical `#FF7077` vs `#0a0e14` → **7.22:1** (PASS AA e AAA texto).

**FECHADO.** Confirmado.

### B-M2 (MAJOR) — Token `--severity-critical` vs `--surface-overlay`, 4.41:1

`app/globals.css:9`: token mudou de `#FF3B4A` para `#FF7077`.

Cálculo: `#FF7077` vs `--surface-overlay` `#1c2530` → **5.78:1** (PASS AA texto 4.5:1; antes era
4.41:1, FAIL). Recalculado também os outros dois fundos por completude:
`#FF7077` vs `--surface-canvas` `#0a0e14` = 7.22:1; vs `--surface-raised` `#141b22` = 6.48:1.
Todos os 3 fundos agora PASS AA texto — a falha estava restrita à combinação overlay e some.

**FECHADO.** Todos os pares severidade × fundo agora ≥4.5:1.

### B-M3 (MAJOR) — Breadcrumb expõe IDs brutos

Código novo confirmado: `lib/breadcrumb-context.tsx` (`BreadcrumbProvider`,
`useSetBreadcrumbLabel`) + `components/app-shell.tsx:22,42-46,56-62` consome `labels` do contexto
com fallback para o slug title-cased. Páginas que registram label:
`app/patient/[mpi_id]/page.tsx:86` (`useSetBreadcrumbLabel(mpiId, patient?.patient_name)`) e
`app/patient/[mpi_id]/pathway/[pp_id]/page.tsx:57` (`useSetBreadcrumbLabel(ppIdRaw,
progress?.pathway_name)`).

**Teste ao vivo (Playwright, login real `admin/admin`, clique real em BedCard → PathwayCard):**

```
Dashboard → clique 1 → /patient/MPI-DEMO-001
BREADCRUMB: "Paciente" "DEMO Sepse Crítica"        ← nome real, correto

           → clique 2 → /patient/MPI-DEMO-001/pathway/{id}
BREADCRUMB: "Paciente" "MPI DEMO 001" "Trilha" "Sepse"   ← segmento Paciente REGRIDE para o ID bruto
```

**Causa raiz:** `useSetBreadcrumbLabel` (`lib/breadcrumb-context.tsx:88-92`) registra o label no
`useEffect` e **remove no cleanup do unmount** (`return () => clearLabel(segment)`). Ao navegar de
`/patient/[mpi_id]` para `/patient/[mpi_id]/pathway/[pp_id]`, o componente da página de paciente
desmonta, seu cleanup dispara e apaga o label do `mpiId` do contexto — e a página de pathway só
registra o label da trilha (`ppId`), não o do paciente. O crumb "Paciente" cai de volta no fallback
`seg.replace(/-/g,' ').replace(/\b\w/g, ...)`.

**Isso é exatamente o cenário citado como exemplo no achado CRITICAL original**
(`/patient/{mpi_id}/pathway/{pp_id}` com "UUID/ID numérico... não o nome do paciente/trilha") —
e ele **ainda ocorre**, na página mais profunda da jornada (3 níveis), que é onde o breadcrumb
mais importa para orientação clínica.

**NÃO FECHADO — fechamento parcial com regressão.** Funciona para o nível 1 (paciente), falha no
nível 2 (paciente ainda visível na trilha). Rebaixado de MAJOR "IDs brutos em toda parte" para
MAJOR "IDs brutos na view mais profunda da jornada" — severidade mantida como MAJOR porque o
usuário mais dependente de contexto (na pathway view, decidindo sobre o paciente) é exatamente
quem vê o ID bruto.

### B-M4 (MAJOR) — Sem atalhos de teclado globais

`grep -rn "addEventListener.*keydown\|useHotkeys\|window.*onkeydown\|document.*onkeydown"
components app lib` → **zero resultados**.

**PERSISTE, sem alteração.**

### B-M5 (MAJOR) — Tooltips clínicos ausentes

`grep -rl "title=" components app` → ainda apenas 2 arquivos: `components/app-shell.tsx` (agora
usado só para o indicador de status de conexão WebSocket, ADR-0034) e
`components/alerts/quick-actions.tsx`.

**PERSISTE, sem alteração** (uso de `title=` não cresceu para os componentes clínicos densos —
`bed-card.tsx`, `criteria-row.tsx`, `score-pair.tsx` etc. continuam sem tooltip).

### B-Mn1 (MINOR) — `text-[Npx]` arbitrário

`grep -rn "text-\[[0-9]*px\]" components app | wc -l` → **10** (era 7 na auditoria original).

**PERSISTE, ligeiramente pior** (+3 ocorrências).

### B-Mn2 (MINOR) — Estilos inline `borderWidth`/`borderStyle`

`grep -rn "borderWidth\|borderStyle" components app | wc -l` → **37** ocorrências (auditoria
original citou exemplos pontuais sem contagem total).

**PERSISTE.**

### B-Mn3 (MINOR) — Cobertura de `focus-visible`

10 arquivos usam `focus-visible` (`button.tsx`, `quick-actions.tsx`, `alert-row.tsx`,
`unit-filter.tsx`, `bed-card.tsx`, `pathway-card.tsx`, `criteria-row.tsx`, `pathway-def-card.tsx`,
`pathway-grid.tsx`, `admin/page.tsx`). 8 arquivos com `onClick` **não** usam `focus-visible`
diretamente: `pathway/[pp_id]/page.tsx`, `admin/user-manager.tsx`, `alerts/filter-bar.tsx`,
`app-shell.tsx`, `dashboard/bed-grid.tsx`, `pathways/pathway-detail.tsx`,
`patient/alert-item.tsx`, `patient/score-timeline.tsx` (alguns desses podem herdar foco visível de
`<button>` nativo do navegador ou de `components/ui/button.tsx`, não confirmado por amostragem
completa dentro do tempo alocado).

**PERSISTE, risco residual não resolvido — mesmo status da auditoria original.**

---

## 2. Material novo deste ciclo

### CSP nonce restaurou hidratação — confirmado e creditado

`middleware.ts:15-49` gera nonce por requisição e o propaga via header `x-nonce` +
`Content-Security-Policy`, permitindo que o Next.js aplique o nonce automaticamente aos scripts de
hidratação sob CSP estrita (`script-src 'self' 'nonce-{nonce}' 'strict-dynamic'`). Confirmado
funcionando: `npx @axe-core/cli http://localhost:3000/login` → **0 violations** (exige DOM
totalmente hidratado e interativo para o axe operar), e a suite E2E completa passou com
interações reais de formulário/clique.

```
npx @axe-core/cli http://localhost:3000/login
→ 0 violations found!
```

Login também expõe `<main id="main-content">` (`app/login/page.tsx:32`) e `<h1
className="sr-only">IntensiCare — Acesso</h1>` (linha 35) — landmark e heading presentes, motivo
adicional para o 0/0 do axe.

### `E2E_BACKEND=1 npx playwright test e2e/smoke.spec.ts` — 9/9 PASS

```
9 passed (13.1s)
```

Inclui os 2 testes reais de backend (login real `admin/admin`, dashboard com lista de pacientes,
jornada de 2 cliques bed→patient→pathway) que antes eram skipados por falta de backend. Confirma
ao vivo o que a auditoria original só pôde inferir do código: jornada 2-cliques funciona, sem
dead-end, cartão de leito tem indicador de severidade visível.

### Admin guard client-side — confirmado, ressalva registrada

`app/admin/page.tsx:33-40`: guarda via `useEffect` que redireciona não-admins
(`if (!isLoading && !user?.is_admin) router.push(...)`) e renderiza `null`/loading enquanto
`isLoading || !user?.is_admin`, evitando flash de conteúdo administrativo. Adequado para UX; é uma
salvaguarda **apenas client-side** — não é objeto desta dimensão (autorização de dados é Dimensão
D/Segurança), mas registrado pois interage com a mesma sessão in-memory descrita abaixo: se o
componente pai perder o token (ver B-C2), o guard corretamente expulsa o usuário — não há
vazamento de conteúdo admin observado.

### B-C2 (NOVO, CRITICAL) — Refresh de página / deep link derruba a sessão

Ao investigar por que `page.goto('/patient/MPI-DEMO-001')` direto (sem clicar a partir do
dashboard) retornava ao `/login` num teste ad-hoc, foi isolada uma causa estrutural, não um
artefato de teste:

- `lib/api.ts:225` — o JWT vive **apenas em memória** (`let _token: string | null = null`),
  comentário explícito no código: "JWT in-memory (never localStorage/sessionStorage)".
- `middleware.ts:16,31-35` — o gate de rota do Next.js verifica **apenas a presença** do cookie
  `token` (HttpOnly, definido pelo backend no login) para decidir se renderiza a página ou
  redireciona — não valida nem lê o JWT em si.
- Resultado: numa navegação client-side (clicar em `<Link>`/`router.push`), o módulo JS
  permanece carregado, `_token` continua em memória, tudo funciona (confirmado: teste 9 da suite,
  9/9 verde).
- Mas num **full page load** — F5, deep link colado na barra de endereço, ou abrir em nova aba —
  o módulo JS é recarregado do zero, `_token` volta a `null`. O middleware ainda vê o cookie
  `token` e deixa a página SSR renderizar o shell autenticado (sidebar, topbar aparecem), mas a
  **primeira requisição de dados client-side** (SWR fetch de `/api/v1/patients/...` etc.) sai sem
  `Authorization: Bearer`, recebe `401`, e `lib/api.ts:261-267` executa
  `window.location.href = '/login'` — um hard redirect, sem tentativa de refresh via
  `refresh_token` (que o backend já emite no login, mas o cliente não usa para rehidratar).

**Verificado ao vivo, duas vezes, isolando a causa:**

1. Login real → dashboard renderiza (`Lista de pacientes` visível) → `page.reload()` →
   `page.url()` = `http://localhost:3000/login`. Log de rede mostra `401` em
   `/api/v1/patients`, `/api/v1/alerts` etc. imediatamente após o reload.
2. Login real → clique 1 (bed card) → `/patient/MPI-DEMO-001` renderiza corretamente (breadcrumb
   com nome real) → **isso via navegação client-side, não reload** — funciona.
3. `page.goto()` direto para `/patient/MPI-DEMO-001` após já autenticado (equivalente a colar o
   link numa nova aba) → mesmo padrão de 401 → `/login`.

**Impacto:** qualquer usuário clínico que dê F5 (comum durante plantões longos, após o
notebook suspender, ou por hábito), abra um link de paciente compartilhado por outro membro da
equipe, ou apenas tenha a aba recarregada por gerenciamento de memória do navegador, **perde a
sessão e é expulso para `/login` sem aviso**, mesmo tendo um cookie de sessão válido por até 30
minutos (`max_age=1800` citado em `lib/api.ts:351`). Isso contradiz diretamente a meta de "jornada
sem dead-ends" que a auditoria original validou — o dead-end existe, só não é alcançável por
navegação interna do app, apenas por reload/deep-link, cenário que a auditoria original (sem
browser) não tinha como exercitar.

Este achado **não é o mesmo** que o problema de hidratação sob CSP (esse já estava e continua
corrigido — confirmado pelo axe 0-violations e pela suite E2E completa rodando sem erro de
hidratação). É um bug de arquitetura de sessão distinto, descoberto só porque este ciclo pôde
efetivamente rodar o app com backend real.

---

## 3. Novo score

### Contagem final

| Severidade | Itens |
|---|---|
| **CRITICAL** | 1 — **B-C2 (NOVO)**: sessão derruba no refresh/deep-link (`lib/api.ts:225-267`, `middleware.ts:16-35`) |
| **MAJOR** | 3 — B-M3 (breadcrumb regride no nível 2, fechamento parcial), B-M4 (sem atalhos, inalterado), B-M5 (sem tooltips clínicos, inalterado) |
| **MINOR** | 3 — B-Mn1 (text-[Npx] 7→10), B-Mn2 (inline border styles, 37 ocorrências), B-Mn3 (focus-visible parcial, inalterado) |

**Fechados desde a auditoria original:** B-C1, B-M1, B-M2 (3 itens, todos com contraste
recalculado e verificado ≥ 4.5:1 AA).

### Cálculo

Mesma rubrica: base 100, CRITICAL −8, MAJOR −4, MINOR −1.5, com ajuste de piso pelas metas
centrais atendidas (jornada, densidade, severidade, 0 páginas standalone) — igual à auditoria
original.

```
100 − 8 (1 CRITICAL) − 12 (3 MAJOR) − 4.5 (3 MINOR) = 75.5
```

Ajuste de piso: **menor que o da auditoria original (+10.5)**, porque uma das metas centrais que
justificava aquele piso — "jornada em 2 cliques sem dead-ends" — está **parcialmente
comprometida** pelo B-C2 (o dead-end existe, é só disparado por reload/deep-link em vez de
navegação interna). As outras metas (densidade, severidade com 4 níveis + ícones, 0 páginas
standalone, skip-link, overlay mobile acessível) permanecem intactas e agora verificadas ao vivo
(não só por inspeção), o que justifica manter algum piso, apenas reduzido.

```
75.5 + 3.5 (piso reduzido) = 79
```

### **NOVO SCORE: 79/100**

Nota: 79 é próximo do 78 original, mas por razões opostas — a auditoria original tinha 1 CRITICAL
de contraste isolado (grave, mas contido a 2 componentes) + 5 MAJOR + 3 MINOR; este ciclo fechou
de fato 3 desses itens (1 CRITICAL + 2 MAJOR, com matemática de contraste recalculada e
confirmada), mas o ganho é quase inteiramente compensado por um CRITICAL novo e estruturalmente
mais grave (compromete toda rota autenticada em reload/deep-link, não só 2 componentes), mais um
MAJOR que não fechou de fato (regrediu no nível mais profundo da jornada). O placar quase-estável
esconde uma composição de achados bem diferente — e mais preocupante em termos de confiabilidade
de sessão — do que o número sozinho sugere.

---

## 4. Os 3 achados mais relevantes remanescentes

1. **B-C2 (CRITICAL, novo)** — Token JWT só em memória + middleware que só checa presença do
   cookie → refresh de página, deep link, ou nova aba derruba a sessão do usuário e o joga de
   volta para `/login`, mesmo com cookie de sessão válido. `lib/api.ts:225-267`,
   `middleware.ts:16-35`. Verificado ao vivo com Playwright (login real, reload real).

2. **B-M3 (MAJOR, fechamento parcial/regressão)** — Breadcrumb mostra nome real do paciente na
   view de paciente, mas **regride para o ID bruto ("MPI DEMO 001") exatamente na view de
   pathway** (nível mais profundo), porque `useSetBreadcrumbLabel` limpa o label no unmount da
   página de paciente e a página de pathway não o re-registra. `lib/breadcrumb-context.tsx:88-92`,
   `app/patient/[mpi_id]/pathway/[pp_id]/page.tsx:57`.

3. **B-M4 + B-M5 (MAJOR, herdados, inalterados)** — Zero atalhos de teclado globais e tooltips
   clínicos ainda restritos a 2 arquivos não-clínicos (`app-shell.tsx`, `quick-actions.tsx`);
   nenhum progresso desde a auditoria original em nenhum dos dois.
