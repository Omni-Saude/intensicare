# Phase 0 — Legacy Codebase Inventory & Audit Partition Map

Audit of the two legacy IntensiCare repositories, run 2026-07-03.

## Audited snapshots

| Repo | Default branch | Commit SHA | Files | Stack |
|---|---|---|---|---|
| `Dev-Infra-Grupo-AMH/ahlabs-trilhas` | `master` | `8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f` | 608 (519 `.py`) | Django + DRF, uWSGI, Docker |
| `Dev-Infra-Grupo-AMH/trilhas-frontend` | `master` | `f9656be2660ec2048ce6240b4ac418b7fe7d5a5b` | 681 (331 `.tsx`, 133 `.ts`, 22 `.jsx`, 153 `.less`) | Next.js + TypeScript, Ant Design, Firebase/Firestore, Agora video |

All source citations in this audit are of the form `repo:path:line-range` at the SHAs above.
Full per-file inventories (line counts; `binary` for non-text): [inventory/ahlabs-trilhas.tsv](inventory/ahlabs-trilhas.tsv), [inventory/trilhas-frontend.tsv](inventory/trilhas-frontend.tsv).

## Backend structure (`ahlabs-trilhas`)

Django project `trilhas` with four apps plus shared utilities (LOC = lines in tracked text files):

| Area | LOC | Candidate rule content |
|---|---|---|
| `trilha_homecare/` | 19,619 | Homecare product: per-discipline clinical assessment forms (`models/formularios/`, `models/formularios/avaliacoes/`), fluid balance (`models/balanco_hidrico/`), clinical choice enums (`models/choices/`), 42 serializers + 24 views with embedded validation |
| `trilha_automatica/` | ~9,700 | Automated ICU care pathways: `models/` incl. `trilhas_v3/`, ETL indicator engine (`etl/trilha1..9.py`, `microindicadores.py`, `macroindicadores.py`, `indicadores.py`), Tasy EHR integration (`models_tasy/`), `trilha_schema/`, Celery `tasks/` |
| `core/` | ~7,700 | Facades for 13+ care pathways (`facade/`: sepse, sepse_v3, ventilacao, sedacao, nutricao, profilaxia, profilaxia_v3, antimicrobiano, eficiencia, equilibrio, estabilidade, estabilizacao, glosa_zero, piora_clinica, movimentacao), `use_cases/validators/`, domain models, API |
| `trilha_manual/` | 4,308 | Manual care-pathway product: models, facade, serializers, tests |
| `utils/` | 2,408 | Shared helpers incl. `composite/` — likely calculation/formatting helpers |
| `trilhas/` (project) | 621 | Settings, celery config, routing |
| Other | small | `templates/` (24 LOC), `static/`, `geoip/`, `uwsgi/`, Docker, 5 migration files |

## Frontend structure (`trilhas-frontend`)

| Area | LOC | Candidate rule content |
|---|---|---|
| `src/components/` | 18,037 | Clinical UI with embedded logic: `ProtocoloSepseContent`, `BalancoHidrico*` (4 dirs + `ColumnsBalancoHidrico`), `Prescricao*`, `FormDadosProntuario`, `TrilhaInterativa`, `TabRecomendacoes`, `ListOcupacoes`, dashboards, reports |
| `src/utils/` | 7,837 | `dataForms/` (14 per-discipline form definitions), `defaultFormRules.ts`, `emailFormRules.ts`, `constants.ts`, converters (`convertBalancoData.ts`), choice lists (`cargos.ts`, `choicesConselho.ts`, `localLesoes.ts`), date/turn logic (`dateTurn.ts`) |
| `src/pages/` | 5,286 | Next.js routes; page-level logic and guards |
| `src/hooks/` | 3,492 | `networking/` (API layer), `Firestore/`, `Search/`, `Lifecycle/` |
| `src/@types/` | 1,293 | Model type definitions (25 files) — encode expected shapes/enums |
| `src/contexts/`, `src/hocs/`, `appConfig.js` | ~400 | Auth/permission gating candidates |
| `src/themes/`, `src/styles/` | — | `LightTheme.less/tsx`, `variables.less`, `globals.less` — design tokens (Phase 5) |

## Phase 1 extraction partitions

Backend (repo `ahlabs-trilhas`, commit `8166c07e`):

| ID | Scope | ~LOC |
|---|---|---|
| BE-01 | `core/facade/`, `trilha_automatica/facade/`, `trilha_automatica/trilha_schema/`, `trilha_automatica/tasks/` | 2,200 |
| BE-02 | `trilha_automatica/etl/`, `trilha_automatica/models_tasy/`, `trilha_automatica/api/` | 1,700 |
| BE-03 | `trilha_automatica/models/` (incl. `trilhas_v3/`) | 7,400 |
| BE-04 | `core/models/`, `core/use_cases/`, `core/filters/`, `core/mixins/` | 3,300 |
| BE-05 | `core/api/` | 4,400 |
| BE-06 | `trilha_homecare/models/` (formularios, avaliacoes, balanco_hidrico, choices) | 5,400 |
| BE-07 | `trilha_homecare/api/v1/serializers/` | ~5,000 |
| BE-08 | `trilha_homecare/api/` excl. serializers (views, filters, urls) | ~4,100 |
| BE-09 | `trilha_homecare/` root files + `templatetags/` | 5,100 |
| BE-10 | `trilha_manual/` | 4,300 |
| BE-11 | `utils/`, `trilhas/` (settings), `templates/`, `static/`, migrations, Docker/config | 3,100 |

Frontend (repo `trilhas-frontend`, commit `f9656be2`):

| ID | Scope | ~LOC |
|---|---|---|
| FE-01 | `src/utils/dataForms/`, `src/utils/defaultFormRules.ts`, `src/utils/emailFormRules.ts` | ~2,500 |
| FE-02 | `src/utils/` remainder | ~5,300 |
| FE-03 | Clinical components A: `BalancoHidrico*`, `ColumnsBalancoHidrico`, `ProtocoloSepseContent`, `TrilhaInterativa`, `TabRecomendacoes` | 2,300 |
| FE-04 | Clinical components B: `Prescricao*`, `Prescricoes`, `FormDadosProntuario`, `HistoricoEvolucao`, `EvolucaoDefault*`, `FieldsetAvGlobalNutricionista` | 4,000 |
| FE-05 | Remaining `src/components/` A–F | ~5,500 |
| FE-06 | Remaining `src/components/` G–Z + `src/icons/` configs | ~6,000 |
| FE-07 | `src/hooks/`, `src/contexts/`, `src/@types/`, `appConfig.js` | 5,200 |
| FE-08 | `src/pages/`, `src/hocs/` | 5,500 |

Phase 5 design-audit track (repo `trilhas-frontend`): D-01 tokens/theme, D-02 component library + IA/navigation, D-03 clinical UX patterns (alert severity, critical-value highlighting, data density).

## Explicitly out of scope (non-rule-bearing)

Binary assets (fonts, images, `.mmdb` GeoIP databases), `yarn.lock`, generated Next.js type stubs, uWSGI/Docker infra config (checked for embedded constants in BE-11), log files.

## Method notes

- Legacy repos were cloned read-only into an isolated scratchpad; no writes or pushes.
- File names, folder structure, and comments are treated as unreliable; every rule is derived from code behavior (Phase 1 ground rule).
- Coverage of every file — including "no rules found" verdicts per file — is recorded per partition and re-checked in Phase 6.
