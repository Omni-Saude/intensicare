# PLANS.md — Integração Frontend-Backend IntensiCare (5 Gaps)
# Planejamento tático com milestones, gatekeepers e rollback plans
# ═══════════════════════════════════════════════════════════════

**Data:** 2026-07-09
**Baseline:** `lib/api.ts` = 17 funções exportadas, 427 linhas. 22/33 páginas mock.
**Meta:** 67+ funções. Zero mock. Breadcrumb integrado. RBAC granular. Tipos atualizados.

---

## ═══════ FASE 0 — RECON ═══════

- [x] Ler HANDOFF.md completo (765 linhas)
- [x] Ler lib/api.ts atual (17 funções, 427 linhas)
- [x] Ler app/layout.tsx atual (Breadcrumb ausente)
- [x] Ler FRONTEND_AUDIT.md (22 páginas mock, 5 gaps críticos)
- [x] Produzir PLANS.md ← ESTE ARQUIVO

**Gatekeeper FASE 0:** Nenhum — fase de leitura apenas.

---

## ═══════ FASE 1 — API Client P0 (TDD domains) ═══════

**Estratégia:** Edição direta (não subagentes) — mesmo arquivo, sequencial.
**Arquivo:** `lib/api.ts` (append no final)
**Gatekeeper:** `npx tsc --noEmit` + `grep -c 'export async function' lib/api.ts`

### M1.1 — Pathways (6 funções, +tipos) ⏱️ ~5min
- Arquivos: `lib/api.ts` (append)
- Código: HANDOFF.md §Grupo 1.1
- Tipos: PathwayInfo, PathwayState, PathwayCriterion, PatientPathway, PathwayCriteriaEval, PathwayProgress, PathwayListResponse, PatientPathwayListResponse
- Funções: fetchPathways, fetchPathway, fetchPatientPathways, enrollPatientInPathway, updatePathwayCriteria, fetchPathwayProgress
- Gatekeeper: `npx tsc --noEmit` + `grep -c 'export async function' lib/api.ts` ≥ 23
- Rollback: `git checkout lib/api.ts`

### M1.2 — Prescricao (6 funções, +tipos) ⏱️ ~5min
- Arquivos: `lib/api.ts` (append)
- Código: HANDOFF.md §Grupo 1.2
- Tipos: PrescriptionRecord, InteractionAlert, PrescriptionCreatePayload, PrescriptionUpdatePayload, StateTransitionPayload, StateMachineDefinition, PrescriptionListResponse
- Funções: fetchPrescriptions, createPrescription, fetchPrescription, updatePrescription, transitionPrescriptionState, fetchStateMachine
- Gatekeeper: `npx tsc --noEmit` + `grep -c 'export async function' lib/api.ts` ≥ 29
- Rollback: `git checkout lib/api.ts`

### M1.3 — Movimentacao (4 funções, +tipos) ⏱️ ~4min
- Arquivos: `lib/api.ts` (append)
- Código: HANDOFF.md §Grupo 1.3
- Tipos: PatientMovement, BedStatus, MovementListResponse, BedGridResponse
- Funções: fetchMovements, registerMovement, fetchBedGrid, updateBedStatus
- Gatekeeper: `npx tsc --noEmit` + `grep -c 'export async function' lib/api.ts` ≥ 33
- Rollback: `git checkout lib/api.ts`

### M1.4 — Formularios (3 funções, +tipos) ⏱️ ~3min
- Arquivos: `lib/api.ts` (append)
- Código: HANDOFF.md §Grupo 1.4
- Tipos: ClinicalFormType, ClinicalFormSubmission, ClinicalFormListResponse, PatientClinicalFormListResponse
- Funções: fetchClinicalFormTypes, fetchPatientClinicalForms, submitClinicalForm
- Gatekeeper: `npx tsc --noEmit` + `grep -c 'export async function' lib/api.ts` ≥ 36
- Rollback: `git checkout lib/api.ts`

### M1.5 — Evolucoes (3 funções, +tipos) ⏱️ ~3min
- Arquivos: `lib/api.ts` (append)
- Código: HANDOFF.md §Grupo 1.5
- Tipos: ClinicalEvolution, EvolutionListResponse
- Funções: fetchEvolucoes, createEvolucao, fetchEvolucao
- Gatekeeper: `npx tsc --noEmit` + `grep -c 'export async function' lib/api.ts` ≥ 39
- Rollback: `git checkout lib/api.ts`

---

## ═══════ FASE 2 — Páginas P0 (TDD domains) ═══════

**Estratégia:** 3 subagentes paralelos (Delegate task)
**Gatekeeper por página:** `grep -c 'mock\|simul\|MOCK' app/<page>/page.tsx` = 0

### M2.1 — Agente A: care-pathways/page.tsx ⏱️ ~10min
- Arquivo: `app/care-pathways/page.tsx`
- Endpoints: fetchPathways(), fetchPatientPathways(), enrollPatientInPathway()
- Padrão: useState(MOCK) → useState([]) + useEffect + loading/error
- Gatekeeper: grep mock = 0 + tsc --noEmit

### M2.2 — Agente B: prescription/page.tsx ⏱️ ~10min
- Arquivo: `app/prescription/page.tsx`
- Endpoints: fetchPrescriptions(), createPrescription(), transitionPrescriptionState()
- Padrão: useState(MOCK) → useState([]) + useEffect + loading/error
- Gatekeeper: grep mock = 0 + tsc --noEmit

### M2.3 — Agente C: patient-movement + clinical-forms ⏱️ ~15min
- Arquivos: `app/patient-movement/page.tsx`, `app/clinical-forms/page.tsx`
- Endpoints: fetchMovements(), fetchBedGrid(), registerMovement(), fetchClinicalFormTypes(), submitClinicalForm()
- Padrão: useState(MOCK) → useState([]) + useEffect + loading/error
- Gatekeeper: grep mock = 0 em ambos + tsc --noEmit

---

## ═══════ FASE 3 — Breadcrumb + RBAC + Tipos ═══════

**Estratégia:** Edição direta (arquivos diferentes, mas inter-relacionados, escopo pequeno).

### M3.1 — Breadcrumb no layout ⏱️ ~2min
- Arquivo: `app/layout.tsx`
- Mudança: `import Breadcrumb` + `<Breadcrumb />` acima do `{children}`
- Gatekeeper: `grep 'Breadcrumb' app/layout.tsx` mostra import + componente
- Rollback: `git checkout app/layout.tsx`

### M3.2 — Hook useRole + Componente RequireRole ⏱️ ~5min
- Arquivos NOVOS: `hooks/useRole.ts`, `components/RequireRole.tsx`
- Código: HANDOFF.md §GAP 4.1 e 4.2
- Gatekeeper: `ls -la hooks/useRole.ts components/RequireRole.tsx` + tsc --noEmit
- Rollback: `rm hooks/useRole.ts components/RequireRole.tsx`

### M3.3 — admin/users dropdown de roles ⏱️ ~10min
- Arquivo: `app/admin/users/page.tsx`
- Mudança: toggle is_admin → `<select>` com 7 roles + updateUserRole2()
- Gatekeeper: `grep 'updateUserRole2' app/admin/users/page.tsx` + tsc --noEmit
- Rollback: `git checkout app/admin/users/page.tsx`

### M3.4 — Tipos TypeScript (encounter_id + definition_version_id) ⏱️ ~5min
- Arquivo: `lib/api.ts`
- Mudanças:
  - PatientBedSummary + encounter_id
  - PatientDetailResponse + encounter_id
  - AlertInfo + definition_version_id
  - UserResponse role → ClinicalRole union
- Gatekeeper: `grep 'encounter_id' lib/api.ts` + `grep 'definition_version_id' lib/api.ts` + tsc --noEmit
- Rollback: `git checkout lib/api.ts`

---

## ═══════ FASE 4 — API Client P1+P2 ═══════

**Estratégia:** 3 subagentes paralelos (append em lib/api.ts — mas grupos diferentes, posições fixas)
**AVISO:** lib/api.ts é arquivo compartilhado. Usar SERIAL — cada agente edita seção fixa.

### M4.1 — Grupo 1.6: Domínios Clínicos (18 funções) ⏱️ ~10min
- Arquivos: `lib/api.ts` (append seção ventilacao+stability+sedacao+deterioration+antimicrobial+prophylaxis+efficiency+indicators)
- Código: HANDOFF.md §Grupo 1.6
- Funções: fetchVentilation, fetchVentilationHistory, fetchStability, fetchStabilityTrend, fetchSedation, fetchSedationHistory, fetchDeterioration, fetchDeteriorationHistory, fetchAntimicrobialAssessments, createAntimicrobialAssessment, fetchAntimicrobialAssessment, fetchAntimicrobialCriteria, fetchProphylaxisBundles, fetchProphylaxisBundle, updateProphylaxisBundle, fetchProphylaxisBundleCriteria, fetchEfficiency, fetchIndicators, fetchIndicatorsSummary, fetchIndicator
- Gatekeeper: `grep -c 'export async function' lib/api.ts` ≥ 57

### M4.2 — Grupo 1.7: Admin + Infra (14 funções) ⏱️ ~8min
- Arquivos: `lib/api.ts` (append seção documentacao+alert_routing+registry)
- Código: HANDOFF.md §Grupo 1.7
- Funções: fetchDocumentacao, createDocumentacao, fetchAlertRoutingRules, createAlertRoutingRule, fetchAlertRoutingRule, updateAlertRoutingRule, deleteAlertRoutingRule, fetchEmpresas, createEmpresa, fetchEmpresa, updateEmpresa, deleteEmpresa, fetchEstabelecimentos
- Gatekeeper: `grep -c 'export async function' lib/api.ts` ≥ 67

---

## ═══════ FASE 5 — Páginas P1+P2 ═══════

**Estratégia:** Batches de 3 subagentes paralelos (páginas distintas).

### M5.1 — Batch 1 (P1 clínicas) ⏱️ ~15min
| Agente | Páginas | Endpoints |
|--------|---------|-----------|
| Agente D | `clinical-notes/page.tsx` | fetchEvolucoes, createEvolucao |
| Agente E | `ventilation/page.tsx`, `stability/page.tsx` | fetchVentilation, fetchStability |
| Agente F | `sedation/page.tsx`, `clinical-deterioration/page.tsx` | fetchSedation, fetchDeterioration |

### M5.2 — Batch 2 (P1 stewardship) ⏱️ ~15min
| Agente G | `antimicrobial-stewardship/page.tsx` | fetchAntimicrobialAssessments, createAntimicrobialAssessment |
| Agente H | `prophylaxis-bundles/page.tsx` | fetchProphylaxisBundles, updateProphylaxisBundle |
| Agente I | `nutrition/page.tsx`, `fluid-balance/page.tsx` | fetchEfficiency, fluid-balance endpoint |

### M5.3 — Batch 3 (P2) ⏱️ ~15min
| Agente J | `indicators/page.tsx`, `efficiency/page.tsx` | fetchIndicators, fetchEfficiency |
| Agente K | `documentation/page.tsx`, `alert-routing/page.tsx` | fetchDocumentacao, fetchAlertRoutingRules |
| Agente L | `handoff/page.tsx`, `communication/page.tsx` | handoff endpoint, communication endpoint |

### M5.4 — Batch 4 (P2 admin) ⏱️ ~15min
| Agente M | `admin/registry/page.tsx` | fetchEmpresas, createEmpresa |
| Agente N | `admin/tenancy/page.tsx`, `admin/audit-log/page.tsx` | tenancy endpoint, audit-log endpoint |

---

## ═══════ FASE 6 — Verificação Final ═══════

- [ ] `npx tsc --noEmit` → zero erros
- [ ] `npm run build` → build sucesso
- [ ] `grep -c 'export async function' lib/api.ts` ≥ 67
- [ ] `grep -rl 'mock\|simul\|Simul\|MOCK' app/ --include='*.tsx' | wc -l` = 0
- [ ] `grep 'Breadcrumb' app/layout.tsx` → import + `<Breadcrumb />`
- [ ] `ls -la hooks/useRole.ts components/RequireRole.tsx` → ambos existem
- [ ] `grep 'encounter_id' lib/api.ts` → definições presentes
- [ ] `grep 'updateUserRole2' app/admin/users/page.tsx` → chamada com role string

---

## ═══════ DEPENDENCY GRAPH ═══════

```
FASE 1 (API P0)
  └── FASE 2 (Páginas P0) [depende de FASE 1 completa]
        └── FASE 3 (Breadcrumb+RBAC+Tipos) [independente, roda em paralelo com FASE 2? NÃO — lib/api.ts conflito]
              └── FASE 4 (API P1+P2) [depende de FASE 3.4 (tipos) liberar lib/api.ts]
                    └── FASE 5 (Páginas P1+P2) [depende de FASE 4]
                          └── FASE 6 (Verificação Final)
```

**ORDEM REAL:**
1. FASE 1 → 2 → 3 executadas serialmente (todas tocam lib/api.ts em algum momento)
2. Mas FASE 3 (M3.1, M3.2, M3.3) pode rodar em paralelo COM FASE 2 se M3.4 ficar por último
3. FASE 4 → FASE 5 → FASE 6

**Simplificação:** Vou executar FASE 1 primeiro, depois FASE 2 em paralelo com M3.1+M3.2+M3.3 (que não tocam lib/api.ts), depois M3.4, depois FASE 4, depois FASE 5, depois FASE 6.
