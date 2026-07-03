# 0013. Clinical severity color system (statusTrilha) versus declared tokens and ad-hoc literals

Status: proposed
Date: 2026-07-03
Audit source: trilhas-frontend @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

## Context and Problem Statement

The legacy platform declares a formal semantic color token set (`@success-color`, `@warning-color`, `@danger-color`, `@info-color`, `@default-color`) in `variables.less`, but none of these is ever referenced by name anywhere in the codebase except the declaration itself (inventory §2.1, §2.2). Separately, the platform declares a tenant-overridable brand color, `--primary-color`, set per company (`empresa.cor_primaria`) and consumed at ≥60 call sites (`trilhas-frontend:src/hooks/useChangeColorTheme.ts:1-19`; `trilhas-frontend:src/components/PageContainer/PageContainer.tsx:112-133`). Neither of these is what actually communicates patient risk on screen. The question this ADR resolves: what should the new platform's clinical severity color system be, given what the legacy system actually did and where it broke down?

## The Legacy Decision

The product's true clinical severity palette is `statusTrilha.ts`: an object literal typed `as any`, with five named states — `NEUTRO`, `VERMELHO`, `AMARELO`, `LARANJA`, and `ASSISTIDO` — each carrying 6 pre-computed shades (`color`, `background`, `backgroundLight`, `ballColor`, `ballBackground`, `backgroundShade`), e.g. `VERMELHO.ballColor = "#FF1633"`, `AMARELO.ballColor = "#ffd900"` (`trilhas-frontend:src/utils/statusTrilha.ts:1-45`). `NEUTRO/VERMELHO/AMARELO/LARANJA` map to an alert severity returned by the API (`ocupacao.alerta`, `trilha.alerta`, `mensagem.alerta`, `criterio.alerta`); `ASSISTIDO` always overrides the raw alert when a bed is manually acknowledged (`assistido === true`). The object is imported directly — not through any theme provider — by 7 components (`InfoPacienteHeader`, `CollapseCard`, `DashboardCard`, `MessageBallon`, `FeedBallon`, `TabRecomendacoes`, `ItemNotificacao`) and consumed via inline `style={{ backgroundColor: statusTrilha[...] }}` rather than CSS classes (inventory §2.2).

This palette is entirely decoupled from `--primary-color`: rebranding a tenant has zero effect on severity colors (inventory §2.2).

The same green/amber/red concept is independently reinvented, with divergent hex literals, in at least six other locations:
- `handleIconByStatus.ts:1-23` (evolução record status: green `#258a10`, red `#ff1633`, plus an unrelated blue `#1890ff` for "liberado")
- `HorarioCheck.tsx:60-138`, two separate code paths in the same file (`colorCheck`: green `#389e0c`, amber `#d4b105`; popover wrapper: green `#acff76`, red `#ff5252`)
- `ItemProtocoloSepse.tsx:42-50` (sepsis first-hour delay flag: red `#e84748`)
- `DashboardCard.tsx:291-392` (occupancy gauge: green `#00DC50`, red `#FF1633`, amber `#FFAB00`)
- `DisplayNotificaoes.tsx:73-96` (notification toast icon: amber `#FFAB00`, hardcoded regardless of the notification's actual severity)

Two of these are live bugs, not just duplication:
- **Severity-blind toast:** `showNotification` builds the `notification.open()` icon as `<MaterialIcon path={mdiBellOutline} color="#FFAB00" />` unconditionally — a VERMELHO and an AMARELO bed alert produce an identical amber toast (`trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:73-96`).
- **Hardcoded-red criteria panel:** immediately below `TabRecomendacoes`'s tab-selector buttons, which correctly color by each trilha's own `alerta`, the criteria `Collapse.Panel` background is set to `backgroundColor: isLight ? statusTrilha["VERMELHO"].backgroundLight : statusTrilha["VERMELHO"].background` — a literal `"VERMELHO"` key, not the criterion's actual alert — so every panel renders red-tinted at every severity (`trilhas-frontend:src/components/TabRecomendacoes/TabRecomendacoes.tsx:213-231`).

## Evident Rationale

*(Inferred — not stated anywhere in code or comments.)* AntD's declared semantic tokens (`@success/@warning/@danger`) provide one color each, with no equivalent of the border/fill/light-fill/ball shade set that per-cell, per-card dynamic clinical coloring needs across both dark and light themes; `statusTrilha`'s 6-shade-per-state shape looks purpose-built to cover exactly that surface without per-consumer contrast math (inventory §2.2). Keeping severity colors immune from `--primary-color` white-labeling is also plausibly deliberate: a hospital group should not be able to reskin what "red" means for patient safety just by picking a brand color (inventory §2.2, §8).

## Assessment

**Strengths:**
- The two-tier separation — an immutable clinical-severity scale versus a tenant-overridable brand scale — is architecturally sound and should be preserved as an explicit, documented rule, not an accident of two unrelated mechanisms happening not to collide (inventory §2.2, §8).
- Pre-computing shades per state (border/fill/light-fill/dot) removed the temptation for each consumer to invent its own tint/shade math — where it was actually used, it worked.

**Weaknesses:**
- `statusTrilha` is untyped (`as any`), lives outside the declared token file, and is consumed via inline styles rather than a themeable API — nothing prevents a new consumer from reinventing it again, which is exactly what happened at least six times (`handleIconByStatus.ts:1-23`; `HorarioCheck.tsx:60-138`; `ItemProtocoloSepse.tsx:42-50`; `DashboardCard.tsx:291-392`; `DisplayNotificaoes.tsx:73-96`).
- The occupancy gauge's near-miss amber (`#FFAB00` vs. `statusTrilha.AMARELO`'s `#ffd900`) is the textbook failure mode of literal-only color: two supposedly-identical concepts silently drift apart with no compiler or lint signal (`DashboardCard.tsx:291-392`).
- The toast bug and the hardcoded-panel bug are not stylistic quirks — they are correctness failures in a patient-safety signal. A red alert can be visually indistinguishable from a yellow one in the one surface (the toast) most likely to be glanced at in passing, and a criteria panel can permanently mislabel severity via background color regardless of the badge/tab next to it.
- The declared AntD semantic tokens (`@success/@warning/@danger/@info/@default` in `variables.less`) are dead weight: zero call sites reference them by name (inventory §2.1), so the codebase effectively maintains two parallel "severity" vocabularies — one dead, one alive but unenforced.

## Considered Options

1. **Port `statusTrilha` as-is** (same shape, same values, still `as any`, still imported ad hoc). Fastest, but reproduces the exact governance gap that produced six divergent reinventions and two live bugs.
2. **Promote `statusTrilha` to a first-class, typed severity token scale** — a single exported, strongly-typed object (or design-token JSON) enumerating the clinical states and their shades, consumed exclusively through a shared hook/component API (e.g. a `<SeverityBadge severity="VERMELHO" variant="ball" />` primitive or CSS custom properties scoped under a `clinical.*` namespace), with lint/CI enforcement (no raw hex literals for red/amber/green outside the token file) and a documented, hard boundary from the tenant `brand.*` namespace.
3. **Fold severity into a general-purpose semantic-color system** shared with non-clinical states (success/warning/error toasts, form validation, etc.), reusing the same token names for both. Simpler token surface, but risks re-coupling patient-safety color to generic UI feedback color, which is one thing the legacy system — despite its flaws — kept correctly separate.
4. **Contrast-check and re-derive the palette from scratch** using a formal color scale (e.g. an OKLCH/HSL-generated ramp) rather than the legacy's five hand-picked hex sets, verifying WCAG contrast for text-on-background and dark/light parity as part of token authoring.

## Decision Outcome

Recommended (pending team ratification): **Option 2, informed by Option 4** — promote `statusTrilha`'s five-state model to a first-class, typed, contrast-checked severity token scale (`clinical.neutro/vermelho/amarelo/laranja/assistido`, each with the same border/fill/light-fill/dot shade roles the legacy set proved useful), published as the only sanctioned way to render severity anywhere in the product. It must be:
- **Typed** (no `as any`), exported from a single module, and consumed through a shared primitive/hook rather than ad hoc inline styles, so every new "is this bed red or yellow" surface is forced through one code path.
- **Kept structurally separate from `brand.*`/tenant color** (Option 2's namespace split), preserving the one part of the legacy design that was actually correct — clinical color must not be white-label-able.
- **Re-derived and contrast-checked** (Option 4) rather than copy-pasted verbatim, since the legacy values were never verified for contrast and already show one accidental near-miss (occupancy gauge amber).
- **Enforced**, not just documented: add a lint rule or code-review checklist item flagging raw red/amber/green hex literals outside the token module, so the six-way duplication found in this audit cannot recur silently.

The rebuild must also fix, not port, the two live severity bugs identified in the audit: the notification toast must derive its icon color from the underlying alert's severity rather than a hardcoded amber, and the recommendations/criteria panel must use each criterion's actual `alerta`, not a literal `"VERMELHO"` key. This is the highest-priority clinical-design decision in the inventory (Critical — patient safety, inventory Summary #2) and should be implemented before any other visual-system work that depends on it (thresholded vitals/labs flagging, ADR 0014, will consume the same token scale).

### Consequences

**Good:**
- A single, typed, enforced severity scale eliminates the class of bug where "red" silently drifts across six call sites, and makes future consumers (vitals thresholding, lab flagging, SOFA banding) reuse rather than reinvent the palette.
- Explicitly documenting the clinical/brand namespace split protects a white-label business requirement (per-tenant branding) from ever being able to compromise a patient-safety signal, closing a boundary that was previously accidental.
- Fixing the toast and criteria-panel bugs removes two concrete, currently-shipping misrepresentations of patient severity.

**Bad:**
- Re-deriving and contrast-checking the palette (rather than copying values) is extra up-front design work and requires clinical/design sign-off on any value that changes from the legacy hex, since staff have muscle memory for "red bed = crisis."
- Enforcing a single consumption path (shared primitive/lint rule) requires tooling investment (custom lint rule or code-review discipline) that the legacy project never had, and will need to be maintained as the component library grows.
- Because `ASSISTIDO` always overrides raw alert severity, the new token API must explicitly model that override semantics (not just five independent colors) or the same "which state wins" ambiguity could resurface in a new form.
