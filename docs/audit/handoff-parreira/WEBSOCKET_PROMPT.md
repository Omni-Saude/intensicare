# PROMPT.md — WebSocket Layer para IntensiCare Frontend v3
# Destinatário: Parreira (Backend/DevOps)
# Gerado por: Ive (Product Design Orchestrator) via deep analysis ADR-0034
# Data: 2026-07-09
# Spec canônica: docs/adr/ADR-0034-realtime-websocket-strategy.md

---

## Contexto

O frontend v3 foi reconstruído do zero (42 componentes, 6 páginas core). A arquitetura segue ADR-0030 (pathway-centric), ADR-0032 (build from zero), e ADR-0033 (componentes genéricos data-driven). O **ADR-0034** define a estratégia de tempo real — WebSocket com fallback para polling — e é o ÚNICO ADR ainda não implementado.

Atualmente o frontend usa SWR com `refreshInterval` para polling no Alert Triage (30s), mas não tem o hook `useRealtimeChannel` com switch automático WS/polling que o ADR-0034 especifica.

**Setup atual:**
- Projeto: `/Users/familia/intensicare/frontend-v3/`
- Stack: Next.js 16 + React 19 + Tailwind CSS 4 + SWR
- API client: `lib/api.ts` (402 linhas, 20 tipos, 14 funções, JWT in-memory)
- Auth: `lib/auth.tsx` (AuthProvider, useAuth, JWT decode)
- Middleware: `middleware.ts` (JWT cookie check)
- Build: `npm run build -- --webpack` (8 rotas, zero erros)

---

## Arquitetura (ADR-0034)

```
┌──────────────────────────────────────────────────┐
│                 useRealtimeChannel                │
│                                                   │
│  ┌──────────────┐     ┌──────────────────────┐   │
│  │ WebSocket    │────▶│ Connected?            │   │
│  │ (primário)   │     │ ✅ → usa WS           │   │
│  └──────────────┘     │ ❌ → fallback polling │   │
│                       └──────────────────────┘   │
│  ┌──────────────┐                                │
│  │ Polling      │  intervalo configurável        │
│  │ (fallback)   │  Dashboard: 30s                │
│  └──────────────┘  Patient/Pathway: 60s          │
└──────────────────────────────────────────────────┘
```

### Canais (6 canais, 3 páginas)

| Canal | Escopo | Página | Ação no frontend |
|-------|--------|--------|-----------------|
| `bed_grid.updated` | Global | Dashboard (`/`) | Revalidar `fetchDashboard()` |
| `alert.raised` | Global | Dashboard, Patient | Revalidar `fetchAlerts()` |
| `alert.updated` | Global | Dashboard, Patient, Alerts | Revalidar `fetchAlerts()` |
| `vitals.updated` | `mpi_id` | Patient Detail (`/patient/[id]`) | Revalidar `fetchPatientDetail(mpiId)` |
| `pathway.updated` | `mpi_id` | Patient Detail | Revalidar `fetchPatientPathways(mpiId)` |
| `pathway.state_changed` | `mpi_id` + `pp_id` | Pathway View (`/patient/[id]/pathway/[pp]`) | Revalidar `fetchPathwayProgress(mpiId, ppId)` |

### Intervalos de Fallback (polling)

| Página | Intervalo | Justificativa |
|--------|-----------|---------------|
| Dashboard | 30s | Visão geral, 20+ pacientes, dados agregados |
| Patient Detail | 60s | 1 paciente, menos crítico que alertas em tempo real |
| Pathway View | 60s | Dados de trilha (estado, critérios, recomendações) |
| Alert Triage | 30s | Alertas precisam de baixa latência |

---

## Contrato TypeScript

### `lib/websocket.ts`

```typescript
// ── Tipos ──

type RealtimeChannel =
  | 'bed_grid.updated'
  | 'alert.raised'
  | 'alert.updated'
  | 'vitals.updated'
  | 'pathway.updated'
  | 'pathway.state_changed';

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected' | 'fallback';

interface WSMessage {
  type: 'auth_required' | 'auth' | 'subscribed' | 'event';
  channel?: RealtimeChannel;
  challenge?: string;
  token?: string;
  payload?: Record<string, unknown>;
}

// ── Hook principal ──

/**
 * Inscreve em um canal de tempo real. Retorna o status da conexão.
 * 
 * - Se WebSocket conecta → mensagens disparam `onMessage`.
 * - Se WebSocket falha (CSP, firewall, timeout 5s) → ativa polling
 *   automático no `fallbackInterval` (ms).
 * - `filter` opcional: filtra mensagens no cliente (ex: só vitals
 *   do mpi_id atual).
 * - `onMessage` é chamado em ambos os modos (WS e polling).
 */
function useRealtimeChannel(
  channel: RealtimeChannel,
  onMessage: (payload: unknown) => void,
  options?: {
    fallbackInterval?: number;     // ms, default: 30_000
    filter?: (payload: unknown) => boolean;
    enabled?: boolean;              // default: true
  }
): { status: ConnectionStatus; lastEvent: Date | null };

/**
 * Hook utilitário: retorna status global da conexão + indicador visual.
 * Usado no AppShell para mostrar WiFi/WifiOff no header.
 */
function useConnectionStatus(): {
  status: ConnectionStatus;
  since: Date | null;              // quando entrou neste status
  reconnect: () => void;           // força reconexão WS
};
```

### Integração com o Auth

```typescript
// lib/websocket.ts — handshake JWT

// 1. Cliente conecta:
const ws = new WebSocket('wss://intensicare.api/ws');
//    Em dev: ws://localhost:8000/ws

// 2. Servidor envia desafio:
// { type: "auth_required", challenge: "<nonce>" }

// 3. Cliente responde:
const token = getToken(); // de lib/api.ts — JWT in-memory
ws.send(JSON.stringify({ type: "auth", token, challenge: nonce }));

// 4. Servidor valida JWT → inscreve canais
// { type: "subscribed", channel: "bed_grid.updated" }

// 5. Mensagens de evento:
// { type: "event", channel: "vitals.updated", payload: { mpi_id: "..." } }
```

---

## CSP (Content-Security-Policy)

### Desenvolvimento (`next.config.ts`)

```typescript
// next.config.ts
const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "connect-src 'self' ws://localhost:8000 wss://localhost:8000",
          },
        ],
      },
    ];
  },
};
```

### Produção (infra — Nginx/CDN)

```nginx
add_header Content-Security-Policy "connect-src 'self' wss://intensicare.api";
```

---

## Integração com Páginas Existentes

### M1 — Dashboard (`app/page.tsx`)

Atualmente usa SWR puro. Deve ser estendido para:

```typescript
// app/page.tsx (trecho novo)
import { useRealtimeChannel } from '@/lib/websocket';

export default function DashboardPage() {
  const { data, error, isLoading, mutate } = useSWR(
    ['dashboard', unit],
    () => fetchDashboard(unit ?? undefined),
  );

  // WebSocket + fallback: revalidar dashboard quando bed_grid ou alertas mudam
  useRealtimeChannel('bed_grid.updated', () => mutate(), {
    fallbackInterval: 30_000,
  });
  useRealtimeChannel('alert.raised', () => mutate(), {
    fallbackInterval: 30_000,
  });

  // ... resto igual
}
```

### M2 — Patient Detail (`app/patient/[mpi_id]/page.tsx`)

```typescript
// Revalidar vitals e pathways quando mudam
useRealtimeChannel('vitals.updated', (payload) => {
  if (payload?.mpi_id === mpiId) mutateDetail();
}, { fallbackInterval: 60_000, filter: (p) => p?.mpi_id === mpiId });

useRealtimeChannel('pathway.updated', (payload) => {
  if (payload?.mpi_id === mpiId) mutatePathways();
}, { fallbackInterval: 60_000, filter: (p) => p?.mpi_id === mpiId });
```

### M3 — Pathway View (`app/patient/[mpi_id]/pathway/[pp_id]/page.tsx`)

```typescript
// Revalidar progresso da trilha quando estado muda
useRealtimeChannel('pathway.state_changed', (payload) => {
  if (payload?.mpi_id === mpiId && payload?.pp_id === ppId) mutateProgress();
}, { fallbackInterval: 60_000, filter: (p) => p?.mpi_id === mpiId && p?.pp_id === ppId });
```

### AppShell — Indicador de Conexão

```typescript
// components/app-shell.tsx — adicionar no header
import { useConnectionStatus } from '@/lib/websocket';
import { Wifi, WifiOff } from 'lucide-react';

// No top bar:
const { status } = useConnectionStatus();
{status === 'connected' && <Wifi className="h-4 w-4 text-[var(--severity-normal)]" />}
{status === 'disconnected' && <WifiOff className="h-4 w-4 text-[var(--severity-critical)]" />}
{status === 'fallback' && <WifiOff className="h-4 w-4 text-[var(--severity-watch)]" />}
```

---

## Referência: Implementação no v2

O frontend v2 (QUE NÃO DEVE SER COPIADO, apenas consultado para entender o padrão) tem:

- `lib/websocket.ts` — hooks `useRealtimeChannel` e `useConnectionStatus`
- Single WebSocket connection com multiplexação de canais
- Fallback automático para polling

O v3 deve implementar o mesmo padrão, mas escrito do zero, integrado com o novo API client (`getToken()` de `lib/api.ts`) e com os novos canais de trilha.

---

## Verificação

```bash
cd /Users/familia/intensicare/frontend-v3

# 1. O arquivo existe e compila
npx tsc --noEmit lib/websocket.ts

# 2. Build completo com WebSocket integrado
npm run build -- --webpack

# 3. Teste manual (dev)
# Abrir Dashboard em 2 janelas → alterar dado em uma → verificar se a outra atualiza
```

---

## Critérios de Done

- [ ] `lib/websocket.ts` criado com `useRealtimeChannel` e `useConnectionStatus`
- [ ] 6 canais definidos como TypeScript union type
- [ ] Switch automático WS → polling (timeout 5s)
- [ ] Fallback polling com intervalos: Dashboard 30s, Patient/Pathway 60s
- [ ] Handshake JWT (desafio/resposta) implementado no cliente
- [ ] Integrado com `getToken()` de `lib/api.ts`
- [ ] `useConnectionStatus` retorna WiFi/WifiOff para AppShell
- [ ] CSP headers configurados em `next.config.ts` para dev
- [ ] `npm run build -- --webpack` passa sem erros
- [ ] Nenhum código copiado do v2 (consultar padrão é OK, copiar NÃO)

---

## Contato

- **Arquitetura:** Niemeyer
- **Frontend:** Ive (Product Design Orchestrator)
- **Dúvidas clínicas:** Rodrigo Aquino

## Referências

- `docs/adr/ADR-0034-realtime-websocket-strategy.md` — spec canônica
- `docs/contracts/pathways-openapi.yaml` — schemas de API
- `docs/audit/handoff-product-designer/DESIGN_BRIEF.yaml` — contratos de componente
- `docs/audit/handoff-product-designer/FRONTEND_REBUILD_PLAN.md` — blueprint completo
- Frontend v3: `/Users/familia/intensicare/frontend-v3/`
