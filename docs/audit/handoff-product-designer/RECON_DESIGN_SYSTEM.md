# RECON Design System — IntensiCare Frontend v2

> **Milestone:** M0 — FASE 0 (RECON)
> **Propósito:** Catálogo completo de ativos de design existentes para handoff ao Product Designer.
> **Regra:** Somente leitura. Nenhum arquivo foi modificado.
> **Data:** 2026-07-07
> **Projeto:** IntensiCare — Sistema de Suporte à Decisão Clínica para UTI

---

## 1. Resumo Executivo

### Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| Framework | Next.js (App Router) | ^15.0.0 |
| UI Library | React | ^19.0.0 |
| Estilização | Tailwind CSS + CSS Custom Properties | ^4.0.0 |
| Design Tokens | Style Dictionary (build-tokens) | ^5.5.0 |
| Componentes Primitivos | Radix UI (Dialog, Dropdown, Popover, Select, Tabs, Toast, Tooltip) | — |
| Ícones | Lucide React | ^0.400.0 |
| Tabelas | TanStack Table | ^8.21.3 |
| Gráficos | Recharts | ^3.9.2 |
| Formulários | react-hook-form + zod | ^7.81.0 / ^4.4.3 |
| Storybook | Storybook + @storybook/nextjs | ^10.4.6 |
| Linguagem | TypeScript | ^5.5.0 |

### Totais do Inventário

| Categoria | Quantidade |
|-----------|-----------|
| Design Tokens (CSS custom properties) | ~180 tokens em 12 famílias |
| Componentes React | 6 (5 com stories) |
| Stories (Storybook) | 44 variantes |
| Endpoints de API | 16 funções em 8 domínios |
| Tipos TypeScript exportados | 30+ interfaces/types |
| Hooks React | 4 (2 gerais + 2 usePatientWebSocket/useKeyboardShortcuts) |
| Rotas (pages) | 13 page.tsx |
| Layouts | 2 (Layout padrão + FullScreenLayout) |
| Bibliotecas de utilidade | 7 arquivos em `lib/` |

### Gaps Identificados (visão geral)

1. **Tokens domain-specific ausentes:** Não existem tokens para domínios clínicos específicos (sepse, antimicrobiano, profilaxia, delirium, etc.)
2. **ClinicalTooltip sem stories:** Único componente sem cobertura de Storybook
3. **Sem testes de componente:** Nenhum teste unitário ou de integração para componentes React
4. **Form engine sem implementação de renderização:** `lib/form-engine/types.ts` define tipos mas não há `FormRenderer`
5. **Thresholds sem UI de gerenciamento visual:** Apenas hook + tipos; admin/thresholds page existe mas está em estado inicial
6. **Sem catálogo de ícones clínicos customizados:** 100% dependente de Lucide — sem ícones específicos de domínio médico
7. **Sem sistema de temas claro/escuro em runtime:** Tokens dark/light existem mas `data-theme` é fixo como `dark` no `:root`

---

## 2. Catálogo de Design Tokens

**Arquivo:** `app/tokens-generated.css` (185 linhas, auto-gerado por Style Dictionary)

### 2.1 Breakpoints
| Token | Valor |
|-------|-------|
| `--breakpoints-sm` | 640px |
| `--breakpoints-md` | 768px |
| `--breakpoints-lg` | 1024px |
| `--breakpoints-xl` | 1280px |
| `--breakpoints-2xl` | 1536px |

### 2.2 Elevation (sombras para camadas)
| Token | Valor | Uso |
|-------|-------|-----|
| `--elevation-none` | none | Superfície base |
| `--elevation-sm` | 4px 4px 8px rgba(0,0,0,0.4) | Small cards, chips, pressed buttons |
| `--elevation-md` | 6px 6px 12px rgba(0,0,0,0.5) | Cards, panels |
| `--elevation-lg` | 8px 8px 16px rgba(0,0,0,0.6) | Modals, overlays |

### 2.3 Motion (duração + easing)
| Token | Valor |
|-------|-------|
| `--motion-duration-instant` | 0ms |
| `--motion-duration-fast` | 150ms |
| `--motion-duration-normal` | 250ms |
| `--motion-duration-slow` | 400ms |
| `--motion-duration-gentle` | 600ms |
| `--motion-easing-standard` | cubic-bezier(0.4, 0.0, 0.2, 1) |
| `--motion-easing-decelerate` | cubic-bezier(0.0, 0.0, 0.2, 1) |
| `--motion-easing-accelerate` | cubic-bezier(0.4, 0.0, 1, 1) |

### 2.4 Radius
| Token | Valor | Uso |
|-------|-------|-----|
| `--radius-sm` | 4px | Buttons, chips, inputs |
| `--radius-md` | 8px | Cards, panels |
| `--radius-lg` | 12px | Modals, dialogs |
| `--radius-xl` | 16px | Drawers, large containers |
| `--radius-full` | 9999px | Avatars, status dots, pills |

### 2.5 Spacing (escala 4px-based)
| Token | Valor | Token | Valor |
|-------|-------|-------|-------|
| `--spacing-0` | 0px | `--spacing-8` | 32px |
| `--spacing-1` | 4px | `--spacing-10` | 40px |
| `--spacing-2` | 8px | `--spacing-12` | 48px |
| `--spacing-3` | 12px | `--spacing-16` | 64px |
| `--spacing-4` | 16px | `--spacing-20` | 80px |
| `--spacing-5` | 20px | `--spacing-24` | 96px |
| `--spacing-6` | 24px | | |

### 2.6 Typography
| Família | Tokens |
|---------|--------|
| **Font family** | `--type-font-family-sans` (Inter), `--type-font-family-mono` (JetBrains Mono) |
| **Font size** | xs (0.6875rem), sm (0.8125rem), base (0.9375rem), lg (1.0625rem), xl (1.25rem), 2xl (1.5rem), 3xl (1.875rem) |
| **Font weight** | normal (400), medium (500), semibold (600), bold (700) |
| **Line height** | tight (1.25), normal (1.5), relaxed (1.75) |

### 2.7 Z-Index
| Token | Valor | Uso |
|-------|-------|-----|
| `--z-index-dropdown` | 100 | Dropdowns, autocomplete, select menus |
| `--z-index-sticky` | 200 | Sticky headers, fixed nav bars |
| `--z-index-overlay` | 300 | Overlays, backdrops, drawers |
| `--z-index-modal` | 400 | Modals, dialogs, popovers |
| `--z-index-toast` | 500 | Toasts, notifications, tooltips |

### 2.8 Clinical Severity (normal/watch/urgent/critical)

Cada nível tem 7 variantes:

| Variante | Propósito | Exemplo (critical) |
|----------|-----------|-------------------|
| `-on-surface-dark` | Texto/ícone em superfície escura | `#F5828F` (AAA 7.68:1) |
| `-on-surface-light` | Texto/ícone em superfície clara | `#E83D54` (AAA 7.01:1) |
| `-signal-dark` | Status dot / border-glow em dark | `#FF3B4A` (AA ≥7.8:1) |
| `-signal-light` | Status dot / border-glow em light | `#D01024` (AA ≥5.2:1) |
| `-fill` | Background de chip/badge | `#B20E22` |
| `-on-fill` | Texto branco sobre fill | `#FFFFFF` (AAA 7.05:1) |
| `-wash` | Row/card tint (alpha variável) | `#B20E22` |

Todos os tokens são calibrados para WCAG AA/AAA.

### 2.9 Clinical Status

| Token | Valor | Uso |
|-------|-------|-----|
| `--clinical-status-attended-color` | `#2B7ABF` | Blue dot, person-check icon |
| `--clinical-status-attended-on-color` | `#FFFFFF` | Texto sobre attended badge |
| `--clinical-status-stale-color` | `#8A8F99` | Gray dot, clock-alert, dashed border |
| `--clinical-status-stale-on-color` | `#FFFFFF` | Texto sobre stale badge |

### 2.10 Action Tokens

| Família | Tokens |
|---------|--------|
| **Primary** | `--action-primary-bg-{dark,light}`, `--action-primary-text-{dark,light}`, `--action-primary-hover-{dark,light}` |
| **Secondary** | `--action-secondary-bg-{dark,light}`, `--action-secondary-text-{dark,light}`, `--action-secondary-border-{dark,light}` |
| **Danger** | `--action-danger-bg-{dark,light}`, `--action-danger-text-{dark,light}`, `--action-danger-hover-{dark,light}` |
| **Disabled** | `--action-disabled-opacity: 0.5` |

### 2.11 Semantic Aliases

| Token | Aponta para |
|-------|------------|
| `--semantic-alert-{severity}-*` | `var(--clinical-severity-{severity}-*)` |
| `--semantic-surface-canvas-{dark,light}` | Background base da página |
| `--semantic-surface-raised-{dark,light}` | Cards, panels |
| `--semantic-surface-overlay-{dark,light}` | Modals, drawers |
| `--semantic-border-default-{dark,light}` | Bordas padrão |
| `--semantic-text-primary-{dark,light}` | Texto principal |
| `--semantic-text-secondary-{dark,light}` | Texto secundário |

### 2.12 Feedback (success/warning/error/info)

Cada tipo tem 5 tokens: `-bg`, `-text`, `-border`, `-icon` (dark + light).

### ⚠️ GAP: Tokens Domain-Specific Ausentes

**NÃO existem** tokens para os seguintes domínios clínicos (serão criados em M1):
- `--clinical-sepsis-*`
- `--clinical-antimicrobial-*`
- `--clinical-prophylaxis-*`
- `--clinical-delirium-*`
- `--clinical-aki-*` (Acute Kidney Injury)
- `--clinical-hemo-*` (hemodinâmica)
- `--clinical-respiratory-*`
- `--clinical-fluid-balance-*`
- `--clinical-electrolyte-*`
- `--clinical-nutrition-*`
- `--clinical-pharmaco-*`
- `--clinical-movimentacao-*`
- `--clinical-comunicacao-*`
- `--clinical-operacional-*`

---

## 3. Catálogo de Componentes

### 3.1 Tabela Resumo

| Componente | Arquivo | Linhas | Props | Stories | Estados Cobertos |
|-----------|---------|--------|-------|---------|-----------------|
| **AlertCard** | `components/AlertCard.tsx` | 469 | `alert: AlertInfo`, `onUpdate: () => void` | ✅ 11 stories | active, acknowledged, escalated, resolved, critical, watch, why-panel (expandido/fechado), sem body, sem mpi_id, full detail |
| **SeverityBadge** | `components/SeverityBadge.tsx` | 283 | `severity: Severity`, `className?: string`, `showLabel?: boolean` | ✅ 16 stories | normal, watch, urgent, critical, info, com/sem label, pulse (critical), all severities grid |
| **TrendBadge** | `components/SeverityBadge.tsx` | (exportado do mesmo arquivo) | `trend: string \| null`, `className?: string` | ✅ 4 stories | increasing, decreasing, stable, unknown |
| **ScoreDisplay** | `components/SeverityBadge.tsx` | (exportado do mesmo arquivo) | `label: string`, `score: number \| null`, `risk?: string`, `trend?: string`, `className?: string` | ✅ 7 stories | MEWS low/med/high, NEWS2 low/med/high, score null, grid |
| **ClinicalTooltip** | `components/ClinicalTooltip.tsx` | 71 | `term: string`, `children: ReactNode`, `side?: 'top'\|'right'\|'bottom'\|'left'`, `sideOffset?: number` | ❌ SEM STORIES | — |
| **Layout** | `components/Layout.tsx` | 380 | `children: ReactNode` | ✅ 6 stories | sidebar padrão, admin user, mobile, FullScreenLayout, FullScreenLayout mobile, login page bypass |
| **FullScreenLayout** | `components/Layout.tsx` | (exportado do mesmo arquivo) | `children: ReactNode` | ✅ 2 stories | default, mobile |
| **DrawerBuilder** | `components/DrawerBuilder.tsx` | 79 | `open: boolean`, `onClose: () => void`, `title?: string`, `children: ReactNode`, `size?: 'sm'\|'md'\|'lg'\|'full'` | ✅ 7 stories | sm, md, lg, full, sem título, fechado, default |
| **ErrorBoundary** | `components/ErrorBoundary.tsx` | 92 | `children: ReactNode`, `fallback?: ReactNode` | ✅ 4 stories | normal render, with error (long message), with error (short message), custom fallback |

### 3.2 Detalhamento por Componente

#### AlertCard (`components/AlertCard.tsx` — 469 linhas)

**Descrição:** Card de alerta clínico com ações de acknowledge, resolve e escalate. Inclui painel "Why This Alert?" expansível que mostra parâmetros que dispararam o alerta.

**Estados de status:**
| Status | Cor de badge | Ações disponíveis |
|--------|-------------|-------------------|
| `active` | critical-wash | Acknowledge, Resolve, Escalate |
| `acknowledged` | attended (azul) | Resolve, Escalate |
| `escalated` | urgent-wash | Resolve |
| `resolved` | normal-wash | Nenhuma (somente visualização) |

**Estados internos:** loading (por ação), error, confirmAction (confirmação antes de resolver/escalar), whyPanelOpen.

**Dependências:** `DrawerBuilder`, `SeverityBadge`, `lib/api` (acknowledgeAlert, resolveAlert, escalateAlert), `lucide-react` (CheckCircle, XCircle, ArrowUpCircle, Clock, AlertTriangle, ChevronDown, ChevronUp, Info).

**Reusabilidade:** Alta. Usado em dashboard, alert-triage, patient detail.

---

#### SeverityBadge (`components/SeverityBadge.tsx` — 283 linhas)

**Descrição:** Badge de severidade com encoding visual canônico por forma + cor (spec: `docs/plan/_work/platform/severity-model.yaml`).

**Encoding visual por severidade:**

| Severity | Forma | Ícone | Cor Fill | Pulse |
|----------|-------|-------|----------|-------|
| `normal` | Círculo (rounded-full) | CheckCircle | Verde | Não |
| `watch` | Quadrado arredondado (6px) | Eye | Amarelo | Não |
| `urgent` | Triângulo (clipPath polygon) | AlertTriangle | Laranja | Não |
| `critical` | Octógono (clipPath polygon) | AlertOctagon | Vermelho | Sim |
| `info` | Círculo (rounded-full) | Info | Verde (normal) | Não |

**Acessibilidade:** `aria-label`, `role="alert"` + `aria-live="assertive"` para critical.

**Sub-componentes exportados:**
- `TrendBadge`: Indicador de tendência (increasing/decreasing/stable)
- `ScoreDisplay`: Display de score (MEWS/NEWS2) com cor por severidade

---

#### ClinicalTooltip (`components/ClinicalTooltip.tsx` — 71 linhas)

**Descrição:** Tooltip para abreviações clínicas (PT-BR) usando Radix Tooltip. Dicionário interno com 9 termos: MEWS, NEWS2, RASS, CAM-ICU, SOFA, qSOFA, AVPU, BPS, NRS.

**⚠️ GAP:** Sem stories. Storybook coverage ausente.

---

#### Layout (`components/Layout.tsx` — 380 linhas)

**Descrição:** Layout principal com sidebar fixa (desktop) + drawer mobile. Inclui drawer de ajuda com atalhos de teclado.

**Sidebar — Itens de Navegação:**

**Seção Clínico:**
| Rota | Label | Ícone |
|------|-------|-------|
| `/dashboard` | Painel | LayoutDashboard |
| `/command-center` | Central de Comando | Activity |
| `/alert-triage` | Triagem de Alertas | Bell |

**Seção Administração** (visível apenas para admin):
| Rota | Label | Ícone |
|------|-------|-------|
| `/admin` | Administração | Shield |
| `/admin/users` | Usuários | UserCog |
| `/admin/thresholds` | Limiares | Sliders |

**Estados:** desktop com sidebar, mobile com header + drawer, login/register bypass (sem sidebar), FullScreenLayout (top bar minimalista).

**Atalhos de teclado globais:** `?` (ajuda), `/` (foco busca), `1-4` (filtrar severidade), `Esc` (limpar filtros), `j/k` ou `↓/↑` (navegar lista).

---

#### DrawerBuilder (`components/DrawerBuilder.tsx` — 79 linhas)

**Descrição:** Wrapper sobre Radix Dialog para drawers modais. Suporta 4 tamanhos.

**Tamanhos:** `sm` (max-w-sm), `md` (max-w-md, default), `lg` (max-w-lg), `full` (viewport inteiro).

**Estados:** aberto com overlay, aberto sem título, fechado.

---

#### ErrorBoundary (`components/ErrorBoundary.tsx` — 92 linhas)

**Descrição:** React Error Boundary class component. Exibe fallback com mensagem de erro + botão "Retry".

**Estados:** normal (renderiza children), erro (default fallback com AlertTriangle + mensagem + retry), erro com fallback customizado.

---

## 4. Catálogo de API Client

**Arquivo:** `lib/api.ts` (409 linhas)

### 4.1 Mecanismo de Request

- **Wrapper:** `request<T>(url, options) → Promise<T>`
- **Autenticação:** JWT Bearer token via `Authorization` header
- **401 handling:** Limpa token e redireciona para `/login`
- **Erro:** `ApiError` class com `status` e `detail`

### 4.2 Endpoints

#### Auth
| Função | Método | Endpoint | Request | Response |
|--------|--------|----------|---------|----------|
| `loginApi` | POST | `/auth/login` | `LoginRequest` | `TokenResponse` |
| `registerApi` | POST | `/auth/register` | `RegisterRequest` | `UserResponse` |
| `logoutApi` | POST | `/auth/logout` | — | void |

#### Dashboard
| Função | Método | Endpoint | Response |
|--------|--------|----------|----------|
| `fetchDashboard(unit?)` | GET | `/api/v1/dashboard?unit=` | `DashboardResponse` |

#### Patient
| Função | Método | Endpoint | Response |
|--------|--------|----------|----------|
| `fetchPatientDetail(mpiId)` | GET | `/api/v1/patients/:mpiId/detail` | `PatientDetailResponse` |

#### Alerts
| Função | Método | Endpoint | Response |
|--------|--------|----------|----------|
| `fetchAlerts(params?)` | GET | `/api/v1/alerts` | `AlertListResponse` |
| `acknowledgeAlert(id, notes?)` | POST | `/api/v1/alerts/:id/acknowledge` | `AlertInfo` |
| `resolveAlert(id, resolution, note?)` | POST | `/api/v1/alerts/:id/resolve` | `AlertInfo` |
| `escalateAlert(id, reason?)` | POST | `/api/v1/alerts/:id/escalate` | `AlertInfo` |

#### Admin
| Função | Método | Endpoint |
|--------|--------|----------|
| `fetchUsers()` | GET | `/admin/users` |
| `createUser(data)` | POST | `/admin/users` |
| `updateUser(id, data)` | PUT | `/admin/users/:id` |
| `updateUserRole(id, isAdmin)` | Helper | Chama updateUser |
| `toggleUserActive(id, isActive)` | Helper | Chama updateUser |
| `updateUserRole2(id, role)` | Helper | Chama updateUser |

#### Thresholds
| Função | Método | Endpoint |
|--------|--------|----------|
| `fetchThresholds(tenantId?)` | GET | `/api/v1/thresholds` |
| `updateThreshold(id, data)` | PUT | `/api/v1/thresholds/:id` |
| `createThreshold(data)` | POST | `/api/v1/thresholds` |

#### Stats
| Função | Resposta |
|--------|----------|
| `fetchAdminStats()` | `AdminStatsResponse` (aggregado de users + thresholds + alerts) |

#### Health
| Função | Endpoint |
|--------|----------|
| `fetchHealth()` | `/health` |

### 4.3 Tipos Exportados (30+)

| Tipo | Campos principais |
|------|------------------|
| `LoginRequest` | username, password |
| `TokenResponse` | access_token, refresh_token, token_type |
| `RegisterRequest` | username, email, password, display_name? |
| `UserResponse` | id, username, email, display_name, is_admin, is_active, role, created_at |
| `DashboardResponse` | patients[], total, active_alerts_total |
| `PatientBedSummary` | mpi_id, bed_id, display_name, unit, latest_mews, latest_news2, active_alerts_count, highest_alert_severity, latest_vitals, last_updated |
| `LatestVitals` | heart_rate, systolic_bp, diastolic_bp, spo2, respiratory_rate, temperature, recorded_at |
| `PatientDetailResponse` | mpi_id, bed_id, display_name, unit, vitals_history[], mews_history[], news2_history[], active_alerts[] |
| `AlertInfo` | id, mpi_id, severity, status, title, body, created_at, acknowledged_at, resolved_at, triggering_parameters?, rule_reference?, alert_definition_version?, data_coverage_note? |
| `TriggeringParameter` | name, value, threshold, unit?, breached |
| `VitalsHistoryPoint` | recorded_at + 7 sinais vitais |
| `ScoreHistoryPoint` | calculated_at, score_type, score_value, trend |
| `UserListResponse` | users[], total |
| `UserCreateRequest` | username, email, password, display_name?, is_admin?, is_active?, role? |
| `UserUpdateRequest` | display_name?, is_admin?, is_active?, email?, role? |
| `ThresholdConfigResponse` | id, tenant_id, unit, score_type, watch_threshold, urgent_threshold, critical_threshold, rate_limit_per_hour, cooldown_minutes, updated_at, updated_by |
| `ThresholdConfigUpdate` | Partial de ThresholdConfigResponse |
| `AdminStatsResponse` | total_users, active_alerts, thresholds_configured |
| `HealthResponse` | status, version, environment, checks |

---

## 5. Catálogo de WebSocket

**Arquivo:** `lib/websocket.ts` (380 linhas)

### 5.1 Eventos

| Evento | Descrição |
|--------|-----------|
| `alert.raised` | Novo alerta gerado |
| `alert.updated` | Alerta existente modificado |
| `bed_grid.updated` | Atualização no grid de leitos |
| `presence.updated` | Mudança de presença de usuário |
| `vitals.updated` | Novos sinais vitais recebidos |

### 5.2 API

| Hook/Classe | Descrição |
|------------|-----------|
| `RealtimeConnection` | Singleton com WS primário + SSE fallback, exponential backoff (1s → 32s) |
| `useRealtimeChannel<T>(eventType, onEvent?)` | Hook React: subscribe a um evento, retorna `{status, lastEvent}` |
| `useConnectionStatus()` | Hook React: status da conexão apenas (`ConnectionStatus`) |

### 5.3 Tipos

| Tipo | Definição |
|------|-----------|
| `RealtimeEventType` | Union: `'alert.raised' \| 'alert.updated' \| 'bed_grid.updated' \| 'presence.updated' \| 'vitals.updated'` |
| `RealtimeEvent<T>` | `{ type, payload: T, timestamp }` |
| `ConnectionStatus` | `'connecting' \| 'connected' \| 'disconnected' \| 'error'` |
| `ChannelCallback<T>` | `(event: RealtimeEvent<T>) => void` |

### 5.4 WebSocket Adicional (Patient-Specific)

**Arquivo:** `hooks/usePatientWebSocket.ts` (122 linhas)

Hook separado para página de paciente: `usePatientWebSocket({mpiId, onUpdate, enabled}) → {connectionState, reconnect}`. Reconexão automática a cada 3s.

---

## 6. Bibliotecas de Utilitários

### 6.1 Auth (`lib/auth.ts` — 90 linhas)

| Função | Descrição |
|--------|-----------|
| `getToken()` | Recupera JWT do sessionStorage |
| `setToken(token)` | Armazena JWT + cookie |
| `clearToken()` | Remove JWT |
| `getUser()` | Recupera UserInfo do sessionStorage |
| `setUser(user)` | Armazena UserInfo |
| `clearUser()` | Remove UserInfo |
| `isAuthenticated()` | Verifica se há token |
| `isAdmin()` | Verifica role admin |
| `logout()` | Limpa tudo + redirect /login |
| `decodeTokenPayload(token)` | Decodifica JWT (sem verificar assinatura) |

**Interface:** `UserInfo { id, username, email, display_name, is_admin, is_active }`

### 6.2 Clinical Severity (`lib/clinical-severity.ts` — 104 linhas)

| Função | Descrição |
|--------|-----------|
| `getSeverityStyle(severity, variant)` | CSSProperties para card ou left-accent border |
| `getSeverityFromAlert(severity)` | Normaliza string → `Severity` |
| `getMEWSSeverity(score)` | Score MEWS → `{colorVar, severity}` |
| `getNEWS2Severity(score)` | Score NEWS2 → `{colorVar, severity}` |
| `getScoreColor(type, value)` | CSS var string por tipo (mews/news2/sofa) |

**Tipo:** `Severity = 'normal' | 'watch' | 'urgent' | 'critical' | 'info'`

### 6.3 Thresholds (`lib/thresholds/`)

**types.ts:** `ThresholdSeverity`, `VitalThreshold`, `ScoreBand`

**useThreshold.ts** (231 linhas):
- Hook `useThreshold()` → `ThresholdAPI`
- Cache de 5 min com fallback para defaults da literatura médica
- 6 sinais vitais com thresholds hardcoded (heart_rate, systolic_bp, diastolic_bp, respiratory_rate, spo2, temperature)
- 1 score band (SOFA: 0-6 normal, 7-9 watch, 10-12 urgent, 13+ critical)
- Helpers: `severityToColorVar()`, `severityToWashVar()`

### 6.4 Form Engine (`lib/form-engine/types.ts`)

**⚠️ GAP:** Apenas tipos definidos, sem implementação de renderização.

Tipos: `FieldType` (8 tipos), `FormField`, `FormGroup`, `FormValidation`, `FormConfig`.

### 6.5 Keyboard Shortcuts (`hooks/useKeyboardShortcuts.ts` — 54 linhas)

Hook genérico: `useKeyboardShortcuts(shortcuts: KeyboardShortcut[])`. Não dispara quando foco está em input/textarea/select/contentEditable.

---

## 7. Catálogo de Rotas

| Path | Page | Descrição | Usa Layout? |
|------|------|-----------|-------------|
| `/` | `app/page.tsx` | Root — provável redirect para /dashboard | Sim |
| `/login` | `app/login/page.tsx` | Tela de login | Não (bypass) |
| `/register` | `app/register/page.tsx` | Tela de registro | Não (bypass) |
| `/dashboard` | `app/dashboard/page.tsx` | Painel principal com grid de pacientes | Sim |
| `/command-center` | `app/command-center/page.tsx` | Central de comando (visão tática) | FullScreenLayout |
| `/alert-triage` | `app/alert-triage/page.tsx` | Triagem e gestão de alertas | Sim |
| `/alert-routing` | `app/alert-routing/page.tsx` | Roteamento de alertas | Sim |
| `/clinical-forms` | `app/clinical-forms/page.tsx` | Formulários clínicos | Sim |
| `/handoff` | `app/handoff/page.tsx` | Passagem de plantão | Sim |
| `/patient/[id]` | `app/patient/[id]/page.tsx` | Detalhe do paciente | Sim |
| `/admin` | `app/admin/page.tsx` | Painel de administração | Sim |
| `/admin/users` | `app/admin/users/page.tsx` | Gestão de usuários | Sim |
| `/admin/thresholds` | `app/admin/thresholds/page.tsx` | Configuração de limiares | Sim |

### Navegação

**Sidebar público (todos os usuários):**
- Painel → `/dashboard`
- Central de Comando → `/command-center`
- Triagem de Alertas → `/alert-triage`

**Sidebar admin (apenas is_admin):**
- Administração → `/admin`
- Usuários → `/admin/users`
- Limiares → `/admin/thresholds`

**Rotas sem link na sidebar:** `/alert-routing`, `/clinical-forms`, `/handoff`, `/patient/[id]`

---

## 8. Matriz de Gaps (o que NÃO existe)

| # | Gap | Severidade | Fase planejada |
|---|-----|-----------|---------------|
| G1 | **Tokens domain-specific** (sepse, antimicrobiano, delirium, AKI, etc.) | 🔴 Critical | M1 (FASE 1) |
| G2 | **ClinicalTooltip sem stories** | 🟡 Medium | M1 (FASE 1) |
| G3 | **Sem FormRenderer** — form-engine tem tipos mas não renderiza | 🟡 Medium | M2 (FASE 2) |
| G4 | **Sem testes de componente** — 0 testes unitários React | 🟡 Medium | M3 (FASE 3) |
| G5 | **Sem tema claro/escuro em runtime** — tokens existem mas `:root` é fixo dark | 🟡 Medium | M1 (FASE 1) |
| G6 | **Sem componentes de gráfico reutilizáveis** — Recharts é usado diretamente nas pages | 🟡 Medium | M2 (FASE 2) |
| G7 | **Sem tabela de dados reutilizável** — TanStack Table sem wrapper | 🟡 Medium | M2 (FASE 2) |
| G8 | **Sem componente de Toast/notificação** — Radix Toast instalado mas sem wrapper | 🟢 Low | M2 (FASE 2) |
| G9 | **Sem ícones clínicos customizados** — 100% Lucide, sem ícones de domínio médico | 🟢 Low | M1 (FASE 1) |
| G10 | **Sem documentação de acessibilidade** — componentes têm aria attributes mas sem docs WCAG | 🟢 Low | M2 (FASE 2) |
| G11 | **Sem suporte a i18n** — textos hardcoded PT-BR | 🟢 Low | Backlog |
| G12 | **Sem loading skeletons** — estados de loading não padronizados | 🟢 Low | M2 (FASE 2) |

---

## 9. Recomendações para FASE 1 (Tokens + Componentes)

### 9.1 Tokens — Prioridades

1. **Criar tokens domain-specific** para os 14 domínios clínicos listados na seção 2.
   - Cada domínio precisa de: `-on-surface`, `-signal`, `-fill`, `-on-fill`, `-wash` (dark + light)
   - Baseline: ~70 novos tokens (5 variantes × 14 domínios)

2. **Implementar tema claro/escuro em runtime**
   - Adicionar toggle no Layout
   - Persistir preferência em localStorage
   - Atualizar `data-theme` dinamicamente

3. **Adicionar tokens de sombra/elevação para tema claro**
   - Tokens atuais são otimizados para dark theme (
shadow com rgba(0,0,0,...))
   - Tema claro precisa de sombras mais sutis

### 9.2 Componentes — Prioridades

1. **Criar stories para ClinicalTooltip** (G2)
   - Todos os 9 termos clínicos
   - Posições (top/right/bottom/left)
   - Termo desconhecido (fallback sem tooltip)

2. **Criar componentes de domínio clínico**:
   - `DomainBadge` — badge colorido por domínio (ex: "Sepse" com cor sepse)
   - `VitalSignCard` — card de sinal vital com threshold visual
   - `ScoreChart` — wrapper Recharts para MEWS/NEWS2 timeline
   - `PatientBedCard` — extrair de dashboard (hoje inline)

3. **Criar wrapper de Toast** usando Radix Toast:
   - `useToast()` hook
   - Variantes: success, error, warning, info
   - Posições configuráveis

4. **Criar biblioteca de ícones clínicos** (SVG customizados):
   - Ícones para cada domínio clínico
   - Ícones para equipamentos (ventilador, bomba de infusão, monitor)
   - Ícones para procedimentos (intubação, diálise, cateter)

### 9.3 Design System — Infraestrutura

1. **Criar página "Foundation" no Storybook**:
   - Colors / Tokens visualizados
   - Typography scale
   - Spacing scale
   - Elevation preview

2. **Documentar padrões de uso de tokens**:
   - Quando usar `-on-surface` vs `-signal` vs `-fill`
   - Guia de acessibilidade: contraste mínimo por variante

---

## Apêndice: Estrutura de Diretórios do Frontend

```
frontend-v2/
├── app/
│   ├── tokens-generated.css          # 185 linhas, 12 famílias de tokens
│   ├── layout.tsx                     # Root layout
│   ├── globals.css                    # Estilos globais
│   ├── page.tsx                       # /
│   ├── login/page.tsx                 # /login
│   ├── register/page.tsx              # /register
│   ├── dashboard/page.tsx             # /dashboard
│   ├── command-center/page.tsx        # /command-center
│   ├── alert-triage/page.tsx          # /alert-triage
│   ├── alert-routing/page.tsx         # /alert-routing
│   ├── clinical-forms/page.tsx        # /clinical-forms
│   ├── handoff/page.tsx               # /handoff
│   ├── patient/[id]/page.tsx          # /patient/:id
│   ├── admin/
│   │   ├── page.tsx                   # /admin
│   │   ├── users/page.tsx             # /admin/users
│   │   └── thresholds/page.tsx        # /admin/thresholds
├── components/
│   ├── AlertCard.tsx                  # 469 linhas
│   ├── AlertCard.stories.tsx          # 188 linhas, 11 stories
│   ├── SeverityBadge.tsx              # 283 linhas (+ TrendBadge, ScoreDisplay)
│   ├── SeverityBadge.stories.tsx      # 176 linhas, 16 stories
│   ├── ClinicalTooltip.tsx            # 71 linhas, ❌ sem stories
│   ├── Layout.tsx                     # 380 linhas (+ FullScreenLayout)
│   ├── Layout.stories.tsx             # 149 linhas, 6 stories
│   ├── DrawerBuilder.tsx              # 79 linhas
│   ├── DrawerBuilder.stories.tsx      # 154 linhas, 7 stories
│   ├── ErrorBoundary.tsx              # 92 linhas
│   └── ErrorBoundary.stories.tsx      # 80 linhas, 4 stories
├── lib/
│   ├── api.ts                         # 409 linhas, 16 funções API
│   ├── auth.ts                        # 90 linhas, auth helpers
│   ├── websocket.ts                   # 380 linhas, WS singleton + hooks
│   ├── clinical-severity.ts           # 104 linhas
│   ├── thresholds/
│   │   ├── types.ts                   # 15 linhas
│   │   └── useThreshold.ts            # 231 linhas
│   └── form-engine/
│       └── types.ts                   # 41 linhas
├── hooks/
│   ├── useKeyboardShortcuts.ts        # 54 linhas
│   └── usePatientWebSocket.ts         # 122 linhas
├── package.json                       # Next.js 15, React 19, Radix UI, etc.
├── tsconfig.json
└── tailwind.config.ts
```

---

> **Fim do RECON.** Pronto para handoff ao Product Designer.
> Próximo milestone: M1 — FASE 1 (criação de tokens domain-specific + componentes)
