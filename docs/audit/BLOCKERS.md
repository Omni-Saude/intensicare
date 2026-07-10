# BLOCKERS.md — IntensiCare Frontend v3
# Gerado: 2026-07-09 | Ive

## Bloqueios ativos

| ID | O que falta | Bloqueador | Plano | Owner |
|----|------------|------------|-------|-------|
| BLK-01 | WebSocket backend (handshake JWT) | Backend não implementa desafio/resposta JWT | Prompt enviado: docs/audit/handoff-parreira/WEBSOCKET_PROMPT.md | Parreira |
| BLK-02 | Dados reais nos pathways | Endpoints retornam 500/404 | Validar endpoints antes do deploy | Parreira |
| BLK-03 | M7 pathways sem dados | `GET /patients/{mpi_id}/pathways` sem dados reais | Frontend genérico pronto — backend precisa popular | Parreira |
| BLK-04 | Cleanup v2 → v3 | Aguardando G2 approval | Script definido no FRONTEND_REBUILD_PLAN.md §6.5 | Niemeyer |

## Bloqueios resolvidos

| ID | O que era | Como resolveu |
|----|-----------|---------------|
| BLK-DONE-01 | CSP bloqueava WebSocket | next.config.ts com CSP headers dev/prod |
| BLK-DONE-02 | API proxy não configurado | rewrites() em next.config.ts |
| BLK-DONE-03 | Recharts quebrado no Next.js 16 | Substituído por SVG sparkline nativo |
