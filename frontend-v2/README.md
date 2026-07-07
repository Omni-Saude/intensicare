# IntensiCare Frontend v2

Painel clínico para monitoramento de pacientes em UTI.

## Stack
- **Framework:** Next.js 15 (app router) + React 19
- **UI:** Radix UI + Tailwind CSS v4
- **Ícones:** Lucide React
- **Gráficos:** Recharts
- **Tabelas:** @tanstack/react-table
- **Formulários:** react-hook-form + zod
- **Design Tokens:** Style Dictionary 5.x
- **Componentes:** Storybook 8.x

## Scripts
- `npm run dev` — servidor de desenvolvimento
- `npm run build` — build de produção
- `npm run build-tokens` — gerar CSS/TS dos design tokens
- `npm run lint` — ESLint
- `npm run storybook` — Storybook em http://localhost:6006
- `npm run build-storybook` — build estático do Storybook

## Estrutura
- `app/` — rotas Next.js (app router)
- `components/` — componentes React reutilizáveis
- `lib/` — utilitários (clinical-severity, form-engine, thresholds, api, auth, websocket)
- `hooks/` — React hooks (usePatientWebSocket, useOverlayStack, useKeyboardShortcuts)
- `config/forms/` — configurações de formulários clínicos (JSON)

## Design Tokens
Os tokens de design são definidos em `../design-tokens/` e compilados via Style Dictionary.
O build gera CSS custom properties consumidas pelo Tailwind via `@theme`.

## Contribuição
1. Componentes novos: criar em `components/` com Storybook story
2. Cores: usar `var(--semantic-*)` e `var(--clinical-severity-*)` — NUNCA usar classes Tailwind de cor (`bg-red-500`, `text-green-*`)
3. Textos: sempre em português (PT-BR)
4. Acessibilidade: todos componentes devem ter `aria-*` attributes, focus visible, touch targets ≥ 44px

## Links
- Storybook: [link após deploy]
- Design tokens: `../design-tokens/`
- ADRs: `../docs/adr/`
