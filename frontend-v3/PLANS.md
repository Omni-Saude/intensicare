# PLANS.md — Frontend v3 Rebuild

## Feature Goal
Construir o novo frontend do IntensiCare **100% do zero**, orientado à jornada do intensivista: Dashboard → Patient Detail → Pathway View. 6 páginas core, sem nenhum código do v2.

## Source of Truth
1. `docs/contracts/pathways-openapi.yaml` — schemas, endpoints, tipos
2. `_work/alerts/pathways/sepse.yaml` — trilha benchmark
3. `FRONTEND_REBUILD_PLAN.md` § 1 — jornada do intensivista

## Milestones (9 fases, ~28 dias)

| Milestone | Dias | Dependências | Status |
|-----------|------|-------------|--------|
| M0 — Foundation | 2 | — | in_progress |
| M1 — Dashboard | 3 | M0 | pending |
| M2 — Patient Detail | 3 | M0 | pending |
| M3 — Pathway Sepse | 4 | M2 | pending |
| M4 — Alert Triage | 3 | M0 | pending |
| M5 — Pathway Catalog | 2 | M0 | pending |
| M6 — Admin | 2 | M0 | pending |
| M7 — 8 Trilhas | 6 | M3 | pending |
| M8 — Integração | 3 | all | pending |

## M0 — Foundation (em execução)

### Entregáveis
1. Projeto Next.js 15 criado com `npx create-next-app@latest`
2. Dependências: @radix-ui/react-slot, class-variance-authority, clsx, tailwind-merge, lucide-react, recharts, react-syntax-highlighter, swr
3. shadcn/ui inicializado
4. globals.css com sistema de severidade (4 níveis: normal/watch/urgent/critical)
5. lib/api.ts com tipos derivados do pathways-openapi.yaml
6. lib/auth.ts com JWT in-memory
7. middleware.ts com proteção de rotas
8. AppShell com sidebar + breadcrumb + TenantProvider
9. Estrutura de diretórios: app/{patient,alerts,pathways,admin,auth}

### Verificação
```bash
npm run build  # zero erros
npm run lint   # zero warnings
npx tsc --noEmit  # tipos OK
```

## Rollback
Se M0 falhar: remover diretório frontend-v3/, recriar do zero.
