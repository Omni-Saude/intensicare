PROMPT PARA IVE — Integração Frontend-Backend (5 Gaps, 100% Cobertura)
═══════════════════════════════════════════════════════════════════════════

## ═══════ GOAL ═══════

Conectar o frontend-v2 do IntensiCare ao backend real, eliminando 100% dos dados mock e
integrando todos os componentes e tipos novos. O backend já está completo (30 gaps fechados
pelo Parreira em 2026-07-09). Sua missão é fazer o frontend CONSUMIR o que já existe.

## ═══════ CONTEXT ═══════

### O que já existe (NÃO modificar)
- **Backend:** 24 routers, 68+ endpoints REST, todos funcionais
- **Contratos:** 15 OpenAPI 3.1.0 em `docs/contracts/`
- **API client parcial:** `frontend-v2/lib/api.ts` (17 funções, 427 linhas)
- **33 páginas** em `frontend-v2/app/`
- **3 componentes novos** do Parreira: `Breadcrumb.tsx`, `OverlayStack.tsx`, `TenantProvider.tsx`

### O que está errado (FRONTEND_AUDIT.md)
- **22/33 páginas usam dados mock** — não consomem o backend real
- **16/24 routers sem função no cliente** — `lib/api.ts` cobre só 7 routers
- **Breadcrumb nunca integrado** — 183 linhas de código morto
- **RBAC binário** — backend tem 7 roles, frontend só usa `is_admin`
- **Tipos desatualizados** — `encounter_id`, `definition_version_id` ausentes

### Leitura obrigatória antes de começar
1. `/Users/familia/intensicare/docs/audit/handoff-ive/HANDOFF.md` — Especificação completa (31 KB)
2. `/Users/familia/intensicare/docs/audit/FRONTEND_AUDIT.md` — Diagnóstico detalhado
3. `/Users/familia/intensicare/frontend-v2/lib/api.ts` — API client atual

---

## ═══════ OS 5 GAPS (RESUMO) ═══════

### GAP 1 — API Client: 50 funções em `lib/api.ts`
Adicionar funções TypeScript tipadas para TODOS os endpoints backend.
Prioridade: P0 (TDD domains) → P1 (clinical) → P2 (admin/infra).
Ver HANDOFF.md §GAP 1 para assinaturas exatas.

### GAP 2 — Páginas Mock: 22 páginas → API real
Substituir `useState(MOCK_DATA)` por `useEffect + fetchXxx()` em cada página.
Ver HANDOFF.md §GAP 2 para matriz página×endpoint.

### GAP 3 — Breadcrumb: 1 linha no `layout.tsx`
`import Breadcrumb from '@/components/Breadcrumb'` + `<Breadcrumb />` acima do `{children}`.

### GAP 4 — RBAC Granular: hook + componente + dropdown
- Criar `hooks/useRole.ts`
- Criar `components/RequireRole.tsx`
- Atualizar `admin/users/page.tsx` com dropdown de 7 roles

### GAP 5 — Tipos TypeScript: `encounter_id` + `definition_version_id`
Adicionar campos novos às interfaces existentes.

---

## ═══════ PLANO DE EXECUÇÃO ═══════

### FASE 0 — RECON (você, sem subagentes) — ≤10min

1. Ler `HANDOFF.md` completo
2. Ler `lib/api.ts` atual
3. Ler `app/layout.tsx` atual
4. Produzir `/Users/familia/intensicare/docs/audit/handoff-ive/PLANS.md` com milestones

### FASE 1 — API Client P0 (TDD domains) — 1 batch

**Milestone 1.1:** Adicionar tipos + funções Pathways (6 funções)
**Milestone 1.2:** Adicionar tipos + funções Prescricao (6 funções)
**Milestone 1.3:** Adicionar tipos + funções Movimentacao (4 funções)
**Milestone 1.4:** Adicionar tipos + funções Formularios (3 funções)
**Milestone 1.5:** Adicionar tipos + funções Evolucoes (3 funções)

Gatekeeper após cada milestone: `npx tsc --noEmit`

### FASE 2 — Páginas P0 (TDD domains) — delegate_task paralelo

Dispatcher 3 subagentes em paralelo (cada um edita 1-2 páginas):

| Agente | Páginas | Endpoints |
|--------|---------|-----------|
| Agente A | `care-pathways/page.tsx` | fetchPathways, fetchPatientPathways |
| Agente B | `prescription/page.tsx` | fetchPrescriptions, createPrescription |
| Agente C | `patient-movement/page.tsx` + `clinical-forms/page.tsx` | fetchMovements, fetchBedGrid, fetchClinicalFormTypes |

Cada agente recebe no `context`:
- Path exato do arquivo
- Funções a importar de `@/lib/api`
- Padrão de substituição (ANTES mock → DEPOIS API)
- Template de loading/error state

Gatekeeper: `grep -c 'mock\|simul\|MOCK' app/<page>/page.tsx` deve ser 0

### FASE 3 — Breadcrumb + RBAC (você direto) — ≤30min

**Milestone 3.1:** Breadcrumb no layout (1 linha)
**Milestone 3.2:** Criar `hooks/useRole.ts` + `components/RequireRole.tsx`
**Milestone 3.3:** Atualizar `admin/users/page.tsx` com dropdown de roles
**Milestone 3.4:** Atualizar tipos com `encounter_id` + `definition_version_id` (GAP 5)

Gatekeeper: `npm run build`

### FASE 4 — API Client P1+P2 (domínios restantes) — delegate_task paralelo

Dispatcher 3 subagentes para os 10 grupos restantes de endpoints (Grupos 1.6 e 1.7 do HANDOFF.md).

Gatekeeper: `grep -c 'export async function' lib/api.ts` ≥ 67

### FASE 5 — Páginas P1+P2 — delegate_task paralelo

Dispatcher subagentes para as 17 páginas restantes. Máximo 3 por batch.

Gatekeeper por página: `grep -c 'mock\|simul\|MOCK' app/<page>/page.tsx` = 0

---

## ═══════ REGRAS DE OURO (AGENTIC-LOOP) ═══════

Estas regras são obrigatórias. Violá-las significa re-trabalho.

### R1 — PLANS.md antes de tudo

NUNCA comece a editar sem um plano. Para cada milestone:
```markdown
## Milestone M1.1: Pathways API (6 funções)
Arquivos: lib/api.ts (append)
Gatekeeper: npx tsc --noEmit
Rollback: git checkout lib/api.ts
```

### R2 — RECON antes de editar

Antes de modificar qualquer página, LEIA o arquivo atual. Entenda:
- Quais imports existem
- Qual a estrutura de estado (useState, useEffect)
- Onde está o mock data
- Quais componentes filhos são afetados

### R3 — Gatekeeper ≠ implementador

Após CADA milestone, um agente DIFERENTE executa a verificação:
```bash
npx tsc --noEmit           # TypeScript compila?
npm run build               # Next.js builda?
grep -c 'mock' page.tsx     # Mock removido?
```

### R4 — PERSISTÊNCIA (LOOP ATÉ PASSAR)

Este é o ponto MAIS IMPORTANTE. O loop NÃO termina até o gatekeeper passar:

```
Milestone → Gatekeeper
  ├── PASSOU → próximo milestone
  └── FALHOU → diagnosticar causa raiz
       ├── agente DIFERENTE corrige
       ├── re-roda gatekeeper
       └── REPETE até PASSAR (sem limite de tentativas)
```

**NUNCA pule um gatekeeper falho.** "É só um erro de tipo" não é desculpa.
**NUNCA marque DONE sem gatekeeper passando.** Self-report não é evidência.

### R5 — Verificação com comandos reais

Toda verificação usa comandos que retornam output real:
```bash
npx tsc --noEmit 2>&1 | tail -5          # Erros TypeScript
npm run build 2>&1 | tail -10             # Erros de build
grep -c 'export async function' lib/api.ts # Contagem de funções
ls -la hooks/useRole.ts                   # Arquivo existe?
```

### R6 — Máximo paralelismo

Agentes que não compartilham arquivos rodam em paralelo:
- **MESMO arquivo** → serial (um depois do outro)
- **Arquivos diferentes** → paralelo (dispatch juntos)

### R7 — Estado no filesystem, não na conversa

Atualize `/Users/familia/intensicare/docs/audit/handoff-ive/HANDOFF.yaml`:
```yaml
phase: "FASE 2"
milestone: "M2.1"
agent: "Agente A"
page: "care-pathways/page.tsx"
status: "DONE"
gatekeeper: "grep mock = 0 | npm run build = PASS"
```

### R8 — Subagentes com contexto RICO

Ao usar `delegate_task`, o `context` DEVE incluir:
1. Path exato do arquivo a editar
2. Trecho de código ANTES (mock) e DEPOIS (API) como exemplo
3. Funções exatas a importar de `@/lib/api`
4. Template de estado loading/error
5. Comando de verificação do gatekeeper

Contexto pobre = subagente genérico = retrabalho.

---

## ═══════ CONSTRAINTS ═══════

1. **NÃO modificar o backend.** Zero alterações em `src/intensicare/`.
2. **NÃO modificar contratos OpenAPI.** Zero alterações em `docs/contracts/`.
3. **NÃO quebrar páginas que já funcionam.** Dashboard, alert-triage, patient/[id], admin/users, admin/thresholds, login, register — estas JÁ usam API real.
4. **Todo novo código em TypeScript estrito.** Sem `any` nos grupos P0. `unknown` é aceitável nos grupos P1/P2.
5. **Manter tema escuro.** Não alterar `globals.css` ou tokens de tema.
6. **Manter PT-BR.** Labels, mensagens de erro, placeholders em português.

---

## ═══════ DONE WHEN ═══════

### Verificação final (rode estes comandos ao final de TODAS as fases)

```bash
cd /Users/familia/intensicare/frontend-v2

# 1. TypeScript compila sem erros
npx tsc --noEmit
echo "tsc exit: $?"  # DEVE ser 0

# 2. Build Next.js passa
npm run build
echo "build exit: $?"  # DEVE ser 0

# 3. API client completo (17 existentes + 50 novas = 67+)
grep -c 'export async function' lib/api.ts
# DEVE ser ≥ 67

# 4. ZERO páginas com mock data
grep -rl 'mock\|simul\|Simul\|MOCK' app/ --include='*.tsx' | wc -l
# DEVE ser 0

# 5. Breadcrumb integrado
grep 'Breadcrumb' app/layout.tsx
# DEVE mostrar import + <Breadcrumb />

# 6. RBAC implementado
ls -la hooks/useRole.ts components/RequireRole.tsx
# Ambos devem existir

# 7. Tipos atualizados
grep 'encounter_id' lib/api.ts
# DEVE retornar as definições nas interfaces

# 8. Role dropdown
grep 'updateUserRole2' app/admin/users/page.tsx
# DEVE ser chamado com string de role
```

### HANDOFF final

Quando TODOS os checklists acima passarem:
1. Atualizar `docs/audit/handoff-ive/HANDOFF.yaml` com status FINAL
2. Reportar contagens finais (funções, páginas, build status)
3. Listar quaisquer páginas que NÃO puderam ser conectadas (ex: endpoint não existe)

---

## ═══════ ANTI-PATTERNS (NÃO FAÇA ISSO) ═══════

- ❌ Começar a editar sem PLANS.md
- ❌ Mesmo agente que implementa também faz gatekeeper
- ❌ Subagente com mais de 3 arquivos no escopo
- ❌ Deixar `useState(MOCK_DATA)` depois de adicionar API function
- ❌ Página sem estado de loading (tela branca)
- ❌ Página sem estado de erro (crash)
- ❌ `any` em tipos de Grupo P0 (TDD domains)
- ❌ Breadcrumb importado mas não renderizado
- ❌ Role dropdown que não persiste (sem chamada à API)
- ❌ Pular gatekeeper "porque foi só uma linha"
- ❌ Parar no primeiro milestone que falhar — o loop PERSISTE

---

## ═══════ REFERENCE ═══════

- **HANDOFF.md:** `/Users/familia/intensicare/docs/audit/handoff-ive/HANDOFF.md` ← ESPECIFICAÇÃO COMPLETA
- **Frontend audit:** `/Users/familia/intensicare/docs/audit/FRONTEND_AUDIT.md`
- **API client atual:** `/Users/familia/intensicare/frontend-v2/lib/api.ts`
- **Layout atual:** `/Users/familia/intensicare/frontend-v2/app/layout.tsx`
- **Contratos:** `/Users/familia/intensicare/docs/contracts/`
- **Síntese forense:** `/Users/familia/intensicare/docs/audit/FORENSICS_SYNTHESIS.md`
