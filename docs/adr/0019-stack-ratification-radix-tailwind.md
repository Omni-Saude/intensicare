# 0019. Stack ratification: Radix UI + Tailwind CSS v4

Status: accepted
Date: 2026-07-07
Depends on: ADR 0001
Ratified by: Administrador / Tech Lead

## Context

ADR 0001 recommended **Option 1** (Next.js app router + Ant Design v5) as the frontend
foundation for the IntensiCare rebuild, based on the premise that the legacy's AntD v4
component vocabulary and clinical-form patterns were worth preserving via a v4→v5
migration rather than a full rewrite.

The team evaluated this recommendation against the actual implementation experience
and chose **Option 2** (Radix UI + Tailwind CSS v4) instead. This ADR formally records
that decision, the rationale for deviating from ADR 0001's recommendation, and the
complementary libraries selected to fill the component gaps left by AntD's absence.

## Decision

**Option 2 is ratified.** The `frontend-v2/` codebase is built on:

| Layer | Choice | Justification |
|---|---|---|
| Framework | Next.js 15 (app router) | Server components, streaming, modern React |
| Headless primitives | Radix UI (7 packages) | Unstyled, accessible, tree-shakeable |
| Styling engine | Tailwind CSS v4 | JIT-on-demand, `@theme` token mapping |
| Icons | Lucide React | Tree-shakeable, consistent style |
| Charts | Recharts | Composable, React-native |
| Tables | @tanstack/react-table | Headless, sorting/filtering/pagination |
| Forms | react-hook-form + zod | Performant, schema-validated |
| Design tokens | Style Dictionary 5.x | Platform-agnostic token pipeline |

## Why Option 2 over Option 1

1. **Token control:** CSS custom properties authored directly, not mediated through
   AntD's `theme.token` shape. The design system owns its tokens.
2. **Bundle size:** No 500 KB+ AntD library. Radix primitives are individually
   tree-shakeable (≈12 KB per primitive).
3. **Dark-first natively:** `data-theme` attribute toggle. No AntD `ConfigProvider`
   algorithm swap, no `dynamic-antd-theme` runtime recompilation.
4. **No library lock-in:** Radix provides unstyled accessible primitives. The visual
   language belongs entirely to IntensiCare.
5. **AntD v4→v5 is a rewrite anyway:** API changes, Less→CSS-in-JS, component prop
   breaks — the migration cost is comparable to a fresh build on Radix.

## Complementary Libraries

AntD v5 provides a large out-of-the-box component surface (Table, Form, Select with
search, DatePicker, etc.). To close the gaps left by choosing Radix instead, three
headless libraries were added:

| Library | Purpose | AntD equivalent |
|---|---|---|
| `@tanstack/react-table` ^8.21 | Clinical tables with sorting, filtering, pagination | AntD `Table` |
| `react-hook-form` ^7.81 + `zod` ^4.4 | Performant form state management + schema validation | AntD `Form` + `Form.Item` rules |
| `@radix-ui/react-select` (already installed) | Select with search, keyboard nav, typeahead | AntD `Select` |

These three libraries cover ~80% of what AntD provided for the clinical domain, with
a significantly smaller bundle and no CSS-in-JS overhead.

## Impact on Dependent ADRs

Detailed impact analysis is in `STACK_DECISION.md`. Summary:

| ADR | Status | Change |
|---|---|---|
| 0001 | **accepted** | Updated to reflect ratified Option 2 |
| 0002 (dark-first) | proposed | Core recommendation unchanged; mechanism: AntD Less → CSS custom properties |
| 0007 (neumorphic) | proposed | Core recommendation unchanged; mechanism: AntD shadow tokens → Tailwind shadow scale |
| 0010 (drawer) | proposed | Core recommendation unchanged; mechanism: AntD Drawer → `@radix-ui/react-dialog` |
| 0015 (form engine) | proposed | Core recommendation unchanged; field renderers: AntD → Radix primitives + Tailwind |

## Consequences

**Positive:**
- Full ownership of the design token pipeline and visual language
- Smaller bundle, faster initial load for bedside dashboards
- No migration path dependency on AntD's release cycle
- Each component dependency is individually replaceable

**Negative:**
- Fewer pre-built enterprise components — must build tables, advanced selects,
  date pickers from primitives
- No AntD ecosystem (ProLayout, ProTable) for admin screens
- Team must invest in component infrastructure that AntD would have provided

## References

- `STACK_DECISION.md` — full decision document with per-ADR impact analysis
- `docs/adr/0001-frontend-stack-and-ui-library.md` — updated to accepted
- `frontend-v2/package.json` — actual dependencies
- `design-tokens/config.js` — Style Dictionary build pipeline
