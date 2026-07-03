# D-03: Clinically Relevant UX Pattern Inventory — trilhas-frontend

**Repo:** trilhas-frontend @ `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` (read-only mirror)
**Method:** every claim below is derived from reading the actual `.tsx`/`.less`/`.ts` source (component props, style rules, theme variables) — not from file/variable names alone. All citations use the form `trilhas-frontend:path:line-range @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

Stack context relevant to every finding below: Next.js + Ant Design (antd 4, LESS-themed via `dynamic-antd-theme`), no design-token build system beyond a single `variables.less` and a hand-written JS "severity palette" (`statusTrilha.ts`). Theming is **multi-tenant**: each company (`empresa`) has a `cor_primaria` hex that is pushed into a runtime CSS custom property at login.

---

## 1. Design tokens actually in use

### 1.1 Compile-time LESS tokens (`src/styles/variables.less`)
trilhas-frontend:src/styles/variables.less:1-15 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

| Token | Value | Observed usage |
|---|---|---|
| `@primary-color` | `#fe6d01` (orange) | Compiled into antd component CSS; also the hard-coded fallback pushed at app mount (see 1.3) |
| `@secondary-color` | `#606060` | e.g. unread-message badge background, `DashboardCard.less:62` |
| `@background-color` | `#333` | not observed wired to any component read |
| `@success-color` | `#258a10` | not referenced by class name anywhere found (`grep` shows no `@success-color` usage outside this file) |
| `@info-color` | `#1a3bb7` | not referenced elsewhere |
| `@default-color` | `#bbbbbb` | not referenced elsewhere |
| `@danger-color` / `@error-color` | `#ff1633` | not referenced by name elsewhere, but the *literal* `#ff1633`/`#FF1633` recurs hard-coded in several places (see §4, §2) |
| `@warning-color` | `#d6a400` | not referenced by name in any `.less`; the runtime CSS var `var(--warning-color)` that a component expects (§6.4) is **never defined**, LESS or runtime |
| `@skeleton-text` | `#eee3` | not observed wired to any component |

**Finding:** most of the semantic tokens declared in `variables.less` (`@success-color`, `@info-color`, `@default-color`, `@warning-color`) are declared but effectively dead — components either hard-code their own literal hex values or reference a same-named CSS custom property that was never set. Only `@primary-color`/`--primary-color` is a live, working token.

### 1.2 The real severity palette: `statusTrilha.ts`
trilhas-frontend:src/utils/statusTrilha.ts:1-45 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

This is the actual clinical-severity color system used app-wide (not `variables.less`). Five named severity states, each with 6 derived shades:

| Key | `color` | `background` (dark) | `backgroundLight` | `ballColor` | `ballBackground` | `backgroundShade` |
|---|---|---|---|---|---|---|
| `NEUTRO` | `#5BCE85` | `#16302A` | `#E1FCE0` | `#00DC50` | `#08712E` | `#08712E1A` |
| `VERMELHO` | `#C54C5C` | `#412125` | `#FCE4DD` | `#FF1633` | `#740614` | `#7406141A` |
| `AMARELO` | `#cebc5a` | `#443f23` | `#fffadb` | `#ffd900` | `#726208` | `#7262081A` |
| `LARANJA` | `#F9A65A` | `#4A2B1F` | `#FFEDDD` | `#ff5900` | `#712B08` | `#7137081A` |
| `ASSISTIDO` | `#4FBFE1` | `#04314A` | `#DCFDFB` | `#00B0FF` | `#0060A0` | `#0060A01A` |

`NEUTRO`/`VERMELHO`/`AMARELO`/`LARANJA` map to a **clinical alert/trilha (care-pathway) severity** returned by the API (`ocupacao.alerta`, `trilha.alerta`, `mensagem.alerta`, `criterio.alerta`), and `ASSISTIDO` is a manually-acknowledged/"being handled" state that always overrides the raw alert color when `assistido === true`. This object is imported directly (not through a theme provider) by 7 components: `InfoPacienteHeader`, `CollapseCard`, `DashboardCard`, `MessageBallon`, `FeedBallon`, `TabRecomendacoes`, `ItemNotificacao` (trilhas-frontend:src/components/InfoPacienteHeader/InfoPacienteHeader.tsx:8, src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:29, src/components/ListDashboard/DashboardCard/DashboardCard.tsx:16, src/components/MessageBallon/MessageBallon.tsx:24, src/components/DisplayNotificaoes/ItemNotificacao/ItemNotificacao.tsx:8, src/components/TabRecomendacoes/TabRecomendacoes.tsx:14 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).

**Important architectural fact:** these colors are static JS literals, entirely independent of the runtime `--primary-color` white-label mechanism (§1.3). Rebranding a tenant's primary/accent color has **zero effect** on clinical severity colors — which is arguably correct (patient safety colors probably shouldn't be brand-customizable) but is not a documented/intentional separation anywhere in code; it is simply two unrelated coloring mechanisms that happen not to collide.

### 1.3 Runtime, per-tenant theming (`--primary-color`)
trilhas-frontend:src/hooks/useChangeColorTheme.ts:1-19 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

```
changeColorTheme: async (color) => {
  await changeAntdTheme(color);                              // recompiles antd's LESS vars in-browser
  document.documentElement.style.setProperty("--primary-color", color);
  document.documentElement.style.setProperty("--primary-shadow-color", `${color}2e`);
}
```

- On every app mount, if the user is in light mode, primary color is force-reset to the default orange `#fe6d01` (trilhas-frontend:src/pages/_app.tsx:36-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
- On loading a company (`PageContainer`), `changeColorTheme(`#${data.cor_primaria}`)` is called with the tenant's stored hex (trilhas-frontend:src/components/PageContainer/PageContainer.tsx:112-133 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b), which is the real source of per-tenant branding.
- `var(--primary-color)` is then consumed as an inline style in >15 components (icons, tag borders, accent bars, scrollbar, nprogress bar) — see `globals.css:30,50,76,94,117-118` for the framework-level usages (trilhas-frontend:src/styles/globals.css:1-173 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) and `RenderTagTable`/`HorarioCheck`/`CollapsedFields.less`/`MessageBallon.less`/`SubGroupHandle.tsx` for component-level usage.
- **Bug-shaped gap:** `Display.tsx` reads `var(--warning-color)` for its "warning" variant tag color, but no code path anywhere ever calls `setProperty("--warning-color", …)`, and no `.less`/`.css` file declares `--warning-color` on `:root` either — this custom property is permanently unset (trilhas-frontend:src/components/Display/Display.tsx:38-44 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). The tag falls back to the browser's inherited/initial color, i.e. the "warning" visual treatment silently does nothing for text color (though `color="orange"` on the antd `Tag` for list-type values still gives some visual signal).

---

## 2. Alert-severity styling

### 2.1 Notification bell / drawer — `DisplayNotificaoes` + `ItemNotificacao`
trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:1-201 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
trilhas-frontend:src/components/DisplayNotificaoes/ItemNotificacao/ItemNotificacao.tsx:1-139 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

- Two independent WebSocket connections are opened per session: one populates the notification list (`ws`), one is a "popover" feed used purely to fire an antd `notification.open()` toast (`wsPopover`) (trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:30-39,100-126 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
- The toast's icon is hard-coded amber `#FFAB00` regardless of the underlying alert severity (trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:73-96 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — i.e. a VERMELHO (red) bed alert and an AMARELO (yellow) one produce an identical amber toast; only the in-drawer list item (`ItemNotificacao`) actually reflects severity color.
- Unread-count badge: antd `Badge` with a numeric `count` — no severity-based recoloring of the badge itself, only presence of a number (trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:140-156 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
- `ItemNotificacao`: severity encoding is a left-edge color bar (`.detail-item-notification`, 5px wide) + a colored icon, both driven by `statusTrilha[notificacao.mensagem.alerta]?.ballColor` when the notification type is `"leito"` (bed/clinical alert); for `"setor"` (sector chat) messages the color is a flat neutral gray `#959595` (trilhas-frontend:src/components/DisplayNotificaoes/ItemNotificacao/ItemNotificacao.tsx:26-39 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). Unread state is a separate signal: a small blue dot (`#4894fd`, unrelated to the severity palette) plus a box-shadow "neumorphic" card style, present regardless of severity (trilhas-frontend:src/components/DisplayNotificaoes/ItemNotificacao/ItemNotificacao.less:1-29 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).

### 2.2 Generic API-error modal — `handleApiError`
trilhas-frontend:src/utils/feedback/handleApiError.tsx:1-103 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

- Single, undifferentiated severity: always `Modal.error(...)` (antd's red/error modal chrome) regardless of whether the underlying error is a validation issue, a permission error, or a server fault — there is no "warning" vs "error" vs "info" variant selection based on error type/status code.
- Field-level validation issues are rendered as a flat list of antd `Tag color="warning"` with a fixed `mdiAlertDecagram` icon (trilhas-frontend:src/utils/feedback/handleApiError.tsx:47-87 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — every individual field error looks the same regardless of how serious the validation failure is.
- This is the single, apparently universal error-surfacing utility (imported by `BalancoHidricoContent`, `ListOcupacoes`, `TrilhaInterativa`, and dozens more) — i.e. **one alert severity for all API failures app-wide.**

### 2.3 Evolution/record status icon+color — `handleIconByStatus`
trilhas-frontend:src/utils/handleIconByStatus.ts:1-23 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

| Status | Icon | Color |
|---|---|---|
| `salvo` (saved) | `mdiCheckCircleOutline` | `#258a10` (green — matches `variables.less` `@success-color`, the only place that token's value is reused, just re-typed as a literal) |
| `liberado` (released/signed) | `mdiCheckAll` | `#1890ff` (antd default blue — not in `statusTrilha` or `variables.less` at all) |
| `inativo` (inactive) | `mdiCancel` | `#ff1633` (matches `statusTrilha.VERMELHO.ballColor` / `@danger-color`, again re-typed as a literal) |
| `""` / default | `mdiInformation` | `#bababa` |

Used only in `HistoricoEvolucao` list items (desktop and mobile variants) to show medical-record (evolução) status (trilhas-frontend:src/components/HistoricoEvolucao/ItemEvolucao/ItemEvolucao.tsx:30-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). This is a **third, independent** severity-color mapping (distinct from `statusTrilha` and from the prescription `colorCheck` in §2.4), reusing the same green/red hex values by re-typing them rather than importing a shared constant.

### 2.4 Prescription check-state color — `HorarioCheck`
trilhas-frontend:src/components/Prescricao/HorarioCheck/HorarioCheck.tsx:126-138 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

```
suspenso            → icon #CCCCCC, antd tag color "grey"
administrado        → icon #389e0c, antd tag color "green"
motivo_nao_administrado → icon #d4b105, antd tag color "yellow"
asbutton (add slot) → icon var(--primary-color)
default/pending     → icon #25979c, antd tag color "cyan"
```

This is a **fourth, independent** color mapping. Notably its green (`#389e0c`) and amber (`#d4b105`) are neither the `statusTrilha` values nor the `handleIconByStatus` values — three different systems all encode "success/green" and "warning/amber" with three different hex pairs. A **fifth** variant appears in the same file's popover header icon: `horario.administrado ? "#acff76" : "#ff5252"` (trilhas-frontend:src/components/Prescricao/HorarioCheck/HorarioCheck.tsx:60-78 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — a *different* green/red pair again, used a few lines away from the `colorCheck` green/red pair in the same component.

### 2.5 Sepsis-protocol delay flag
trilhas-frontend:src/components/ProtocoloSepseContent/ItemProtocoloSepse/ItemProtocoloSepse.tsx:42-50 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

`item.atraso_primeira_hora` (item overdue within the first hour of the sepsis bundle) renders a `mdiClockAlert` icon hard-coded to `#e84748` — a **sixth** distinct "red" literal, different from `statusTrilha.VERMELHO.ballColor` (`#FF1633`), `@danger-color` (`#ff1633`), and the popover `#ff5252` above.

### 2.6 Sepsis protocol completion state — no color at all
trilhas-frontend:src/components/ProtocoloSepseContent/ProtocoloSepseContent.tsx:68-90 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

`concluida` (completed) renders a `mdiCheck` icon and `finalizado` (ended/discarded, with a rejection-reason popover) renders `mdiClose` — both in the **default/inherited icon color**, i.e. this is the one status representation in the whole sepsis flow that uses shape-only encoding (check vs. X) with no color differentiation, inconsistent with every other status representation in the app which pairs icon shape with a distinct color.

**Summary table — alert/status color systems found (all independent, none shared):**

| System | File | "Good/green" | "Bad/red" | "Warning/amber" |
|---|---|---|---|---|
| Clinical severity (`statusTrilha`) | statusTrilha.ts | `#00DC50` | `#FF1633` | `#ffd900` (AMARELO) / `#ff5900` (LARANJA) |
| Evolução record status | handleIconByStatus.ts | `#258a10` | `#ff1633` | n/a (uses blue `#1890ff` for "liberado") |
| Prescription check tag/icon | HorarioCheck.tsx colorCheck | `#389e0c` | n/a (uses grey for suspended) | `#d4b105` |
| Prescription popover icon | HorarioCheck.tsx CustomWrapper | `#acff76` | `#ff5252` | n/a |
| Sepsis-item delay flag | ItemProtocoloSepse.tsx | n/a | `#e84748` | n/a |
| Bed-occupancy gauge | DashboardCard.tsx (§4.4) | `#00DC50` | `#FF1633` | `#FFAB00` |
| Notification toast icon | DisplayNotificaoes.tsx | n/a | n/a | `#FFAB00` |

---

## 3. Critical-value / abnormal-vitals highlighting

This is the most consequential gap found in the audit: **there is essentially no threshold-based visual flagging of abnormal clinical values anywhere in the codebase.**

### 3.1 Vital signs — `ItemSinaisVitais`
trilhas-frontend:src/components/BalancoHidricoItens/ItemSinaisVitais/ItemSinaisVitais.tsx:29-127 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

Heart rate, respiratory rate, blood pressure (systolic/diastolic), temperature, SpO2, HGT (capillary glucose), ventilation mode, supplemental O2 flow, FiO2, consciousness level, pain scale — all 15 fields are rendered through the same generic `ListItem` (label/value row with a `@primary-color` accent bar, see trilhas-frontend:src/components/ListItem/ListItem.less:15-22 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) with **no conditional styling based on value**. A SpO2 of 99% and a SpO2 of 60% render identically.

### 3.2 Labs / assistive info — `InformacoesAssistenciais`
trilhas-frontend:src/components/InformacaoesAssistenciais/InformacoesAssistenciais.tsx:1-171 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

Same pattern for blood pressure, RASS, Glasgow, delirium, 24h diuresis, 24h fluid balance, temperature, leukocytes, platelets, CRP, lactate, pH, bicarbonate, pO2, pCO2, P/F ratio, creatinine, urea, bilirubin — every one of these clinically load-bearing values (several of which are classic ICU deterioration/sepsis markers) is shown via the same neutral `ListItem`, no color, no icon, no bolding differentiated by abnormal range.

### 3.3 24h summary indicators — `ItemIndicadores24h`
trilhas-frontend:src/components/ItemIndicadores24h/ItemIndicadores24h.tsx:1-63 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

Fluid balance, diuresis, HGT, bowel movements, max temperature, and gains over 24h — again rendered through plain `ListItem`, no thresholding.

### 3.4 Fluid-balance grid — `GridView`
trilhas-frontend:src/components/BalancoHidricoVisaoGeral/GridView/GridView.tsx:81-96 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
trilhas-frontend:src/components/BalancoHidricoVisaoGeral/GridView/GridView.less:38-44 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

Every non-zero cell in the entrada/saída (intake/output) hourly grid is rendered with a fixed green pill background (`background: #42e26f`, defined once in the `.cell` class) purely to signal "there is a value here" — a large positive intake and a large unexpected output extreme are visually identical. There is no positive/negative-balance color split, and no "out of expected range" flag.

### 3.5 SOFA score tag — static severity regardless of score
trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:85-94 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

```
<Tag className="tag-sofa" style={{borderRadius: "16px"}} color="warning">
  Escore sofa: {initialValues.dados_prontuario.escore_sofa}
</Tag>
```

The SOFA (Sequential Organ Failure Assessment) score — a validated ICU severity/mortality-risk score — is always rendered with the antd `"warning"` tag color, whether the score is 0 (low risk) or 20+ (very high risk). No color escalation by score band exists anywhere the SOFA value is displayed.

### 3.6 The one place a "critical value" mechanism *looks* like it exists but doesn't
trilhas-frontend:src/components/RenderTagTable/RenderTagTable.tsx:1-39 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

`RenderTagTable` takes an explicit `color` prop and renders a colored left-border title or a colored/bordered `Tag` — structurally, this looks exactly like a component built to encode critical-value severity in table cells. In practice, it is used in 8 different admin-table column definitions (`ColumsSetorTable`, `ColumsLeitoTable`, `ColumsUsuarioTable`, `ColumsEstabelecimentoTable`, `ColumsGrupoTable`, `ColumnsGestaoPacientesTable`, `ColumsInconsistencia`, `ColumsRelatorioEvolucaoTable`) and in **every single call site** the `color` argument passed is the literal string `"var(--primary-color)"` (trilhas-frontend:src/components/ColumsSetorTable/ColumsSetorTable.tsx:34,44,55; src/components/ColumsLeitoTable/ColumsLeitoTable.tsx:35,45,59,68; src/components/ColumsUsuarioTable/ColumsUsuarioTable.tsx:34,44,55; src/components/ColumnsGestaoPacientesTable/ColumnsGestaoPacientesTable.tsx:34,42,50; src/components/ColumsInconsistencia/ColumsInconsistenciaAssinatura.tsx:46 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). None of these tables are clinical-value tables (they're admin listings of setores/leitos/usuários/estabelecimentos/grupos/inconsistências), so this isn't in itself a clinical gap — but it demonstrates the codebase already has a per-cell color-injection primitive that was simply never wired to any threshold logic, in any table, including the two clinically relevant ones (`ColumnsEntrada`/`ColumnsSaida` for fluid balance, which don't use `RenderTagTable` at all and have zero `render` color logic — trilhas-frontend:src/components/ColumnsBalancoHidrico/ColumnsEntrada/ColumnsEntrada.tsx:1-98, src/components/ColumnsBalancoHidrico/ColumnsSaida/ColumnsSaida.tsx:1-112 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).

### 3.7 Where a form of "critical" flagging *does* exist
- **Invasive procedures badge**: an amber `mdiAlertBoxOutline` icon (`#d6a400`, matching `@warning-color`'s literal value) shown on the bed card only when `procedimentos_invasivos.length > 0`, with a popover listing them (trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:423-454 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — presence/absence flagging, not value-threshold flagging.
- **Sepsis first-hour delay** (§2.5) and **items em atraso** (protocol items overdue) — a `mdiClockAlert` icon on the trilha card (trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:570-578 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — again presence-based (an item is late) rather than derived from a clinical value.
- **Bed-occupancy percentage gauge** (§4.4) is the *only* place in the whole codebase where a continuous number is mapped to a red/amber/green scale by threshold.

---

## 4. Data-density choices in clinical tables/dashboards

### 4.1 ICU bed grid — `ListOcupacoes`
trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:420-436 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

Responsive `Col span` breakpoints (24-column antd grid):
```
width > 2800            → span 4   (≈6 cards/row)
1800 < width < 2400     → span 6   (≈4 cards/row)
1260 < width < 1800     → span 8   (3 cards/row)
800  < width < 1260     → span 12  (2 cards/row)
width < 800             → span 24  (1 card/row)
```
Note the gap between 2400 and 2800 (no rule matches width in (2400,2800], `span` becomes `undefined`, antd defaults to full-width in that band) — a density inconsistency/bug band on very large monitors.

Loading state uses 10 `SkeletonList` placeholders (`itemHeight=230`) rather than skeletons shaped like the actual card (rounded button bars only) — trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:466-484 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, src/components/SkeletonList/SkeletonList.tsx:20-37 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b.

Each bed card (`CollapseCard`) toggles between a fixed `11rem` collapsed height and `50rem` expanded height via CSS animation (trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.less:1-21 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — i.e. density is a manual global collapse/expand toggle (`collapseAll` prop) rather than per-card user control, all-or-nothing across the whole ward view.

### 4.2 Sector/dashboard grid — `ListDashboard`
trilhas-frontend:src/components/ListDashboard/ListDashboard.tsx:26-39 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

```
width > 1800          → span 6
1260 < width < 1800   → span 8
800 < width < 1260    → span 12
width < 800           → span 24
```

**Discrepancy vs. §4.1:** this is structurally the same "responsive card grid" pattern used one page up the navigation hierarchy (sectors dashboard vs. beds-in-a-sector), but it uses a *different* breakpoint set (no 2400/2800 tier, no `undefined` gap) and does not reuse the shared `collapseRule`/`collapseRuleMobile` constants (`1260`/`800`, trilhas-frontend:src/utils/constants.ts:5-6 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — the span logic re-derives its own literals that happen to partially coincide with those constants rather than importing them. Two near-identical grid-density behaviors, hand-duplicated with drift.

### 4.3 Audit/inconsistency tables — dense virtualized-height tables
trilhas-frontend:src/components/InconsistenciaContent/InconsistenciaAssinaturaContent/InconsistenciaAssinaturaContent.tsx:107-118 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

`size="small"`, fixed vertical scroll region `calc(100vh - 350px)`, server-side pagination + sortable columns — this is the highest-density tabular view in the app (compliance/signature-inconsistency audit), contrasting with the card-based, low-density ICU bed views. Same `scroll.y` pattern reused in `BalancoHidricoContent`'s tables implicitly via `size="large"` (lower density) — trilhas-frontend:src/components/BalancoHidricoContent/BalancoHidricoContent.tsx:458-471 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b — i.e. table density (`size="small"` vs `"large"`) is chosen ad hoc per screen, not from a shared density token.

### 4.4 Bed-occupancy gauge — `DashboardCard`
trilhas-frontend:src/components/ListDashboard/DashboardCard/DashboardCard.tsx:291-307 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

```
occupancy > 70%  → strokeColor #FF1633 (red)
occupancy > 50%  → strokeColor #FFAB00 (amber)
else             → strokeColor #00DC50 (green)
```

This is the **only threshold-based numeric-to-color mapping in the codebase**. Its red and green match `statusTrilha.VERMELHO.ballColor`/`NEUTRO.ballColor` exactly, but its amber (`#FFAB00`) does not match `statusTrilha.AMARELO.ballColor` (`#ffd900`) — the same conceptual traffic-light is reimplemented with one hex accidentally-matching and one hex silently different, rather than importing `statusTrilha`.

The same card also renders a stacked-bar breakdown of alert counts (red/amber/green/assisted-blue) via 4 separate antd `Progress` bars, each independently colored from `statusTrilha` directly (correctly, unlike the occupancy gauge) — trilhas-frontend:src/components/ListDashboard/DashboardCard/DashboardCard.tsx:154-176,356-392 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b.

---

## 5. Status color-coding semantics (patient/bed/prescription/sepsis)

### 5.1 Patient/bed alert status (the dominant semantic)
`ocupacao.alerta` / `trilha.alerta` / `mensagem.alerta` / `criterio.alerta`, resolved through `statusTrilha`, with `assistido === true` always overriding to `ASSISTIDO` — applied consistently to:
- Patient header border + glow: `InfoPacienteHeader` (trilhas-frontend:src/components/InfoPacienteHeader/InfoPacienteHeader.tsx:26-43 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b)
- Bed card border + glow + "ball" indicator + gender icon + age-badge background: `CollapseCard` (trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:268-421 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b)
- Sector dashboard card border + glow + ball: `DashboardCard` (§4.4)
- Chat message header ball + gender icon + age badge, keyed off the *bed's* alert, not the message itself: `MessageBallon` (trilhas-frontend:src/components/MessageBallon/MessageBallon.tsx:76-152 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b)
- Notification item left-bar + icon (§2.1)
- Tab-selector buttons in the recommendations drawer, correctly reading each trilha's own `alerta` (trilhas-frontend:src/components/TabRecomendacoes/TabRecomendacoes.tsx:98-148 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b)

### 5.2 Discrepancy: criteria-content panel hard-codes "VERMELHO" regardless of actual severity
trilhas-frontend:src/components/TabRecomendacoes/TabRecomendacoes.tsx:213-231 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

Immediately below the correctly-dynamic tab-selector buttons (§5.1), the criteria/recommendation `Collapse.Panel` content is styled with:
```
backgroundColor: isLight ? statusTrilha["VERMELHO"].backgroundLight : statusTrilha["VERMELHO"].background
```
— a **literal** `"VERMELHO"`, not `ocupacao.trilhas[i].alerta`. Every criteria panel, for every severity level (amarelo, laranja, vermelho), renders with the same red-tinted background. This is a genuine internal inconsistency: the same feature correctly reflects severity one component up (the tab button) and then ignores it one component down (the panel content).

### 5.3 Bed occupancy state (`leito.ocupado`)
Boolean, not part of the severity palette — occupied beds get the full alert-colored border/ball treatment; empty beds get a flat neutral border (`#212433`) and an `.empty` class with a matching neutral box-shadow (trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.less:23-26 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — i.e. "empty" is visually a "calm/neutral" state, not a distinct alert color, and is indistinguishable at a glance from a `NEUTRO` occupied bed except for content (no patient name/vitals rendered).

### 5.4 Prescription check states
Covered in §2.4 (`HorarioCheck` — suspenso/administrado/motivo_nao_administrado/pending, 5 different literal color sets across 2 nearby code paths in the same file).

### 5.5 Sepsis protocol states
- Acceptance workflow (`TrilhaInterativa`): plain primary-color "Aceitar" button vs. `danger ghost` "Recusar" button — a binary accept/refuse using antd's built-in `danger` treatment, not the `statusTrilha` palette (trilhas-frontend:src/components/TrilhaInterativa/TrilhaInterativa.tsx:199-224 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
- Checklist item states: `concluida` (done, check icon, no color — §2.6), `finalizado`/discarded (X icon, no color, with rejection-reason popover), first-hour delay (red `#e84748`, §2.5), per-item checkbox (`checado`/"Checar" label toggle, antd default styling, no severity color at all) (trilhas-frontend:src/components/ProtocoloSepseContent/ItemProtocoloSepse/ItemProtocoloSepse.tsx:14-67 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).

### 5.6 Medical-record/evolução status
Covered in §2.3 (`handleIconByStatus`: salvo/liberado/inativo/default).

---

## 6. Clinical form UX (dynamic forms, conditional fields, skeleton loading)

### 6.1 Schema-driven dynamic form engine
trilhas-frontend:src/components/FormDadosProntuario/SubFormsDadosProntuario/SelectCampoType/SelectCampoType.tsx:1-177 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

Every clinical data-entry form (patient admission, movement/transfer, discharge, vitals) is driven by a `Models.DadosFormDinamico[]` schema (grupo/campos/subGroup metadata), dispatched by `campo.type` to one of 10 typed sub-renderers (`string`, `select`, `interval`, `number`, `boolean`, `checkbox`, `data`, `list`, `masked`, `multicheck`). This is a metadata/config-driven form architecture rather than hand-built forms per screen — new clinical fields are added by editing the `dataForms/*.ts` schema objects, not by writing new JSX.

### 6.2 "Multi-step" is simulated, not a wizard
No `antd Steps` (stepper) component is used anywhere in the codebase (`grep` for `Steps` returns zero matches). Instead, the "multi-step" feel of clinical data entry is produced by three separate, uncoordinated mechanisms:
1. **Accordion sections** (`CollapsedFields`): each `grupo` (e.g. "Ventilação Mecânica", "Sedação") is a collapsible `Collapse.Panel`, all `defaultActiveKey`-expanded unless `collapseAll` is set (trilhas-frontend:src/components/FormDadosProntuario/CollapsedFields/CollapsedFields.tsx:32-38 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
2. **Tabs inside a drawer** for movement history vs. new-entry (trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:558-647 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
3. **Sequential drawers** for distinct actions (choose evolução type → drawer opens the specific form) (trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:136-257 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).

### 6.3 Conditional fields — three different mechanisms, no shared abstraction
- **Group-level "nullify" switch**: a per-group `Switch` (only shown in `mode !== "in_page"`) that flags an entire fieldset (e.g. "Parada Cardiorrespiratória") to be nulled out on submit via a `nullifiers` map walked recursively by `nullifyFields` (trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:36-54 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, src/components/FormDadosProntuario/CollapsedFields/CollapsedFields.tsx:56-83 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). The fields stay mounted and interactive; only the *submitted value* is nulled.
- **Sub-group-level "checavel" switch**: shows/hides a sub-group's fields via inline `display: none/block` (fields remain mounted in the form tree so antd `Form` state is preserved) — trilhas-frontend:src/components/FormDadosProntuario/SubGroupHandle/SubGroupHandle.tsx:32-91 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b.
- **Permission/company-type-driven field disabling**: e.g. `FormLeito` disables name/code inputs unless `empresaData?.tipo === "manual"`, and hides the camera-IP field entirely unless `can_manage_camera` (trilhas-frontend:src/components/FormLeito/FormLeito.tsx:42-66 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — conditional rendering driven by RBAC/tenant config rather than by other field values.

None of these three conditional-field mechanisms share a common implementation; each was hand-rolled per form area.

### 6.4 Loading states — two unrelated patterns, no shared choice logic
- **Skeleton rows** (`SkeletonList`): N rounded `Skeleton.Button` bars inside `Form.Item`s — used for list/card placeholders (e.g. the bed grid while paginating) (trilhas-frontend:src/components/SkeletonList/SkeletonList.tsx:1-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). Shape is generic (a rounded bar), not shaped to the content it's replacing.
- **Full-screen overlay spinner** (`FadeLoading`): a fixed, full-viewport translucent (`#fffaf566`) overlay with a spinning `mdiLoading` icon colored `@primary-color`, blocking all interaction underneath (trilhas-frontend:src/components/FadeLoading/FadeLoading.tsx:1-23 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, src/components/FadeLoading/FadeLoading.less:1-17 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). Used for save/submit/mutation operations across nearly every form-bearing drawer (`ListOcupacoes`, `BalancoHidricoContent`, etc.) — this is a global-block pattern rather than local per-field/per-section loading affordance.

There is no consistent rule visible in code for *which* loading pattern a given screen uses; it appears to be per-screen author choice (initial fetch → skeleton; mutation → full-screen spinner, in most but not all cases).

---

## 7. Real-time patterns

Three independent real-time mechanisms coexist, with no shared abstraction layer:

### 7.1 Raw WebSocket — notifications
`w3cwebsocket` connections to `${baseWsURL}notificacao/` (list) and the same endpoint with `?popover=true` (toast feed), manually reconnected/cleaned up per component mount (§2.1). No reconnection/backoff logic visible; `ws.onerror` just logs to console (trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:100-133 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).

### 7.2 Firestore — chat, presence, and video-room roster
`useCollection`/`useDocument` hooks wrap Firestore `onSnapshot` listeners generically (trilhas-frontend:src/hooks/Firestore/useCollection.tsx:1-77 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b), backed by a singleton Firebase app (trilhas-frontend:src/utils/getFirebaseApp.ts:1-17 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). Used for:
- Video-call room presence (`usersOnline` filtered by `online_call === true`) with a live green `Ball` indicator (`#00DC50`, hard-coded, coincidentally matching `statusTrilha.NEUTRO.ballColor`) — trilhas-frontend:src/components/BuildVideoChat/BuildVideoChat.tsx:34-37,113-146 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b.
- Sector chat messages/reactions (`MessageBallon`, not shown in full here but consuming Firestore-backed hooks per component imports).

### 7.3 Polling / `setInterval` — dashboard & bed-list auto-refresh
`ListOcupacoes` runs a `setInterval(() => applyFilters({...filters}), reloadTime*1000)` gated by an app-wide `AutoReloadContext.update` flag, independent of both the WebSocket and Firestore channels (trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:116-141 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). This means the primary ICU bed grid does **not** update live off the alert WebSocket — it refetches on a timer, so a new red alert can take up to `reloadTime` seconds to appear on the grid even though the same alert would show near-instantly in the notification bell/toast.

### 7.4 Video display
- **ICU camera stream** (`DisplayVideoUti`): an `<iframe>` embed of a camera URL, with a user-toggleable CSS `blur(20px)` filter for patient-privacy ("eye/eye-off" button) that is purely a client-side visual mask — the underlying stream is not stopped, only visually obscured (trilhas-frontend:src/components/DisplayVideoUti/DisplayVideoUti.tsx:17-68 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
- **Telemedicine call** (`BuildVideoChat`/`VideoCall`): Agora RTC SDK (`agora-rtc-react`) for actual bidirectional video, gated by a `hasVideoDevice` check (falls back to an antd `Result status="warning"` "Video Offline" state if no camera is present) (trilhas-frontend:src/components/BuildVideoChat/BuildVideoChat.tsx:53-110 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b). This is architecturally distinct from the passive camera-monitoring iframe — two different video technologies for two different clinical use cases (passive UTI monitoring vs. active telemedicine call), which is a reasonable and clear separation.

### 7.5 Notification badges
Simple antd `Badge count={n}` on the bell icon (§2.1) and a separate ad hoc "unread messages" badge on `DashboardCard` (a plain circular div showing `qtd_mensagens`, capped display at `"+99"`, background = `@secondary-color`, i.e. not the alert palette) (trilhas-frontend:src/components/ListDashboard/DashboardCard/DashboardCard.tsx:250-259 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, src/components/ListDashboard/DashboardCard/DashboardCard.less:58-69 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b) — two different badge visual treatments (antd `Badge` vs. hand-rolled circular div) for conceptually the same "unread count" affordance.

---

## 8. Consistent, well-factored patterns worth preserving

Not everything is inconsistent — several patterns are genuinely reusable and consistently applied:

- **`DrawerBuilder`**: a single reusable drawer scaffold (95vw mobile / 50vw desktop via the shared `collapseRule=1260` constant, standardized Salvar/Fechar footer buttons, `destroyOnClose`) used for essentially every create/edit/detail panel in the app (trilhas-frontend:src/components/DrawerBuilder/DrawerBuilder.tsx:1-99 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
- **`AlertDelete`**: a consistent two-step destructive-action confirmation (an antd `Alert type="warning"` banner + a `Popconfirm` with a `danger` "Excluir" button) used uniformly for destructive flows (trilhas-frontend:src/components/AlertDelete/AlertDelete.tsx:1-49 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
- **`Ball` icon**: a small two-tone SVG (colored dot + darker background ring) used identically wherever a compact severity/presence dot is needed (bed cards, dashboard cards, chat headers, online-user roster) (trilhas-frontend:src/icons/Ball.jsx:1-34 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b).
- **`collapseRule` (1260px) / `collapseRuleMobile` (800px)**: centrally defined breakpoint constants (trilhas-frontend:src/utils/constants.ts:5-6 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b), correctly reused by `DrawerBuilder`, `Prescricao`, `ProtocoloSepseContent`, `ListOcupacoes` (for the `collapsed` boolean, though *not* for its `span` breakpoints — see §4.2).

---

## 9. Candidate ADR decisions

Each entry: **what the legacy did** → **evident rationale** → **assessment for the new platform**.

1. **Two-tier color model: static JS severity palette (`statusTrilha`) + runtime CSS-var tenant brand color (`--primary-color`).**
   Rationale (inferred): keep patient-safety colors (red/amber/green/blue) immune from white-label branding while still allowing each hospital group to reskin the "brand" chrome (headers, buttons, accents).
   Assessment: **the separation itself is sound and worth keeping as an explicit rule** in the new design system (e.g. two token namespaces: `clinical.*` immutable, `brand.*` tenant-overridable) — but it must be *documented and enforced*, not incidental. In the legacy app it was never written down; multiple components (§2.3, §2.4, §4.4) reinvented "red/green/amber" with their own literals instead of importing `statusTrilha`, so the boundary leaked into token duplication rather than staying clean.

2. **No critical-value/threshold color-coding for vitals, labs, fluid balance, or SOFA score (§3).**
   Rationale (inferred): none evident — this looks like an unaddressed gap rather than a deliberate choice; the `RenderTagTable` component (§3.6) suggests someone built a per-cell color primitive intending to use it for this purpose and then never wired the thresholds.
   Assessment: **this is the highest-leverage clinical UX improvement available for the new platform** — define reference ranges per vital/lab (age/context-adjusted where applicable) and a shared "abnormal value" token scale (e.g. mild/moderate/critical) applied uniformly to vitals cards, lab panels, and fluid-balance grids. Do not port the current "no encoding" behavior forward as if it were a considered baseline.

3. **Single generic `handleApiError` = always `Modal.error`, no severity/type differentiation (§2.2).**
   Rationale (inferred): simplicity — one utility, one call site pattern, used everywhere.
   Assessment: keep the *one shared utility* idea (good — it did produce app-wide consistency for the error path) but extend it with a severity parameter (validation/warning vs. server error vs. permission) so visual weight matches actual severity, and so the field-level `Tag color="warning"` treatment isn't applied uniformly to every kind of validation issue.

4. **Multi-step clinical forms are simulated via accordion + tabs + sequential drawers, never a `Steps` wizard (§6.2).**
   Rationale (inferred): the schema-driven form engine (§6.1) organizes fields into named "groups," and accordion panels were the natural container for that; true linear workflows (e.g. movement history vs. new entry) were solved with tabs instead.
   Assessment: the underlying schema-driven engine is a strong pattern worth carrying forward (fast to extend, one rendering path per field type). Whether true wizard/stepper semantics are needed depends on clinical workflow requirements the new platform should validate with users — but the *conditional field* logic (§6.3) should be unified into one mechanism (a single "visibility/nullability" rule engine) rather than reimplemented three separate ways.

5. **Three independent real-time channels (WebSocket, Firestore, polling) with no shared reconnection/backoff or update-propagation guarantee (§7.1–7.3).**
   Rationale (inferred): each was added when a specific feature needed it (notifications → WS, chat/presence → Firestore, dashboard refresh → simple timer) without a unifying real-time layer.
   Assessment: **the biggest correctness risk found**, given that the primary ICU bed grid (`ListOcupacoes`) refreshes on a polling timer rather than reacting to the same alert push that drives the notification bell — meaning the two "live" views of the same event (bell vs. grid) can visibly disagree for up to `reloadTime` seconds. The new platform should standardize on one real-time transport (or a single subscription abstraction that both drives) so the grid and alerting are guaranteed consistent.

6. **Bed-occupancy gauge (DashboardCard) reimplements the red/amber/green traffic-light with its own literals and its own thresholds (70%/50%), independent of `statusTrilha` (§4.4).**
   Rationale (inferred): occupancy % is a different *kind* of "severity" (operational capacity, not per-patient clinical alert) from `statusTrilha`'s meaning, so a separate scale may have been intentional.
   Assessment: the *concept* of a separate operational-capacity scale is reasonable, but it should be a **named, shared token set** (e.g. `capacity.low/medium/high`) rather than inline hex literals that almost — but don't quite — match the clinical palette; the near-miss amber (`#FFAB00` vs `#ffd900`) is exactly the kind of accidental drift a token system prevents.

7. **`--warning-color` CSS custom property is referenced but never defined (§1.3), silently degrading the `Display` component's "warning" variant.**
   Rationale: likely an incomplete refactor — `--primary-color`/`--primary-shadow-color` were wired into the runtime theming hook but `--warning-color` (and the other `variables.less` semantic tokens) were not.
   Assessment: a concrete cautionary example for the rebuild — if a runtime CSS-variable theming approach is reused, every token the LESS layer promises must actually be set at runtime (or the component layer must not assume it is). Recommend a lint/test that asserts all `var(--x)` usages have a corresponding `setProperty`/`:root` definition.

8. **Two visually distinct "loading" affordances (skeleton rows vs. full-screen blocking spinner) chosen per-screen with no documented rule (§6.4).**
   Rationale (inferred): skeleton for initial list/page load, full-screen spinner for mutations — a reasonable *intuitive* split, but never formalized.
   Assessment: worth formalizing explicitly (e.g. "list/page loads always skeleton; discrete mutations always inline-button-spinner, never full-screen block") — the legacy full-screen block-on-mutation pattern is heavy-handed for a clinical tool where staff may need to keep working elsewhere on screen; the new platform should default to non-blocking, localized loading feedback except where data integrity truly requires a blocking wait.

9. **Reusable `DrawerBuilder`/`AlertDelete`/`Ball` primitives, consistently applied (§8).**
   Rationale: clear intentional componentization for the most repeated UI shapes (edit panel, destructive confirm, status dot).
   Assessment: **carry these forward as-is conceptually** — they are the parts of this system that most resemble a real design system and should inform the new platform's core primitives (dialog/drawer shell, destructive-confirmation pattern, status-dot atom).

10. **Per-tenant white-label color is the only "theme"; there is no evidence of per-tenant *typography*, spacing, or logo-driven layout customization beyond color.**
    Rationale (inferred): `cor_primaria` is the only per-company customization field surfaced anywhere in the components read.
    Assessment: if the new platform needs deeper multi-tenant branding (logo placement, secondary color, dark/light default), that is new scope, not a lift-and-shift — the legacy mechanism only proves out single-hex runtime recoloring via CSS custom properties plus `dynamic-antd-theme`, which is a reasonable technique to reuse for that one dimension.
