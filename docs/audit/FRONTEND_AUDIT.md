# 🔍 Auditoria de Frontend — IntensiCare v2

**Data:** 2026-07-09 | **Auditor:** Niemeyer (System Architect)  
**Escopo:** Verificar se todas as adições do backend estão corretamente consumidas e exibidas no frontend  
**Metodologia:** RECON → Cross-reference API↔Cliente → Integração de Componentes → Mock Data Audit

---

## Sumário Executivo

O backend do IntensiCare teve **30 gaps fechados** na remediação de 2026-07-09. Esta auditoria verifica se o frontend reflete essas adições. **Resultado: o frontend está significativamente atrás do backend em termos de integração.** 22 de 33 páginas usam dados mock. O componente Breadcrumb (183 linhas, 30+ rotas mapeadas) foi criado mas nunca integrado. Apenas 7 de 24 routers backend têm funções correspondentes no cliente API.

**Score de Integração Frontend:** 34/100

---

## 1. Cobertura da API Client (`lib/api.ts`)

### Backend Routers vs Funções no Cliente

| Backend Router | Endpoints | Função no Cliente | Status |
|---------------|-----------|-------------------|--------|
| `auth` | 3 | `loginApi`, `registerApi`, `logoutApi` | ✅ COMPLETO |
| `dashboard` | 2 | `fetchDashboard` | ✅ COMPLETO |
| `alerts` | 5 | `fetchAlerts`, `acknowledgeAlert`, `resolveAlert`, `escalateAlert` | ✅ COMPLETO |
| `admin` (users) | 3 | `fetchUsers`, `createUser`, `updateUser` | ✅ COMPLETO |
| `thresholds` | 3 | `fetchThresholds`, `updateThreshold`, `createThreshold` | ✅ COMPLETO |
| `health` | 1 | `fetchHealth` | ✅ COMPLETO |
| `patients` (detail) | 1 | `fetchPatientDetail` | ✅ PARCIAL (só detail) |
| `pathways` | 6 | — | 🔴 AUSENTE |
| `prescricao` | 5 | — | 🔴 AUSENTE |
| `movimentacao` | 4 | — | 🔴 AUSENTE |
| `formularios` | 3 | — (raw fetch na página) | 🟡 PARCIAL |
| `evolucoes` | 3 | — | 🔴 AUSENTE |
| `ventilation` | 2 | — | 🔴 AUSENTE |
| `stability` | 2 | — | 🔴 AUSENTE |
| `sedacao` | 2 | — | 🔴 AUSENTE |
| `deterioration` | 2 | — | 🔴 AUSENTE |
| `antimicrobial` | 4 | — | 🔴 AUSENTE |
| `prophylaxis` | 4 | — | 🔴 AUSENTE |
| `efficiency` | 1 | — | 🔴 AUSENTE |
| `indicators` | 3 | — | 🔴 AUSENTE |
| `documentacao` | 2 | — | 🔴 AUSENTE |
| `alert_routing` | 5 | — | 🔴 AUSENTE |
| `registry` | 6 | — | 🔴 AUSENTE |
| `events` (WS) | 1 | — | 🔴 AUSENTE |

**Resumo:** 7/24 routers cobertos (29%). 17 routers sem funções no cliente.

---

## 2. Mock Data: O Gap Principal

### Páginas com API Real vs Mock

| Página | Fonte de Dados | API Client |
|--------|---------------|------------|
| **dashboard** | `fetchDashboard()` | ✅ Real |
| **command-center** | `fetchDashboard()` | ✅ Real |
| **alert-triage** | `fetchAlerts()` | ✅ Real |
| **sepse-dashboard** | `fetchAlerts()` + `fetchPatientDetail()` | ✅ Real |
| **patient/[id]** | `fetchPatientDetail()` | ✅ Real |
| **admin/thresholds** | `fetchThresholds()` | ✅ Real |
| **admin/users** | `fetchUsers()` | ✅ Real |
| **admin (dashboard)** | `fetchAdminStats()` | ✅ Real |
| **login** | `loginApi()` | ✅ Real |
| **register** | `registerApi()` | ✅ Real |
| **clinical-forms** | `fetch('/api/clinical-forms')` raw | 🟡 Parcial |
| **care-pathways** | "mock: all in the dropdown" | 🔴 Mock |
| **prescription** | "Simula chamada à API" | 🔴 Mock |
| **patient-movement** | "Dados mock indisponíveis" | 🔴 Mock |
| **clinical-notes** | "Simulate initial load" | 🔴 Mock |
| **sedation** | "MockSedationPatient" | 🔴 Mock |
| **ventilation** | "generateMockTrend" | 🔴 Mock |
| **stability** | "Mock Patients" | 🔴 Mock |
| **clinical-deterioration** | "using mock data per spec" | 🔴 Mock |
| **fluid-balance** | "Simula carregamento" | 🔴 Mock |
| **antimicrobial-stewardship** | "Mock async save" | 🔴 Mock |
| **prophylaxis-bundles** | "Simulate loading state" | 🔴 Mock |
| **nutrition** | "Mock async save" | 🔴 Mock |
| **indicators** | "Simula fetch — usa mock" | 🔴 Mock |
| **efficiency** | "Simula novo fetch" | 🔴 Mock |
| **documentation** | "Mock submit" | 🔴 Mock |
| **alert-routing** | "Simulated API call" | 🔴 Mock |
| **handoff** | "Simulate data loading" | 🔴 Mock |
| **communication** | "Simulated initial load" | 🔴 Mock |
| **admin/registry** | "Dados mock indisponíveis" | 🔴 Mock |
| **admin/tenancy** | "mock data loads instantly" | 🔴 Mock |
| **admin/audit-log** | "Simula carregamento inicial" | 🔴 Mock |

**Resumo:** 11/33 páginas com API real (33%). 22/33 páginas com mock (67%).

---

## 3. Componentes Novos: Criados mas Não Integrados

### Breadcrumb (`components/Breadcrumb.tsx` — 183 linhas)

| Aspecto | Status | Detalhe |
|---------|--------|---------|
| Componente existe | ✅ | 183 linhas, TypeScript, acessível |
| Hook `useBreadcrumbs` | ✅ | 30+ mapeamentos de rota em PT-BR |
| Integrado no layout | 🔴 NÃO | Nenhuma página importa Breadcrumb |
| Usado em alguma página | 🔴 NÃO | Zero usos em todo o frontend |
| Suporte a UUID dinâmico | ✅ | Detecta e encurta UUIDs |
| Acessibilidade | ✅ | `aria-label`, `aria-current`, focus-visible |

**Gap:** Componente completo e bem escrito, mas **nunca foi integrado ao layout ou a qualquer página.** É código morto. Deveria estar no `layout.tsx` acima do `{children}`.

### OverlayStack (`components/OverlayStack.tsx` — 254 linhas)

| Aspecto | Status | Detalhe |
|---------|--------|---------|
| Componente existe | ✅ | 254 linhas, Radix Dialog, z-index stacking |
| Hook existe | ✅ | `hooks/useOverlayStack.tsx` (duplicado?) |
| Provider no layout | ✅ | `<OverlayStackProvider>` importado de `@/hooks/useOverlayStack` |
| Esc key support | ✅ | Fecha overlay no topo da pilha |
| Focus trapping | ✅ | Radix Dialog nativo |
| Browser back support | ✅ | Implementado |

**Gap:** O layout importa de `@/hooks/useOverlayStack` mas o componente principal está em `@/components/OverlayStack`. Possível duplicação. Nenhuma página usa `useOverlayStack()` para abrir drawers.

### TenantProvider (`components/TenantProvider.tsx` — 41 linhas)

| Aspecto | Status | Detalhe |
|---------|--------|---------|
| Componente existe | ✅ | 41 linhas, useEffect, localStorage |
| Integrado no layout | ✅ | `<TenantProvider tenant="default" />` |
| Suporte multi-tenant | 🟡 PARCIAL | Hardcoded para "default" |
| Leitura dinâmica | ✅ | Lê `localStorage.getItem('intensicare:tenant')` |
| CSS custom properties | ✅ | `data-tenant` attribute no `<html>` |

**Gap:** O tenant é hardcoded como `"default"`. O `localStorage` fallback existe mas nunca é populado por nenhuma página. O white-label funciona tecnicamente, mas não há UI para trocar de tenant.

---

## 4. RBAC no Frontend

### O que o backend entrega (pós gap-closure C7):
- Campo `role` no modelo `User` com 7 valores: `medico`, `enfermeiro`, `fisioterapeuta`, `farmacia`, `nutricao`, `admin`, `readonly`
- `require_medico()`, `require_enfermeiro()`, etc. no backend

### O que o frontend consome:

| Aspecto | Status | Detalhe |
|---------|--------|---------|
| Tipo `UserResponse` tem `role` | ✅ | `role: string \| null` na interface |
| Tipo `UserUpdateRequest` tem `role` | ✅ | `role?: string \| null` |
| Função `updateUserRole2` | ✅ | `updateUserRole2(userId, role)` — envia role string |
| UI para selecionar role | 🔴 NÃO | Página de admin/users não tem dropdown de role |
| Route guards por role | 🔴 NÃO | Middleware só verifica auth, não role |
| Condicional rendering por role | 🔴 NÃO | Nenhuma página esconde/mostra conteúdo por role |
| `is_admin` ainda é usado | 🟡 SIM | `is_admin: boolean` no UserResponse |

**Gap:** O backend suporta 7 roles granulares, mas o frontend ainda opera com o modelo binário `is_admin`. A interface `UserResponse` tem o campo `role` mas nenhuma página o utiliza para controle de acesso.

---

## 5. `encounter_id` e Content-Addressing no Frontend

### O que o backend entrega (pós gap-closure C4, C5):
- `encounter_id` no `PatientPathway`
- `definition_version_id` (SHA-256) no `PathwayDefinition`

### O que o frontend consome:

| Aspecto | Status | Detalhe |
|---------|--------|---------|
| `PatientBedSummary` tem `encounter_id` | 🔴 NÃO | Interface não inclui o campo |
| `PatientDetailResponse` tem `encounter_id` | 🔴 NÃO | Interface não inclui o campo |
| `PathwaySchema` tem `definition_version_id` | 🔴 NÃO | API client não tem tipos de pathway |
| Páginas exibem `encounter_id` | 🔴 NÃO | Nenhuma página referencia |
| Páginas exibem content hash | 🔴 NÃO | Nenhuma página referencia |

**Gap:** As adições de `encounter_id` e content-addressing (SHA-256) estão completamente ausentes do frontend. Os tipos TypeScript não foram atualizados.

---

## 6. Design Tokens e Temas

| Aspecto | Status | Detalhe |
|---------|--------|---------|
| Style Dictionary pipeline | ✅ | `design-tokens/` com build script |
| CSS custom properties | ✅ | `globals.css` com variáveis |
| Tema escuro default | ✅ | `<html data-theme="dark">` |
| Tema claro alternativo | ✅ | `[data-theme="light"]` definido |
| Neumorphic elevation | 🟡 | Tokens definidos, sem uso visível em componentes |
| Per-tenant colors | 🟡 | `data-tenant` attribute existe mas hardcoded |
| Tailwind violations | 🟡 | 38 restantes (dark theme intencional) |

---

## 7. Resumo de Gaps por Severidade

### 🔴 CRÍTICO (5)

| ID | Gap | Impacto |
|----|-----|---------|
| F01 | **16/24 routers backend sem funções no cliente API** | Backend expõe endpoints que o frontend não consegue consumir |
| F02 | **22/33 páginas com dados mock** | Maioria das páginas não está integrada com backend real |
| F03 | **Breadcrumb criado mas NUNCA integrado** | Componente de 183 linhas é código morto |
| F04 | **RBAC granular não implementado no frontend** | 7 roles no backend, mas frontend só usa `is_admin` binário |
| F05 | **`encounter_id` e content-addressing ausentes dos tipos** | Adições críticas do backend invisíveis no frontend |

### 🟡 ALTO (5)

| ID | Gap | Impacto |
|----|-----|---------|
| F06 | TenantProvider hardcoded para "default" | White-label existe mas não é funcional |
| F07 | Nenhuma página usa `useOverlayStack()` | Drawer-in-drawer não implementado apesar do componente existir |
| F08 | Rotas de prescricao não alinhadas | Backend mudou rotas (H3), frontend não acompanhou |
| F09 | TypeScript types desatualizados | `PatientBedSummary` sem `encounter_id`, sem tipos de pathway/prescricao |
| F10 | Middleware sem RBAC | Qualquer usuário autenticado acessa qualquer página |

### 🟠 MÉDIO (4)

| ID | Gap | Impacto |
|----|-----|---------|
| F11 | `clinical-forms` usa fetch raw em vez da API client | Inconsistência com padrão do projeto |
| F12 | `admin:admin` no RTSP builder | Já corrigido no backend (M11), mas frontend não verificado |
| F13 | Formulários offline-first (M8) não implementado | Service Worker + IndexedDB ausentes |
| F14 | Sem tratamento de erro 409/422 específicos | Páginas mock não testam cenários de erro do backend |

### 🟢 BAIXO (2)

| ID | Gap | Impacto |
|----|-----|---------|
| F15 | Sem testes E2E ou de integração | Cypress/Playwright não configurados |
| F16 | AlertCard tem stories mas sem testes unitários | Storybook cobre visual, não lógica |

---

## 8. Recomendações

### Imediato (este sprint)

1. **Adicionar funções no `lib/api.ts`** para os 16 routers faltantes:
   ```typescript
   // pathways
   fetchPathways, fetchPathway, enrollPatient, updateCriteria, getProgress
   // prescricao
   fetchPrescriptions, createPrescription, updatePrescription, transitionState
   // movimentacao
   fetchMovements, registerMovement, fetchBedGrid, updateBedStatus
   // ... etc
   ```

2. **Integrar Breadcrumb** no `layout.tsx`:
   ```tsx
   import Breadcrumb from '@/components/Breadcrumb';
   // No layout:
   <Breadcrumb />
   {children}
   ```

3. **Atualizar tipos TypeScript** com `encounter_id`, `definition_version_id`, `role` enum:
   ```typescript
   interface PatientBedSummary {
     encounter_id: string;  // NOVO
     // ...
   }
   ```

### Curto Prazo (2 sprints)

4. **Conectar páginas mock ao backend** — prioridade:
   - P0: `prescription`, `care-pathways`, `patient-movement` (domínios TDD)
   - P1: `clinical-notes`, `sedation`, `ventilation`, `stability`
   - P2: `indicators`, `efficiency`, `antimicrobial`, `prophylaxis`

5. **Implementar RBAC no frontend**:
   - `useRole()` hook que lê `UserResponse.role`
   - `RequireRole` componente wrapper
   - Middleware com role-based routing

6. **Conectar TenantProvider** ao contexto de autenticação:
   - Popular `localStorage('intensicare:tenant')` após login
   - Expor tenant atual em `useUser()` hook

### Médio Prazo

7. **Testes E2E** com Cypress ou Playwright
8. **Offline-first** forms (IndexedDB + Service Worker)
9. **Storybook** para todos os componentes (23 existentes, ~15 sem stories)

---

## 9. Métricas

| Métrica | Valor |
|---------|-------|
| Total de páginas | 33 |
| Páginas com API real | 11 (33%) |
| Páginas com mock | 22 (67%) |
| Componentes | 23 |
| Componentes integrados ao layout | 2/3 novos (TenantProvider ✅, OverlayStack ✅, Breadcrumb 🔴) |
| Backend routers | 24 |
| API client functions | 17 |
| Routers SEM função no cliente | 17/24 (71%) |
| Tipos TypeScript atualizados pós gap-closure | 0/5 adições críticas |

---

## 10. Conclusão

**O frontend NÃO reflete as 30 adições do backend.** O gap principal não é de código ausente — é de **integração**. Os componentes existem (Breadcrumb, OverlayStack, TenantProvider), a API client está parcialmente implementada, e as páginas têm UI completa. Mas a camada de conexão entre frontend e backend está **77% mockada**.

**Score de Integração Frontend: 34/100**

**Ações prioritárias:**
1. Completar `lib/api.ts` com funções para todos os 24 routers (17 faltantes)
2. Conectar as 5 páginas TDD ao backend real (prescription, care-pathways, patient-movement, clinical-forms, clinical-notes)
3. Integrar Breadcrumb ao layout
4. Implementar RBAC granular no frontend

---

*Relatório gerado por Niemeyer (System Architect). Baseline: backend pós gap-closure (30 gaps fechados) vs frontend-v2 atual.*
