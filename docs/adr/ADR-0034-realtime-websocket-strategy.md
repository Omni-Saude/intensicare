# ADR-0034: Estratégia de Atualização em Tempo Real — WebSocket com Degradação Graciosa

**Status:** proposed  
**Data:** 2026-07-09  
**Decisão por:** Niemeyer (System Architect)  

---

## Contexto

O Dashboard e o Patient Detail do frontend v2 já implementam WebSocket para atualização em tempo real (canais: `bed_grid.updated`, `vitals.updated`, `alert.raised`, `alert.updated`). O código existe em `lib/websocket.ts` e os hooks `useRealtimeChannel` e `useConnectionStatus` são usados pelas páginas.

No entanto, o handoff do Parreira identificou problemas:
1. **CSP bloqueia WebSocket** — o header Content-Security-Policy não permite `ws://localhost:8000`
2. **JWT não é enviado no handshake** — o WebSocket conecta sem autenticação
3. **O v3 adiciona novos canais** — `pathway.updated`, `pathway.state_changed` para o Pathway View

Precisamos de uma estratégia que:
1. Funcione em produção (HTTPS/WSS)
2. Degrade graciosamente quando WebSocket falha (fallback para polling)
3. Suporte os novos canais de trilha
4. Não bloqueie o build por CSP

## Decisão

**Manter WebSocket como mecanismo primário de atualização em tempo real, com fallback automático para polling (intervalo: 30s para Dashboard, 60s para Patient/Pathway View). Corrigir CSP para `wss://` em produção e `ws://localhost:8000` em desenvolvimento.**

### Arquitetura de Realtime

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

### Canais no v3

| Canal | Escopo | Ação |
|-------|--------|------|
| `bed_grid.updated` | Dashboard | Atualizar grid de leitos |
| `alert.raised` | Dashboard, Patient | Recarregar alertas |
| `alert.updated` | Dashboard, Patient | Recarregar alertas |
| `vitals.updated` | Patient Detail | Recarregar vitals (se mpi_id match) |
| **`pathway.updated`** | Patient Detail | Recarregar trilhas ativas |
| **`pathway.state_changed`** | Pathway View | Recarregar progresso da trilha |

### Correção de CSP

```nginx
# Desenvolvimento (next.config.js)
Content-Security-Policy: "connect-src 'self' ws://localhost:8000 wss://localhost:8000"

# Produção (infra)
Content-Security-Policy: "connect-src 'self' wss://intensicare.api"
```

### Estratégia de Autenticação no WebSocket

```
1. Cliente conecta: new WebSocket("wss://intensicare.api/ws")
2. Servidor envia desafio: { type: "auth_required", challenge: "<nonce>" }
3. Cliente responde: { type: "auth", token: "<jwt>", challenge: "<nonce>" }
4. Servidor valida JWT → inscreve nos canais autorizados
5. Conexão estabelecida — troca de mensagens
```

Até que o backend implemente o handshake JWT no WebSocket, o fallback para polling será o mecanismo padrão em produção.

## Alternativas Consideradas

### Alternativa A: Server-Sent Events (SSE)
- **Prós:** Unidirecional (servidor→cliente), mais simples que WebSocket, HTTPS nativo
- **Contras:** Não suporta reconexão tão bem quanto WebSocket, menos suporte em bibliotecas React, não permite cliente→servidor (ex: subscribe/unsubscribe dinâmico)
- **Rejeitada porque:** WebSocket já está implementado e funcional (com correções). Migrar para SSE seria retrabalho sem ganho proporcional.

### Alternativa B: Polling puro (sem WebSocket)
- **Prós:** Zero complexidade de infra, funciona em qualquer ambiente
- **Contras:** Latência de até 30s para alertas críticos (inaceitável em UTI), carga no servidor
- **Rejeitada porque:** UTI requer latência < 5s para alertas críticos. Polling de 5s em 20+ pacientes simultâneos sobrecarregaria o backend.

### Alternativa C: WebSocket + sem fallback
- **Prós:** Código mais simples
- **Contras:** Se WebSocket falhar (CSP, firewall, proxy), a interface congela — sem atualização nenhuma
- **Rejeitada porque:** Ambiente hospitalar tem firewalls restritivas. Fallback é obrigatório para confiabilidade clínica.

## Consequências

### Positivas
- Atualização em tempo real para alertas críticos (latência < 5s)
- Resiliência: se WebSocket falhar, polling mantém a interface viva
- Canais de trilha permitem que o Pathway View reaja a mudanças de estado em tempo real
- `useConnectionStatus` já mostra indicador visual (WiFi/WifiOff) — mantido no v3

### Negativas
- Complexidade de dois mecanismos (WS + polling)
- Correção de CSP requer coordenação com infra/Parreira
- Handshake JWT no WebSocket requer mudança no backend (postergável: fallback cobre)

### Riscos e Mitigações
- **Risco:** CSP correto mas WebSocket ainda bloqueado por firewall hospitalar → **Mitigação:** Fallback automático para polling. Interface nunca congela.
- **Risco:** Polling de 30s perde alerta crítico por 29 segundos → **Mitigação:** Dashboard usa 30s (visão geral). Patient Detail usa 60s (menos pacientes, menos crítico). Se necessário, reduzir para 15s/30s.
- **Risco:** Múltiplos canais de WebSocket consomem memória no cliente → **Mitigação:** Um único WebSocket connection com multiplexação de canais (já implementado em `lib/websocket.ts`).

---

## Referências

- Frontend v2: `lib/websocket.ts` (hooks `useRealtimeChannel`, `useConnectionStatus`)
- FRONTEND_REBUILD_HANDOFF.md (Parreira) § 6 (Riscos — WebSocket CSP)
- FRONTEND_REBUILD_PLAN.md § 5.2 (FASE 1 — Dashboard com WebSocket)
