# D-02 — Component Library & Information Architecture Inventory
**Repo:** `trilhas-frontend` · **Commit:** `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` (read-only)
**Stack facts (verified):** Next.js 12 (pages router) + React 17 + antd 4.21 + LESS (`next-plugin-antd-less`), Firebase 8 (Firestore only), `agora-rtc-react` (video), raw `websocket` client (notifications), `moment`, `nookies` (cookie-based SSR auth). — trilhas-frontend:package.json:1-45 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

All claims below are derived from reading the actual `.tsx`/`.less` source, not from filenames. Every material claim has an inline citation in the form `trilhas-frontend:path:lines @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b`.

---

## 1. Design Tokens & Theming Engine

### 1.1 Token source of truth
Two token files exist and are **not identical in role**:

| File | Role |
|---|---|
| `src/styles/variables.less` | LESS `@variables` consumed at **build time** by the antd Less compiler. |
| `next.config.js` `variables` object | The **same 15 values, hand-duplicated** and passed into `withAntdLess({ modifyVars })`. |

trilhas-frontend:src/styles/variables.less:1-15 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
trilhas-frontend:next.config.js:5-21 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

| Token | Value | Notes |
|---|---|---|
| `@primary-color` | `#fe6d01` (orange) | Also the hard default re-applied at app mount, see 1.3 |
| `@secondary-color` | `#606060` | |
| `@primary-color-shade` | `darken(@primary-color, 47%)` | derived |
| `@background-color` | `#333` | |
| `@success-color` | `#258a10` | |
| `@info-color` | `#1a3bb7` | |
| `@default-color` | `#bbbbbb` | |
| `@danger-color` / `@error-color` | `#ff1633` | aliased |
| `@warning-color` | `#d6a400` | |
| `@skeleton-text` | `#eee3` | |
| `@degree` / `@grad-perc` | `120deg` / `-100%` | used for gradient utilities |
| `@header-opacity` | `0.8` | |
| `@border-width` | `3px` | |

trilhas-frontend:src/styles/variables.less:1-15 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

**Critically:** the antd theme is compiled with `getThemeVariables({ dark: true, compact: true })` as the *base*, and the custom variables above are layered on top — i.e. **the shipped build is antd's dark theme by default**; "light mode" is a separate, hand-maintained CSS override layer (§1.2), not a first-class antd theme. trilhas-frontend:next.config.js:23-37 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 1.2 Light/Dark switching
- `useLightTheme()` reads/writes a `theme.light` cookie and calls `window.location.reload()` on toggle — **switching theme is a full page reload**, not a live re-render. trilhas-frontend:src/hooks/useLightTheme.ts:1-23 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- When `isLight`, `_app.tsx` dynamically imports `themes/LightTheme.tsx` (`ssr:false`), which does nothing but `require("./LightTheme.less")` — a **second, hand-written stylesheet of `.light`-suffixed class overrides** layered on top of the dark-theme antd build. trilhas-frontend:src/pages/_app.tsx:18-51 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/themes/LightTheme.tsx:1-9 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- Consequence: **every component that needs to look correct in both modes must locally branch on an `isLight` boolean and append a `"light"` class name** — confirmed in ~30+ components (`ItemDefault`, `ListItem`, `MobileCardWrapper`, `MicroIndicadores` callers, `CollapseCard`, `GridView`/`MobileView`, etc.), e.g. trilhas-frontend:src/components/ItemDefault/ItemDefault.tsx:27-31 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. There is no shared "theme context" object with semantic colors — each component re-derives literal hex values per mode (e.g. `GridView.tsx` hardcodes `"#434343"`/`"#fff"` and `"#eeeeee"`/`"#373737"` inline). trilhas-frontend:src/components/BalancoHidricoVisaoGeral/GridView/GridView.tsx:15-19 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 1.3 Per-tenant white-labeling (runtime color)
- `useChangeColorTheme().changeColorTheme(color)` calls the `dynamic-antd-theme` package to recompute Ant Design's Less variables **at runtime in the browser**, then sets two CSS custom properties (`--primary-color`, `--primary-shadow-color`) on `document.documentElement`. trilhas-frontend:src/hooks/useChangeColorTheme.ts:1-19 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- `PageContainer` calls this with `` `#${data.cor_primaria}` `` — i.e. **each company (`empresa`) has a stored hex brand color** (`Models.Usuario.Empresa.cor_primaria`) fetched over REST, and the whole app re-themes itself per tenant after login. trilhas-frontend:src/components/PageContainer/PageContainer.tsx:114-133 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- On mount, `_app.tsx` unconditionally forces `changeColorTheme("#fe6d01")` **only when `isLight`** — meaning dark-mode users rely solely on the SSR-compiled default until `PageContainer` mounts and re-applies the tenant color, while light-mode users get an extra hardcoded reset to the default orange before the tenant color is loaded (visible FOUC of the wrong brand color). trilhas-frontend:src/pages/_app.tsx:36-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 1.4 Domain color vocabulary — `statusTrilha`
A single, un-typed (`as any`) 5-state clinical alert palette is imported everywhere status needs a color: `NEUTRO` (green), `VERMELHO` (red), `AMARELO` (yellow), `LARANJA` (orange), `ASSISTIDO` (blue — "attended to"). Each state carries 6 pre-computed shades (`color`, `background`, `backgroundLight`, `ballColor`, `ballBackground`, `backgroundShade`) so components never compute contrast — they just pick the shade key for the context (border vs. fill vs. light-mode fill). trilhas-frontend:src/utils/statusTrilha.ts:1-45 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. This is the **actual semantic-color system** of the product (more than the LESS `@success/@warning/@danger` tokens, which are barely used in clinical UI) and is consumed via inline `style={{ backgroundColor: statusTrilha[...] }}` rather than CSS classes/custom properties, e.g. in the bed card: trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:268-356 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b.

### 1.5 Icon systems (two, coexisting)
1. **Material Design Icons** via `@mdi/js` path data, always wrapped by `MaterialIcon`, which forces `size="1em"` and an `anticon` class so MDI glyphs sit flush inside antd's icon slots (buttons, badges, tags). Used in the overwhelming majority of the ~281 component files. trilhas-frontend:src/components/MaterialIcon/MaterialIcon.tsx:1-19 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
2. **Bespoke hand-drawn SVG components** (`.jsx`, no TS types) for domain concepts that MDI doesn't cover: clinical roles (`Enfermagem`, `Farmaceutico`, `Fisioterapeuta`, `Fonoaudiologo`, `Medico`, `Musicoterapia`, `Nutricionista`, `Psicologo`, `TecEnfermagem`, `Terapeuta`), gender (`Masculino`, `Feminino`), config-menu icons (`EmpresaIcon`, `EstabelecimentoIcon`, `GrupoIcon`, `LeitosIcon`, `MonitorIcon`, `ProfissionalIcon`, `SetorIcon`) and decorative assets (`Logo`, `Waves`, `Ball`, `AddEmoji`, `PdfIcon`). trilhas-frontend:src/icons/configs/EstabelecimentoIcon.jsx:1-37 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b — each takes `size`/`color` props and hardcodes its own viewBox, i.e. **no shared icon-sizing contract** between the two systems.

---

## 2. Layout System

### 2.1 `PageContainer` — the app shell
`components/PageContainer/PageContainer.tsx` is the single layout root used by essentially every authenticated page (25 usages outside its own folder). It is responsible for:
- antd `Layout` with fixed `Header` / `Content` / `Footer`. trilhas-frontend:src/components/PageContainer/PageContainer.tsx:227-233,433-482 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- **Cascading data loading**: given `idEmpresaAtual`/`idEstabelecimentoAtual`/`idSetorAtual` props (populated from the Next.js route params by the calling page), it independently fetches empresa → estabelecimento → setor via REST and exposes them via `onLoadEmpresa/onLoadEstabelecimento/onLoadSetor` callbacks — i.e. **breadcrumb-like context state is refetched by every page that mounts `PageContainer`**, not read from a shared cache. trilhas-frontend:src/components/PageContainer/PageContainer.tsx:114-179,198-212 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- Applies the tenant color theme on empresa load (§1.3). trilhas-frontend:src/components/PageContainer/PageContainer.tsx:120 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- Renders the **collapsed/mobile hamburger drawer** (antd `Drawer`, `placement="left"`, `width="70vw"`) containing `ItensMenuMobile` (swap empresa/estabelecimento/setor) when `width < collapseRule` (1260px). trilhas-frontend:src/components/PageContainer/PageContainer.tsx:227-323 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- Renders the persistent header actions: auto-reload `Switch`, `SwitchThemeButton`, `SelectEmpresaAtual`, breadcrumb-style `Tag` trail (estabelecimento/setor, not a `Breadcrumb` component — see §4.3), `DisplayNotificaoes` (WebSocket bell), user tag, config/profile/logout icon buttons. trilhas-frontend:src/components/PageContainer/PageContainer.tsx:324-432 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- Renders a page-level **back button + `Typography.Title` page name** row inside `Content`, gated by `hideBackButton`; back navigation sets a `setBacking(true)` flag before `router.back()` with a 200 ms delay (used elsewhere to distinguish "back" navigation from forward, e.g. to skip a refetch). trilhas-frontend:src/components/PageContainer/PageContainer.tsx:441-472 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- Renders a static copyright `Footer` naming the vendor ("iTech Ltda") and environment (prod/homolog based on `baseURL.includes("homol")`), unless `hideFooter`. trilhas-frontend:src/components/PageContainer/PageContainer.tsx:475-481 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- Blocks render entirely (`<LoadingAuth/>`) until `token && empresaAtual.id && !loading` — i.e. **auth/empresa gating happens client-side inside the layout component**, not purely via SSR redirect (SSR only checks the cookie exists, see §6.1). trilhas-frontend:src/components/PageContainer/PageContainer.tsx:227,483-485 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 2.2 Drawer-in-drawer as the primary "detail view" pattern
There is no client-side modal-routing or nested-route pattern for secondary views; instead the codebase nests antd `Drawer`s (via `DrawerBuilder`) up to **two levels deep** from a single page. Example: `OcupacoesPage` opens a chat `DrawerBuilder` (placement right), and *inside* that drawer conditionally renders a second `DrawerBuilder` for `TabRecomendacoes` (the bed's clinical tabs). trilhas-frontend:src/pages/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]/setor/[id_setor].tsx:228-290 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. `ListOcupacoes` similarly stacks 4 independent `DrawerBuilder`s (filter, recomendações, add-movimentação, add/remove paciente) off one list screen. trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:489-690 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

`DrawerBuilder` (`components/DrawerBuilder`) is the shared primitive: wraps antd `Drawer`, forces `closable={false}` on the native X (replaced with a custom link-button X), auto-sizes `width` to `"95vw"` below `collapseRule` else `"50vw"`, and standardizes a footer with Save/Close `Button`s (`shape="round"`, ghost primary + default) driven by `hideOk/hideClose/hidefooter/disableOkButton/extraButton` props. 16 call sites outside its own folder. trilhas-frontend:src/components/DrawerBuilder/DrawerBuilder.tsx:1-99 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 2.3 Card/list wrapper primitives
| Component | Purpose | Notes |
|---|---|---|
| `DefaultCardWrapper` | antd `Card` with fixed classes `"main-card with-pagination responsive"`, `bordered=false` default | 4 usages — thinner adoption than `PageContainer`/`DrawerBuilder`. trilhas-frontend:src/components/DefaultCardWrapper/DefaultCardWrapper.tsx:1-25 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `MobileCardWrapper` | Light/dark-aware card div with optional `Typography.Title` | **0 usages found anywhere in `src`** — dead code. trilhas-frontend:src/components/MobileCardWrapper/MobileCardWrapper.tsx:1-21 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `ItemDefault` | Generic clickable list row: icon + title + description + children, `isLight`-aware, optional entrance animation | 10 usages. trilhas-frontend:src/components/ItemDefault/ItemDefault.tsx:1-48 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `ListItem` | Minimal label/value row (`title` + children), `isLight`-aware | 5 usages. trilhas-frontend:src/components/ListItem/ListItem.tsx:1-33 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `Display` | Label/value "read view" field — renders a `Tag` list if value is an array, else plain text; returns `<></>` if falsy | memoized; used across read-only clinical detail views. trilhas-frontend:src/components/Display/Display.tsx:1-60 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `DisplayCard` | Big clickable menu-tile card (icon + title) used for empresa/estabelecimento choice screens | trilhas-frontend:src/components/DisplayCard/DisplayCard.tsx:1-27 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `SkeletonList` | N `Skeleton.Button` rows as a loading placeholder, or an `Empty` state if `errorMessage` is passed | Used as the loading/error state for most paginated grids. trilhas-frontend:src/components/SkeletonList/SkeletonList.tsx:1-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `FadeLoading` | Full-section spinner overlay (`mdiLoading` + optional message), `dark` variant | trilhas-frontend:src/components/FadeLoading/FadeLoading.tsx:1-22 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `AlertDelete` | Standard "danger banner + Popconfirm delete button" | trilhas-frontend:src/components/AlertDelete/AlertDelete.tsx:1-48 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `RenderTagTable` | Renders a table cell as either a colored left-border title or a colored pill `Tag`, color passed in as a raw hex/CSS-var string | Reused across every `Columns*Table.tsx` column-definition file. trilhas-frontend:src/components/RenderTagTable/RenderTagTable.tsx:1-39 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |

---

## 3. Component Library Catalog (by category)

The repo has **117 top-level directories under `src/components`** (281 `.tsx` files, 126 co-located `.less` files) — one folder per component, each typically `ComponentName.tsx` + `ComponentName.less` + `index.tsx` barrel re-export. trilhas-frontend:src/components (directory listing) @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 3.1 Navigation / chrome primitives
| Component | Behavior (verified) | Adoption |
|---|---|---|
| `CircularMenu` | Floating-action-button that expands a vertical stack of `Tooltip`-labeled child buttons via `translate3d` CSS transforms; a `blur-background` overlay closes it on outside click; `collapsed` prop flips expansion direction | Used on the bed-list page (`OcupacoesPage`) for Filtrar/Expandir/Mensagens/Relatórios/Dashboard actions. trilhas-frontend:src/components/CircularMenu/CircularMenu.tsx:1-65 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/pages/.../setor/[id_setor].tsx:104-208 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `SideFixedButton` | A `Button` fixed at a caller-supplied `top` pixel offset with icon+label | **0 usages found outside its own folder** — dead code. trilhas-frontend:src/components/SideFixedButton/SideFixedButton.tsx:1-36 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `BottomDrawer` | A bare `div`-based slide-up panel (not antd `Drawer`) toggled by a `visible` class, fixed `height` | Exactly **1 usage**, inside `DrawerReacoes` (emoji-reaction picker). trilhas-frontend:src/components/BottomDrawer/BottomDrawer.tsx:1-37 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `Breadcrumbs` | Full antd `Breadcrumb` built from `router.asPath` segments, skipping 36-char (UUID-length) segments and capitalizing the rest | **0 usages anywhere in `src`** — dead code; the header instead shows a hand-built `Tag` trail (§2.1) | trilhas-frontend:src/components/Breadcrumbs/Breadcrumbs.tsx:1-58 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `CustomTabs` | Reimplementation of a tab bar (not antd `Tabs`): absolutely-positioned sliding underline `div`, manual `activeKey` state, per-tab width `100/n`% | 2 usages (`DrawerReacoes`, inconsistências page) — antd's own `Tabs` is used everywhere else (`TabRecomendacoes`, `ListOcupacoes`, etc.), so **two parallel tab implementations coexist**. trilhas-frontend:src/components/CustomTabs/CustomTabs.tsx:1-98 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `ItensMenuMobile` | 3 swap cards (Empresa/Estabelecimento/Setor) shown inside the mobile hamburger `Drawer`; clicking one calls `onSwicth(destiny)` to navigate up the hierarchy | Only rendered from `PageContainer`'s mobile drawer. trilhas-frontend:src/components/ItensMenuMobile/ItensMenuMobile.tsx:1-72 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `HeadTitlePage` | `next/head` wrapper for page `<title>`/meta | Present on nearly every page. |
| `SwitchThemeButton` | antd `Switch` bound to `useLightTheme` | §1.2 |
| `SelectEmpresaAtual` | Header company switcher | consumed only inside `PageContainer` |

### 3.2 Forms — static
Each domain entity has a dedicated `Form*` component (`FormLeito`, `FormSetor`, `FormGrupo`, `FormUsuario`, `FormEstabelecimento`, `FormEmpresa`, `FormEditGrupo`, `FormLogin`, `FormProntuario`) following one shape: receives an antd `FormInstance` from the parent (parent owns submit + drawer chrome via `DrawerBuilder`), renders `Form.Item`s with a shared `defaultFormRules` validator import, a `HeaderForm` title, and a `mode: "in_page" | "modal"` prop that toggles `disabled` state on fields (view vs. edit). trilhas-frontend:src/components/FormEstabelecimento/FormEstabelecimento.tsx:1-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 3.3 Forms — the dynamic clinical-form engine (`FormDadosProntuario`)
This is the single most structurally significant subsystem in the component tree. It renders **arbitrary, config-driven clinical documentation forms** rather than one hardcoded form per role:

- Entry point `FormDadosProntuario` takes a `dadosFormProntuario: Models.DadosFormDinamico[]` config array (not markup) plus `initialValues`, and supports a `nullStatus` mechanism that can null-out whole sub-objects/arrays on submit (`nullifyFields`) when a group's "annul" switch is off — used to represent "this clinical section doesn't apply to this patient." trilhas-frontend:src/components/FormDadosProntuario/FormDadosProntuario.tsx:1-111 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- `CollapsedFields` renders each config group as an antd `Collapse.Panel`, optionally with a per-group "annulável" `Switch` in the header, and recurses into either nested `subGroup`s (via `SubGroupHandle`) or a flat `campos` array (via `SelectCampoType`), or a fully custom injected `Fieldset` React component reference carried in the config itself. trilhas-frontend:src/components/FormDadosProntuario/CollapsedFields/CollapsedFields.tsx:1-139 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- `SelectCampoType` is the field-type dispatcher: `campo.type` ∈ `{string, select, interval, number, boolean, checkbox, data, list, masked, multicheck}`, each mapped to a dedicated `SubForm*` renderer (10 field-type components under `SubFormsDadosProntuario/`). trilhas-frontend:src/components/FormDadosProntuario/SubFormsDadosProntuario/SelectCampoType/SelectCampoType.tsx:1-176 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- **14 distinct config files** instantiate this engine for different clinical roles/screens: `dataFormEnfermagem`, `dataFormFisioterapeuta`, `dataFormFonoaudiologo`, `dataFormFormularioMedico`, `dataFormFarmaceutico`, `dataFormMusicoterapia`, `dataFormNutricionista`, `dataFormPsicologo`, `dataFormTecEnfermagem`, `dataFormPaciente`, `dataFormMovimentacao`, `dataFormRemovePaciente`, `dataFormIntercorrencia`, `dataFormBalancoHidrico`. trilhas-frontend:src/utils/dataForms (directory listing) @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- This engine is what backs the "Evolução" (clinical progress-note) menu per professional role (`useEvolucaoMenu`), the bed-side "add/remove/move patient" drawers in `ListOcupacoes`, and the read-only "último prontuário" tab in `TabRecomendacoes`. trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:565-690 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/components/TabRecomendacoes/TabRecomendacoes.tsx:339-346 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 3.4 Filters
10+ `Filter*` components (`FilterGestaoPacientes`, `FilterEstabelecimentos`, `FilterFormRelatorioEvolucao`, `FilterGrupos`, `FilterInconsistencias` (+ nested `FilterInconsistenciaAssinatura`), `FilterLeitos`, `FilterOcupacoes`, `FilterSetores`, `FilterUsuarios`, `FilterArquivos`) all follow the same shape: plain antd `Form` (`layout="vertical"`) with `onFilter`/`onClear` callbacks, rendered as the content of a `DrawerBuilder` opened from a header `Affix`-pinned filter button. Example: `FilterGestaoPacientes`. trilhas-frontend:src/components/FilterGestaoPacientes/FilterGestaoPacientes.tsx:1-68 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, wired in trilhas-frontend:src/components/GestaoPacienteContent/GestaoPacienteContent.tsx:205-239 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 3.5 Tables
Each list entity has a `Colum(n)s*Table.tsx` file exporting a plain `ColumnType<T>[]` array (not a component) with `responsive: ["xs"|"sm"]` per column (antd's built-in responsive-column feature) and cell renderers delegating to `RenderTagTable` for colored value display. Example: `ColumnsGestaoPacientesTable`. trilhas-frontend:src/components/ColumnsGestaoPacientesTable/ColumnsGestaoPacientesTable.tsx:1-59 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. `FooterPaginator` (antd `Pagination`) reads `page`/`paginator` from `PaginationContext` and calls its `paginate()` action — it cannot be used outside a `PaginationProvider`. trilhas-frontend:src/components/FooterPaginator/FooterPaginator.tsx:1-35 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 3.6 Clinical/domain-specific widgets (no generic antd equivalent)
| Component | What it renders | Key mechanic |
|---|---|---|
| `CollapseCard` (in `ListOcupacoes/`) | The ICU **bed card**: patient name/age/gender icon, occupied/empty state, `statusTrilha`-colored border + glow, `MicroIndicadores` icon row, per-"trilha" (care pathway) colored chips, camera/files/evolução action buttons | All coloring is **inline `style` objects computed from `statusTrilha`**, not CSS classes — see §1.4. trilhas-frontend:src/components/ListOcupacoes/CollapseCard/CollapseCard.tsx:1-690 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `MicroIndicadores` | Row of tooltipped icons: noradrenaline use, mechanical ventilation, sedation, hemodialysis, length-of-stay (days), expected mortality (%) | Pure presentational, `color` prop driven by caller's `statusTrilha` lookup. trilhas-frontend:src/components/MicroIndicadores/MicroIndicadores.tsx:1-90 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `TabRecomendacoes` | Per-bed tabbed panel: "Critérios" (nested left-tab-bar of care "trilhas" with alert-colored buttons, `Collapse` of recommendations, an "Assistido" (attended) checkbox gated by `can_assist_ocupacao` permission and by which user already checked it) + "Último prontuário" (read-only `FormDadosProntuario`) | Custom `renderTabBar` replaces antd's default tab strip with hand-styled buttons colored via `statusTrilha`. trilhas-frontend:src/components/TabRecomendacoes/TabRecomendacoes.tsx:1-353 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `TrilhaInterativa` | Accept/Refuse workflow for a clinical protocol (named check: `trilha.nome === "Sepse" \|\| "Profilaxia"`), posts acceptance or a refusal reason via `useModalSender`-style `Modal.info` form, links out to a full protocol page | Domain logic (protocol name string match) lives in the component, not in config. trilhas-frontend:src/components/TrilhaInterativa/TrilhaInterativa.tsx:1-245 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `Prescricao` / `HorarioCheck` | Medication administration list: one row per scheduled dose time (`horario`), each independently checkable/editable/deletable via `onOk({body, horarioId})` | trilhas-frontend:src/components/Prescricao/Prescricao.tsx:1-149 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `BalancoHidricoContent`/`BalancoHidricoVisaoGeral` | Fluid-balance (intake/output) entry and an hourly grid overview | See §5.1 for its explicit responsive split. |
| `ProtocoloSepseContent` | Sepsis protocol checklist items | |
| `DisplayVideoUti` | ICU bed camera feed embedded via `<iframe src={cameraURL}...>` pointing at a **separate camera microservice** (`NEXT_PUBLIC_CAMERA_URL`, `/api/v2/...`), with a client-side "blur" privacy toggle button | Not a native video element/WebRTC player — camera streaming is entirely delegated to another service via iframe embed. trilhas-frontend:src/components/DisplayVideoUti/DisplayVideoUti.tsx:1-71 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `BuildVideoChat` / `VideoCall` | Agora RTC telemedicine call UI, shows "who's online" list sourced from a Firestore collection | See §6.4 |
| `MessagesList` / `MessageBallon` / `ChatSenderFooter` / `DrawerReacoes` | Setor (ward) chat: paginated REST message history + Firestore-signaled refresh | See §6.3 |
| `DisplayNotificaoes` / `ItemNotificacao` | Bell icon + drawer of push notifications | Raw WebSocket, not Firestore — see §6.5 |

### 3.7 Utility/infra components
`CheckPwa` (client-only PWA install prompt), `LoadingAuth` (full-screen auth-gate spinner), `FileB64Convert`/`PDFB64Convert`/`ImagePicker`/`FilePicker`/`FileGrid`/`FilesLeitoComponent` (file upload → base64 pipeline for the REST API, no direct-to-storage upload), `DownloadMultiple` (zips/downloads several files client-side), `CustomDatePicker`/`CustomSwitch` (thin antd wrappers standardizing default props), `HeaderForm` (title bar used inside every form/drawer).

---

## 4. Route Map & Information Architecture

**27 routed page files** under `src/pages` (excluding `_app`/`_document`/`404`), all under a single nested dynaminc-segment hierarchy rooted at `/empresa/[id_empresa]/...`. Verified via full directory listing. trilhas-frontend:src/pages (directory listing) @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

```
/                                                                     Login (FormLogin)                       — src/pages/index.tsx
/empresa                                                              Escolher empresa (company picker)        — src/pages/empresa/index.tsx
/empresa/[id_empresa]                                                 Estabelecimentos dashboard (ListDashboard)— .../[id_empresa].tsx
/empresa/[id_empresa]/feed                                            Home-care social feed                    — .../feed/index.tsx
/empresa/[id_empresa]/relatorio-evolucao                              Evolution/progress-note report builder   — .../relatorio-evolucao/index.tsx
/empresa/[id_empresa]/configuracoes                                   Settings menu (permission-filtered tiles) — .../configuracoes/index.tsx
  /configuracoes/empresa                                              Company data form
  /configuracoes/estabelecimentos                                     Establishments CRUD list
  /configuracoes/setores                                              Sectors/wards CRUD list
  /configuracoes/leitos                                                Beds CRUD list
  /configuracoes/grupos , /grupos/[id_grupo]                          Access-group CRUD + detail (users/sectors manager)
  /configuracoes/profissionais , /profissionais/[id_profissional]     Users CRUD + detail (incl. patient-assignment mgmt)
/empresa/[id_empresa]/estabelecimento/[id_estabelecimento]            Sectors ("setores") list for one establishment
  /chats                                                               Sector chat directory
  /chats/[id_setor]/[id_usuario]                                       1:1 video-call page (Agora)
  /setor/[id_setor]                                                    ★ ICU bed board (ListOcupacoes) — the core screen
    /auditoria , /auditoria/[id_ocupacao]                              Audit trail list + detail
    /cameras                                                           Sector camera grid
    /dashboard                                                         Sector KPI dashboard (charts)
    /inconsistencias                                                   Data-quality "inconsistências" report + signature sub-report
    /leito/[id_leito]/ocupacao/[id_ocupacao]                           Bed camera/video page (DisplayVideoUti)
      /balanco                                                        Fluid balance (BalancoHidricoContent)
      /prescricao                                                     Medication administration (Prescricao)
      /sepse/[id_trilha]                                               Sepsis protocol detail page
```
Route list assembled from: trilhas-frontend:src/pages/**/*.tsx (find listing) @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 4.1 Navigation model
There is **no persistent left/side nav menu** and no antd `Menu` component driving primary navigation. Navigation is entirely:
1. **Drill-down via tile grids** — `DisplayCard`/`ListDashboard` cards (empresa → estabelecimento) and `ItemDefault`/`ListItem` rows (settings tiles), each an `onClick` → `router.push`.
2. **Header company/context switcher** (`SelectEmpresaAtual`, `ItensMenuMobile`) for jumping between empresa/estabelecimento/setor without going back down the tile hierarchy. trilhas-frontend:src/components/ItensMenuMobile/ItensMenuMobile.tsx:1-72 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
3. **`CircularMenu` FAB** for page-level actions on the bed board (filter/expand/chat/reports/dashboard). §3.1
4. A hand-built **`Tag` trail** in the header (estabelecimento name, setor name), each tag clickable to jump back to that level — functions as a breadcrumb but is bespoke, not the `Breadcrumbs` component (which is dead code, §3.1). trilhas-frontend:src/components/PageContainer/PageContainer.tsx:330-357 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
5. **Menu-driven settings**: `useMenuByPermissions` builds the configuracoes tile list purely from boolean permission flags (`can_manage_empresa`, `can_manage_grupo_acesso`, `can_manage_usuario`), each entry a `{route, nome, image}` tuple consumed by `ListConfiguracoes`. trilhas-frontend:src/hooks/useMenuByPermissions.tsx:1-111 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 4.2 Tabs as sub-navigation
Two different tab implementations are both in active use (see §3.1 `CustomTabs` finding): antd `Tabs` for `TabRecomendacoes` ("Critérios"/"Último prontuário") and for the add-movement drawer's date-history tabs in `ListOcupacoes`, vs. the bespoke `CustomTabs` for the reactions drawer and the inconsistências page.

### 4.3 Auth gating of routes
Every page exports `getServerSideProps` calling `validateRoute(ctx)(callback)`, which reads the `trilhas.token`/`trilhas.permissions`/`theme.light` cookies via `nookies`, and redirects to `/` if no token (permission checks are opt-in via an `ignorePermission` flag that defaults to `true`, i.e. **route-level permission enforcement is off by default** and must be explicitly requested per page — no page in the repo was observed passing `ignorePermission=false`). trilhas-frontend:src/hocs/validateRoute.ts:1-38 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. Actual feature-level gating happens client-side via `useEffectivePermissions()` flags controlling button/menu visibility (e.g. `can_assist_ocupacao`, `can_manage_prescricao`, `can_add_movimentacao`). trilhas-frontend:src/hooks/useEffectivePermissions.tsx:1-28 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

---

## 5. Responsive Strategy

### 5.1 Two competing strategies, both present
**(A) Single-tree, class-toggling (dominant pattern, ~42 files):** `useWindowSize()` (a raw `resize` listener returning `[width, height]`) is read, then `collapsed = width < collapseRule` (1260 px) — occasionally `collapseRuleMobile` (800 px) for a second, tighter breakpoint — is computed with `useMemo` and used to (a) toggle a `"collapsed"`/`"mobile"` CSS class, and/or (b) branch small pieces of JSX/inline style (column widths, icon sizes, drawer width). This is the pattern in `PageContainer`, `DrawerBuilder`, `GestaoPacienteContent`, `TabRecomendacoes`, `CollapseCard`, `OcupacoesPage`, etc. — **49 files import `useWindowSize`, 42 reference `collapseRule`**. trilhas-frontend:src/hooks/useWindowSize.tsx:1-15 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/utils/constants.ts:5-6 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b (breakpoint constants), counts from repo-wide grep of `src/**/*.tsx`.

**(B) Fully separate component trees (rare, 1 confirmed instance):** `BalancoHidricoVisaoGeral` renders either `<GridView>` or `<MobileView>` — two entirely separate component files with their own `.less`, not a shared component with responsive classes — selected by the same `collapsed` boolean. trilhas-frontend:src/components/BalancoHidricoVisaoGeral/BalancoHidricoVisaoGeral.tsx:1-55 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. `GridView` lays out an hour×patient CSS grid; `MobileView` lays out the same data as stacked cards per hour — genuinely different information density per breakpoint, which is presumably *why* it was forked rather than class-toggled. trilhas-frontend:src/components/BalancoHidricoVisaoGeral/GridView/GridView.tsx:1-107 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/components/BalancoHidricoVisaoGeral/MobileView/MobileView.tsx:1-85 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

**(C) Ad hoc numeric breakpoints, independent of both of the above:** `ListOcupacoes` computes an antd `Col` `span` (out of 24) via a **5-bucket manual `if` chain over raw `window.innerWidth`** (>2800→4, 1800–2400→6, 1260–1800→8, 800–1260→12, <800→24) that does not reuse `collapseRule`/`collapseRuleMobile` and does not use antd's `Grid` responsive props (`xs/sm/md/lg/xl/xxl`) at all. trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:420-437 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 5.2 No CSS container queries / design-system breakpoint tokens
All responsive logic is JS-computed from `window.innerWidth` (client-only; SSR renders the desktop tree first, then re-renders on mount) rather than CSS media queries reacting to layout — the few `@media` queries that do exist in `.less` files (e.g. `globals.less`'s `.content-wrapper` margin reset, `.empty-page-feedback` height) use yet another literal breakpoint (`1260px`, `768px`) hand-typed into the stylesheet rather than referencing `@variables.less`. trilhas-frontend:src/styles/globals.less:1-20 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/styles/globals.less:137-145 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

---

## 6. State Management & Data Flow

### 6.1 Auth (`AuthContext`)
- SSR: `validateRoute` (per-page `getServerSideProps`) only checks cookie presence (§4.3).
- Client: `AuthProvider` re-verifies the token against `/verify-token/` on every mount (`useMountEffect`), pulls `allPermissions` (`/permissions/all/` presumably) and, if a `refresh-token` round-trip fails, calls `logout()`. `signIn()` posts to `/login/`, sets the `trilhas.token` cookie (30-day maxAge), and redirects to `/empresa/{id}` directly if the user has exactly one company, else to the company picker. trilhas-frontend:src/contexts/AuthContext/AuthContext.tsx:1-193 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- Auth state (`user`, `permissions`, `empresaData`) is a **single global React Context**, not a query cache — every consumer re-renders on any change and there's no request de-duplication/staleness model (no react-query/SWR anywhere in `package.json`). trilhas-frontend:package.json:18-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 6.2 REST layer (`hooks/networking/*`)
19 files, one per resource (`empresas`, `estabelecimentos`, `setor`, `leito`, `ocupacao`, `usuario`, `mensagens`, `prescricao`, `balancoHidrico`, `inconsistencias`, `feed`, `dashboard`, `arquivos`, `grupos`, `indicadores`, `evolucao`, `permission`, `trilhaInterativaSepse`). Each exports small `useGetX/usePostX/usePatchX/useDeleteX` hooks that are just `useCallback`-memoized wrappers around a shared `api` axios instance (`utils/api.ts` → `getAPIClient()`), hitting a REST path built from `empresa/estabelecimento/setor` IDs. Example: `hooks/networking/setor.ts` (9 hooks over `/empresas/:id/.../setores/...`). trilhas-frontend:src/hooks/networking/setor.ts:1-181 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. **Every** call site wraps these in `try/catch` and funnels failures to the single shared `handleApiError()` util, which assumes a Django-REST-Framework-shaped error body (`error.errors: Record<string, string | string[] | NestedIssue[]>`) and renders it as an antd `Modal.error` with per-field `Tag`s. trilhas-frontend:src/utils/feedback/handleApiError.tsx:1-103 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 6.3 List/pagination state (`PaginationContext` factory)
`createPagination({cleanPage, defaultFilters})` is a **factory that manufactures a fresh Context+Provider pair per call site** (not a single shared context) — `ListOcupacoes` calls it once at module scope to build its own `PaginationProvider`/`PaginationContext` pair, wraps its inner component, and injects the resource's `useGetX` list function as the `request` prop. The provider owns `page`, `filters`, `paginator` (`limit`/`offset`) state and exposes `applyFilters`/`clearFilters`/`paginate`, auto-fetching on mount (`useMountEffect`). trilhas-frontend:src/contexts/PaginationContext/PaginationContext.tsx:1-133 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, instantiated at trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:46-51,695-717 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. `FooterPaginator` is the generic consumer (§3.5).

### 6.4 "Live" data is polling, not push, for the mission-critical bed board
Both the estabelecimento dashboard and the ICU bed board (`ListOcupacoes`) implement **client-side polling** gated by a shared `AutoReloadContext` (`update: boolean`, toggled by a header `Switch`) and a per-company configurable interval (`empresa.tempo_atualizacao`, in seconds): a `setInterval` re-runs the REST fetch (`_getEmpresaIndicadores` / `applyFilters`) every `tempo_atualizacao * 1000` ms while `update` is true, cleared on unmount or when toggled off. trilhas-frontend:src/contexts/AutoReloadContext/AutoReloadContext.tsx:1-22 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/pages/empresa/[id_empresa]/index.tsx:57-87 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/components/ListOcupacoes/ListOcupacoes.tsx:112-141 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b — i.e. **despite Firebase being a dependency, actual bed/vitals/alert state is never pushed over Firestore; it is REST-polled**, with the poll interval a per-tenant business setting rather than a fixed technical constant.

### 6.5 Firestore is used only as a lightweight signal/presence layer, never as the data source
Every Firestore access in the repo targets exactly one document shape, `chats/{setorId}/usuarios/{usuarioId}`, via the generic `useDocument`/`useCollection` hooks (`onSnapshot` wrappers around the Firestore v8 JS SDK). trilhas-frontend:src/hooks/Firestore/useDocument.tsx:1-40 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/hooks/Firestore/useCollection.tsx:1-76 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b. Concretely:
- `MessagesList` reads this doc purely to know **when to re-run the REST message fetch** and to zero an unread counter (`qtd_mensagens`) — **chat message history itself is paginated REST** (`getMensagensBySetor`), not a Firestore collection. trilhas-frontend:src/components/MessagesList/MessagesList.tsx:332-348 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- `OcupacoesPage`'s `CircularMenu` "Mensagens" badge reads `setorDoc.qtd_mensagens` from the same doc. trilhas-frontend:src/pages/.../setor/[id_setor].tsx:50-52,142-152 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- `useUpdateStatus`/`BuildVideoChat` write/read `online_call: boolean` on the same per-user doc, and `useCollection` filters `where("online_call","==",true)` across all users in the sector to show "who's in the call" for Agora video. trilhas-frontend:src/hooks/useUpdateStatus.ts:1-18 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b, trilhas-frontend:src/components/BuildVideoChat/BuildVideoChat.tsx:34-51 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b
- **No other Firestore collection/document path appears anywhere in the repo.** This is a deliberate but narrow "presence/signal" usage of Firestore, layered on top of a REST-of-record backend, rather than Firestore being the system of record for chat/collaboration data.

### 6.6 Push notifications are a third, independent real-time channel (raw WebSocket)
`DisplayNotificaoes` opens **two** raw `w3cwebsocket` connections (`websocket` npm package, not socket.io) directly to `${baseWsURL}notificacao/?token=...` — one for the in-app notification list, one (`&popover=true`) purely to trigger an antd `notification.open()` toast, debounced 2s (`lodash.debounce`) to avoid toast spam. Marking as read sends a JSON `{evento:"visualizar", visto:true, id}` message back over the same socket (i.e. **the socket is bidirectional and doubles as a mutation channel**, not just a stream). trilhas-frontend:src/components/DisplayNotificaoes/DisplayNotificaoes.tsx:1-133 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b — so the app has **three independent real-time mechanisms** (Firestore signaling for chat/presence, raw WebSocket for notifications, `setInterval` REST polling for bed/dashboard data) with no shared abstraction between them.

### 6.7 Video calling
`BuildVideoChat`/`VideoCall` use `agora-rtc-react`'s `createClient` against `agoraApiKey`/`agoraConfigs`, with Firestore-driven presence (§6.4) and a `useSendIndicator("entrada_videochamada")` REST call fired on join (an analytics/audit event, separate from the realtime layers). trilhas-frontend:src/components/BuildVideoChat/BuildVideoChat.tsx:1-155 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b

### 6.8 Miscellaneous lifecycle/util hooks
`useMountEffect`/`useUnmountEffect`/`useRerenderWrapper` (`hooks/Lifecycle`) are used pervasively as thin wrappers over `useEffect(fn, [])`/cleanup/force-remount-via-key, standardizing "run once on mount" and "force a subtree to refetch by remounting it" idioms across dozens of components (e.g. `RerenderWrapper` around `DisplayNotificaoes`, `ListOcupacoes`'s `CollapseCard`s, `PageContainer`).

---

## 7. Dead Code / Discrepancies Found

| Finding | Evidence |
|---|---|
| `Breadcrumbs` component fully implemented (antd `Breadcrumb`, UUID-aware path parsing) but **never imported anywhere** | grep across `src/**/*.tsx` for `Breadcrumbs` outside its own folder → 0 hits |
| `MobileCardWrapper` fully implemented, light/dark-aware, **never imported anywhere** | same method, 0 hits |
| `SideFixedButton` fully implemented, **never imported anywhere** | same method, 0 hits |
| `CustomTabs` (bespoke tab bar) coexists with antd `Tabs` used for the same UI purpose elsewhere, adopted in only 2 files | grep counts, §3.1/4.2 |
| PWA manifest still names the product **"teleUTI"**, not "Trilhas" | trilhas-frontend:public/manifest.json:1-3 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b — confirms a prior product rename that wasn't fully propagated |
| Design tokens duplicated verbatim between `src/styles/variables.less` and `next.config.js` (manual sync required, no single import) | trilhas-frontend:src/styles/variables.less:1-15 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b vs. trilhas-frontend:next.config.js:5-21 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| `statusTrilha` (the actual clinical semantic-color system) is typed `as any` and never expressed in the LESS token file — it lives entirely in a `.ts` object consumed via inline styles | trilhas-frontend:src/utils/statusTrilha.ts:1-45 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| Three independent real-time channels (Firestore doc signaling, raw WebSocket, `setInterval` REST polling) with no shared reconnect/backoff/error-handling abstraction | §6.4–6.6 |
| Route-level permission enforcement (`validateRoute`'s `ignorePermission` param) defaults to `true` (i.e. off) and no call site was found overriding it — all real enforcement is client-side UI gating | trilhas-frontend:src/hocs/validateRoute.ts:4-38 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |
| Theme switch (`useLightTheme`) requires a full `window.location.reload()` — not a live toggle | trilhas-frontend:src/hooks/useLightTheme.ts:12-18 @ f9656be2660ec2048ce6240b4ac418b7fe7d5a5b |

---

## 8. Candidate ADR Decisions

1. **Base theme is Ant Design "dark", with a hand-written "light" override stylesheet, switched via cookie + full page reload.**
   *Legacy rationale (evident):* fastest way to ship a dark-first clinical UI (reduces glare in dim ICU rooms) while still offering a light mode for admin/office contexts, without building a full dual-theme design token system.
   *Assessment:* Works but is fragile — every component must locally branch `isLight` and hardcode a second set of colors (no semantic tokens), and switching modes costs a full reload. New platform should adopt CSS-custom-property–based theming (single token set, two value maps) so components never branch, and mode switching is instant.

2. **Per-tenant runtime re-theming via a single brand hex color (`empresa.cor_primaria`) applied through `dynamic-antd-theme` + CSS variables.**
   *Legacy rationale:* multi-tenant white-labeling (each hospital/company keeps its own brand color) without server-side build-per-tenant.
   *Assessment:* Valid requirement to carry forward; the *mechanism* (client-side Less recompilation) is expensive/fragile — a token-based design system (CSS variables only, no Less recompilation) achieves the same white-labeling more cheaply and removes the FOUC/hardcoded-default-color bug noted in §1.3.

3. **A single un-typed, hand-authored 5-state clinical alert palette (`statusTrilha`) is the true "design system" for clinical severity, decoupled from the antd/LESS token file.**
   *Legacy rationale:* clinical alert coloring needed more shades per state (border/fill/light-fill/ball/ball-fill) than antd's status colors provide, and needed to be usable in inline styles for per-cell dynamic coloring in tables/cards.
   *Assessment:* This is a real, valuable domain concept (severity taxonomy: Neutro/Vermelho/Amarelo/Laranja/Assistido) worth promoting to a first-class, typed design token in the new platform — it is effectively the product's most important color system and should not remain an untyped implementation detail.

4. **No shared primary navigation (no side menu / `Menu` component); IA is drill-down tile grids + a header context switcher + a FAB (`CircularMenu`) for page actions.**
   *Legacy rationale:* the hierarchy (empresa → estabelecimento → setor → leito → ocupação) is deep and strictly nested, so drill-down tiles map naturally to it, and the header switcher lets users jump across siblings without re-drilling.
   *Assessment:* Reasonable for the strict hierarchy, but there is no persistent wayfinding beyond the header `Tag` trail — a real breadcrumb component was built (`Breadcrumbs`) but abandoned. New IA should decide deliberately between tile-drill-down vs. persistent sidebar nav, and if breadcrumbs are wanted, build one component and use it (don't duplicate ad hoc `Tag` trails per layout).

5. **Two tab implementations coexist (antd `Tabs` and a bespoke `CustomTabs`).**
   *Legacy rationale:* unclear/likely historical — `CustomTabs`'s sliding-underline visual may not have been achievable with the antd version in use at the time.
   *Assessment:* Consolidate on one tab primitive; if the sliding-underline visual is wanted, implement it once as a themed variant of the single tab component.

6. **Drawer-in-drawer (2 levels deep) is the standard pattern for secondary/tertiary views, instead of routed pages or a modal stack manager.**
   *Legacy rationale:* keeps context (the bed board / chat) visible/mounted behind the drawer; avoids full page navigations for frequent, short-lived tasks (view protocol tabs, add movement, filter).
   *Assessment:* Works, but there is no generic "stack of overlays" abstraction — each page hand-wires its own boolean `visible` states and close handlers for every drawer level. Consider a proper overlay/stack manager in the new platform so nesting depth, back-navigation (Esc/back button), and focus trapping are handled once.

7. **Config-driven dynamic clinical form engine (`FormDadosProntuario` + `dataForm*.ts` configs + typed field renderers) rather than one hardcoded form per clinical role.**
   *Legacy rationale:* ~14 different clinical roles/screens (nursing, physio, pharmacy, nutrition, psychology, music therapy, speech therapy, physician, patient intake/removal, movement, fluid balance, intercurrence) need overlapping-but-distinct structured documentation, with nested groups, nullable sections, and 10 field types.
   *Assessment:* This is a strong, reusable pattern and one of the most valuable pieces of IP in the legacy frontend — it should be preserved and modernized (stronger typing than the current `as any`-laden config, and ideally the config schema becomes shareable with the backend/FHIR-mapping layer) rather than re-hardcoded per form in the new platform.

8. **Real-time strategy is fragmented across three unrelated mechanisms with no shared abstraction: Firestore (presence/unread signaling only), raw WebSocket (push notifications, bidirectional), and `setInterval` REST polling at a per-tenant configurable interval (mission-critical bed board).**
   *Legacy rationale (evident):* each was bolted on when a specific feature needed it (chat unread badges → Firestore was already a dependency for something; notifications → a Django Channels-style WS endpoint; bed board → simplest-possible "just refetch periodically," configurable per hospital because network/device capability varies).
   *Assessment:* This is the single highest-leverage architectural decision to revisit. The bed board (the actual mission-critical, life-safety-adjacent view) is the *least* real-time of the three. New platform should pick one push mechanism (e.g. WebSocket/SSE or a single realtime DB) and use it consistently for anything that currently polls, especially clinical status.

9. **Firestore, where used, is deliberately kept out of the data-of-record path** (message history, patient data, bed status are all REST) **and restricted to ephemeral signaling** (unread counts, "online in call" presence).
   *Legacy rationale:* avoids dual-writing clinical/audit data to two databases; Firestore's realtime `onSnapshot` is only needed for cheap, throwaway UI signals.
   *Assessment:* Sound principle to keep (don't let a NoSQL realtime layer become a second source of truth for clinical data) even if the specific vendor changes.

10. **File uploads go through a base64-encode-then-POST pipeline (`FileB64Convert`, `ImagePicker`, `FilesPickContent`), not direct-to-object-storage signed uploads.**
    *Legacy rationale:* simplest integration with a single REST backend, no separate storage-service auth needed client-side.
    *Assessment:* Fine for small clinical attachments, but base64 inflates payload ~33% and routes binary data through the app server; revisit for large files (video, imaging) in the new platform.

11. **Camera video is not a first-party player — it's an `<iframe>` embed of a separate camera microservice (`NEXT_PUBLIC_CAMERA_URL`).**
    *Legacy rationale:* the ICU camera/monitoring system is a distinct service (likely different vendor/protocol, e.g. RTSP-to-HLS bridge) and iframing it was the fastest integration.
    *Assessment:* Acceptable as a service boundary; new platform should keep camera streaming as a separable service but consider a first-party player shell (consistent chrome, the existing "blur for privacy" toggle, error/reconnect states) rather than a bare iframe.

12. **A single centralized error-handling function (`handleApiError`) assumes a DRF-shaped validation-error body and renders every failure as an antd `Modal.error`, called individually from nearly every REST call site's `catch` block.**
    *Legacy rationale:* consistent user-facing error UX with minimal boilerplate per call site; matches the Django REST Framework backend's error shape.
    *Assessment:* Good instinct (one error-rendering surface) but implemented as manual repetition in every `catch` rather than centralized in the HTTP client (e.g. an axios interceptor) — worth centralizing further, and decoupling the UI (modal vs. toast) from the parsing of the backend's error shape so the frontend isn't coupled to DRF specifically.

13. **Route-level auth is cookie-presence-only in SSR (`validateRoute`); permission enforcement happens entirely client-side via UI-gating hooks (`useEffectivePermissions`).**
    *Legacy rationale:* permissions are numerous/fine-grained (booleans like `can_manage_prescricao`, `can_assist_ocupacao`, `can_add_movimentacao`, ...) and likely change per company; enforcing them all at the SSR/route level for every nested route would be heavy boilerplate given `validateRoute`'s per-page opt-in design.
    *Assessment:* Real authorization must still be enforced server-side (REST API), which the current design implicitly relies on — but the frontend pattern of defaulting `ignorePermission=true` on every observed call site means the SSR guard provides no defense-in-depth beyond "is logged in." New platform should make the safe default `false` (deny) and require explicit route permission declarations.

14. **Design tokens are duplicated by hand between `src/styles/variables.less` and `next.config.js`.**
    *Legacy rationale:* `next-plugin-antd-less`'s `modifyVars` needs a plain JS object at Next.js config time, which can't directly `@import` a `.less` file, so the values were copy-pasted.
    *Assessment:* Minor but real drift risk (already 15 values kept in sync by convention only); new platform's token pipeline should have one source of truth (e.g. JSON/YAML tokens transformed into both the CSS-in-JS/CSS-variable output and any build-time theme config).
