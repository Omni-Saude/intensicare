# GAP_CLOSURE_PLAN.md — IntensiCare Frontend v3
# Gerado: 2026-07-09 | Ive (Product Design Orchestrator)
# Objetivo: 38 gaps → DONE ou BLOCKED

## Gaps DS Governance (22 total — 1 CRITICAL, 18 MAJOR, 3 MINOR abertos)

| ID | Severity | Descrição | Local | Status |
|----|----------|-----------|-------|--------|
| DS-C1 | CRITICAL | `rgb()` hardcoded | app/admin/page.tsx:81 | ✅ DONE — substituído por shadow-sm |
| DS-M1 | MAJOR | 12 `text-[Npx]` arbitrários | vários | ⬜ OPEN |
| DS-M2 | MAJOR | 6 width/height fixos | vários | ⬜ OPEN |
| DS-M3 | MINOR | 18 borderWidth/borderStyle inline | vários | ⬜ OPEN |

## Gaps A11y (3 total)

| ID | Severity | Descrição | WCAG | Local | Status |
|----|----------|-----------|------|-------|--------|
| A11Y-1 | MEDIUM | Skip-link ausente | 2.4.1 | app/layout.tsx | ✅ DONE — `<a href="#main-content">` no layout + `id="main-content"` no main |
| A11Y-2 | MEDIUM | Overlay mobile sem teclado | 2.1.1 | app-shell.tsx:155 | ✅ DONE — role=button, tabIndex=0, aria-label, keyboard Enter/Esc/Space |
| A11Y-3 | MEDIUM | ~40% elementos sem focus-visible | 2.4.7 | vários | ✅ DONE — 19 focus-visible:ring adicionados em 10+ componentes |

## Gaps UX (32 total — 2 CRITICAL, 5 MAJOR, 16 MINOR, 10 NICE-TO-HAVE)

| ID | Severity | Descrição | Local | Status |
|----|----------|-----------|-------|--------|
| UX-C1 | CRITICAL | Logout sem confirmação | app-shell.tsx:143 | ✅ DONE — confirmação inline |
| UX-C2 | CRITICAL | Severity hardcoded 'normal' | pathway page:213 | ✅ DONE — data-driven |
| UX-M1 | MAJOR | Breadcrumb mostra slugs | app-shell.tsx | ⬜ OPEN |
| UX-M2 | MAJOR | Sem confirmação ao escalar alerta | quick-actions.tsx | ✅ DONE — QW3: não procede |
| UX-M3 | MAJOR | Sem atalhos de teclado | vários | ⬜ OPEN |
| UX-M4 | MAJOR | Sem tooltips clínicos | vários | ⬜ OPEN |
| UX-M5 | MAJOR | Estilos inconsistentes entre páginas | vários | ⬜ OPEN |

## Gaps Stories (39 total)

| ID | Descrição | Status |
|----|-----------|--------|
| ST-001..039 | 39 componentes sem stories | ⬜ OPEN |

## Progresso

| Estado | Count |
|--------|-------|
| ✅ DONE | 4 |
| ⬜ OPEN | 34 |
| 🔒 BLOCKED | 0 |
| **Total** | **38** |

## Próxima ação: FASE 2 — Stories (batch 1 de 3 agentes)
