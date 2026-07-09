HANDOFF PACKAGE — Ive (Design-to-Code Orchestrator)
═══════════════════════════════════════════════════════════════
Target: 100% Frontend-Backend Integration dos 5 Gaps Críticos
═══════════════════════════════════════════════════════════════

## ═══════ ENVELOPE ═══════

Goal:        Conectar o frontend-v2 ao backend real, eliminando 100% dos dados mock e integrando todos os componentes novos.
Context:     Backend tem 30 gaps fechados (pós gap-closure 2026-07-09). Frontend está 67% mockado. 22/33 páginas usam dados falsos.
Constraints: Todos os endpoints existem. Todos os contratos OpenAPI existem. NÃO modificar backend. Somente TypeScript/React.
Done When:   22 páginas mock → API real. Breadcrumb integrado. RBAC granular funcionando. Tipos atualizados. npm run build passa.
Risk:        MEDIUM — frontend-only, sem risco de regressão no backend.
Scope:       frontend-v2/lib/api.ts, frontend-v2/app/*/page.tsx, frontend-v2/components/, frontend-v2/app/layout.tsx

## ═══════ CONTEXT ═══════

### O que aconteceu antes (Niemeyer + Parreira)

1. Niemeyer auditou a plataforma → 38 gaps encontrados
2. Niemeyer ratificou 29 ADRs (governança completa)
3. Parreira fechou 30 gaps no backend (data model, segurança, contratos, YAMLs)
4. Niemeyer auditou o frontend → **5 gaps críticos encontrados** (FRONTEND_AUDIT.md)

### Baseline reports (LEIA antes de agir)

- `/Users/familia/intensicare/docs/audit/FRONTEND_AUDIT.md` — Auditoria completa do frontend
- `/Users/familia/intensicare/docs/audit/FORENSICS_SYNTHESIS.md` — Síntese Niemeyer+Parreira
- `/Users/familia/intensicare/docs/contracts/` — 15 contratos OpenAPI 3.1.0

### Estado atual do frontend

- 33 páginas no total
- 11 páginas com API real (dashboard, alerts, patient detail, admin, login)
- 22 páginas com dados mock (67%)
- 3 componentes novos criados pelo Parreira (Breadcrumb, OverlayStack, TenantProvider)
- Apenas Breadcrumb NÃO está integrado ao layout

---

## ═══════ GAP 1: API Client (`lib/api.ts`) — 50 funções faltantes ═══════

### Backend endpoints × API client status

As funções abaixo DEVEM ser adicionadas a `/Users/familia/intensicare/frontend-v2/lib/api.ts`.
Cada grupo inclui: tipos TypeScript + função async + tratamento de erro (usa o `request<T>()` helper existente).

### Grupo 1.1 — Pathways (TDD, 6 endpoints) ⭐ P0

```typescript
// ── TYPES ──
export interface PathwayInfo {
  id: number;
  name: string;
  slug: string;
  description: string;
  active: boolean;
  definition_version_id?: string;  // NOVO: content-addressing SHA-256
  definition_hash?: string;
  states: PathwayState[];
  criteria: PathwayCriterion[];
  created_at: string;
}

export interface PathwayState {
  id: string;
  name: string;
  order: number;
  is_terminal?: boolean;
}

export interface PathwayCriterion {
  id: string;
  name: string;
  category: string;
  unit?: string;
  normal_range?: string;
  alert_threshold?: string;
}

export interface PatientPathway {
  id: number;
  mpi_id: string;
  encounter_id: string;          // NOVO (gap C4)
  bed_id?: string;                // NOVO
  unit?: string;                  // NOVO
  pathway: PathwayInfo;
  current_state_id: string;
  status: 'active' | 'completed' | 'archived';
  severity: 'normal' | 'watch' | 'urgent' | 'critical';
  criteria: PathwayCriteriaEval[];
  enrolled_at: string;
  completed_at?: string;
}

export interface PathwayCriteriaEval {
  criteria_id: string;
  met: boolean;
  value?: string;
  evaluated_at: string;
}

export interface PathwayProgress {
  patient_pathway_id: number;
  mpi_id: string;
  encounter_id: string;
  pathway_name: string;
  current_state: string;
  criteria_summary: { total: number; met: number; not_met: number; pending: number };
  state_history: { from_state: string; to_state: string; changed_at: string; reason: string }[];
  trend: string;
  recommendation: string;
}

export interface PathwayListResponse { pathways: PathwayInfo[]; }
export interface PatientPathwayListResponse { pathways: PatientPathway[]; }

// ── FUNCTIONS ──
export async function fetchPathways(): Promise<PathwayListResponse> {
  return request<PathwayListResponse>('/api/v1/pathways');
}
export async function fetchPathway(pathwayId: number): Promise<PathwayInfo> {
  return request<PathwayInfo>(`/api/v1/pathways/${pathwayId}`);
}
export async function fetchPatientPathways(mpiId: string): Promise<PatientPathwayListResponse> {
  return request<PatientPathwayListResponse>(`/api/v1/patients/${encodeURIComponent(mpiId)}/pathways`);
}
export async function enrollPatientInPathway(mpiId: string, pathwayId: number): Promise<PatientPathway> {
  return request<PatientPathway>(`/api/v1/patients/${encodeURIComponent(mpiId)}/pathways`, {
    method: 'POST',
    body: JSON.stringify({ pathway_definition_id: pathwayId }),
  });
}
export async function updatePathwayCriteria(mpiId: string, patientPathwayId: number, criteria: { criteria_id: string; met: boolean; value?: string }[]): Promise<PatientPathway> {
  return request<PatientPathway>(`/api/v1/patients/${encodeURIComponent(mpiId)}/pathways/${patientPathwayId}/criteria`, {
    method: 'PUT',
    body: JSON.stringify({ criteria }),
  });
}
export async function fetchPathwayProgress(mpiId: string, patientPathwayId: number): Promise<PathwayProgress> {
  return request<PathwayProgress>(`/api/v1/patients/${encodeURIComponent(mpiId)}/pathways/${patientPathwayId}/progress`);
}
```

### Grupo 1.2 — Prescricao (TDD, 6 endpoints) ⭐ P0

```typescript
// ── TYPES ──
export interface PrescriptionRecord {
  id: string;
  patient_id: string;
  medication_id: string;
  medication_name?: string;
  estado: 'draft' | 'active' | 'completed' | 'discontinued' | 'suspended';
  dose: number;
  dose_unit: string;
  via_administracao: string;
  frequencia: string;
  data_inicio: string;
  data_fim?: string;
  instrucoes?: string;
  versao: number;
  alertas?: InteractionAlert[];
  created_at: string;
  updated_at?: string;
}

export interface InteractionAlert {
  tipo: string;
  gravidade: 'contraindicated' | 'severe' | 'moderate' | 'minor';
  mecanismo: string;
  recomendacao: string;
  resolvido: boolean;
}

export interface PrescriptionCreatePayload {
  patient_id: string;
  medication_id: string;
  dose: number;
  dose_unit: string;
  via_administracao: string;
  frequencia: string;
  data_inicio: string;
  data_fim?: string;
  instrucoes?: string;
}

export interface PrescriptionUpdatePayload {
  dose?: number;
  dose_unit?: string;
  via_administracao?: string;
  frequencia?: string;
  data_fim?: string;
  instrucoes?: string;
}

export interface StateTransitionPayload {
  transition: 'activate' | 'complete' | 'discontinue' | 'suspend' | 'resume';
  reason?: string;
  co_signatario_id?: string;
}

export interface StateMachineDefinition {
  states: string[];
  transitions: { from: string; to: string; guard: string }[];
}

export interface PrescriptionListResponse { prescriptions: PrescriptionRecord[]; }

// ── FUNCTIONS ──
export async function fetchPrescriptions(mpiId: string): Promise<PrescriptionListResponse> {
  return request<PrescriptionListResponse>(`/api/v1/patients/${encodeURIComponent(mpiId)}/prescriptions`);
}
export async function createPrescription(mpiId: string, data: PrescriptionCreatePayload): Promise<PrescriptionRecord> {
  return request<PrescriptionRecord>(`/api/v1/patients/${encodeURIComponent(mpiId)}/prescriptions`, {
    method: 'POST', body: JSON.stringify(data),
  });
}
export async function fetchPrescription(prescriptionId: string): Promise<PrescriptionRecord> {
  return request<PrescriptionRecord>(`/api/v1/prescriptions/${prescriptionId}`);
}
export async function updatePrescription(prescriptionId: string, data: PrescriptionUpdatePayload, version: number): Promise<PrescriptionRecord> {
  return request<PrescriptionRecord>(`/api/v1/prescriptions/${prescriptionId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
    headers: { 'If-Match': String(version) },
  });
}
export async function transitionPrescriptionState(prescriptionId: string, data: StateTransitionPayload): Promise<PrescriptionRecord> {
  return request<PrescriptionRecord>(`/api/v1/prescriptions/${prescriptionId}/state`, {
    method: 'POST', body: JSON.stringify(data),
  });
}
export async function fetchStateMachine(): Promise<StateMachineDefinition> {
  return request<StateMachineDefinition>('/api/v1/prescriptions/state-machine');
}
```

### Grupo 1.3 — Movimentacao (TDD, 4 endpoints) ⭐ P0

```typescript
// ── TYPES ──
export interface PatientMovement {
  id: number;
  mpi_id: string;
  encounter_id?: string;
  type: 'admission' | 'transfer' | 'discharge';
  from_unit?: string;
  to_unit?: string;
  from_bed?: string;
  to_bed?: string;
  timestamp: string;
  notes?: string;
}

export interface BedStatus {
  bed_id: string;
  unit: string;
  room?: string;
  status: 'free' | 'occupied' | 'blocked' | 'cleaning';
  current_patient_mpi_id?: string;
  current_patient_name?: string;
  occupied_since?: string;
  last_cleaned_at?: string;
  notes?: string;
}

export interface MovementListResponse { movements: PatientMovement[]; }
export interface BedGridResponse { beds: BedStatus[]; }

// ── FUNCTIONS ──
export async function fetchMovements(mpiId: string): Promise<MovementListResponse> {
  return request<MovementListResponse>(`/api/v1/patients/${encodeURIComponent(mpiId)}/movements`);
}
export async function registerMovement(mpiId: string, data: Partial<PatientMovement>): Promise<PatientMovement> {
  return request<PatientMovement>(`/api/v1/patients/${encodeURIComponent(mpiId)}/movements`, {
    method: 'POST', body: JSON.stringify(data),
  });
}
export async function fetchBedGrid(): Promise<BedGridResponse> {
  return request<BedGridResponse>('/api/v1/beds');
}
export async function updateBedStatus(bedId: string, data: { status: string; notes?: string }): Promise<BedStatus> {
  return request<BedStatus>(`/api/v1/beds/${encodeURIComponent(bedId)}`, {
    method: 'PUT', body: JSON.stringify(data),
  });
}
```

### Grupo 1.4 — Formularios (TDD, 3 endpoints) ⭐ P0

```typescript
export interface ClinicalFormType {
  form_type: string;
  name: string;
  description: string;
  score_range?: { min: number; max: number };
  fields: { key: string; type: string; label: string; required: boolean }[];
}

export interface ClinicalFormSubmission {
  id: string;
  mpi_id: string;
  encounter_id: string;
  form_type: string;
  definition_version: string;
  data: Record<string, unknown>;
  score?: number;
  score_components?: Record<string, number>;
  created_at: string;
  created_by: string;
}

export interface ClinicalFormListResponse { forms: ClinicalFormType[]; }
export interface PatientClinicalFormListResponse { submissions: ClinicalFormSubmission[]; }

export async function fetchClinicalFormTypes(): Promise<ClinicalFormListResponse> {
  return request<ClinicalFormListResponse>('/api/v1/clinical-forms');
}
export async function fetchPatientClinicalForms(mpiId: string): Promise<PatientClinicalFormListResponse> {
  return request<PatientClinicalFormListResponse>(`/api/v1/patients/${encodeURIComponent(mpiId)}/clinical-forms`);
}
export async function submitClinicalForm(mpiId: string, data: { form_type: string; definition_version: string; data: Record<string, unknown>; notes?: string }): Promise<ClinicalFormSubmission> {
  return request<ClinicalFormSubmission>(`/api/v1/patients/${encodeURIComponent(mpiId)}/clinical-forms`, {
    method: 'POST', body: JSON.stringify(data),
  });
}
```

### Grupo 1.5 — Evolucoes (TDD, 3 endpoints) ⭐ P0

```typescript
export interface ClinicalEvolution {
  id: string;
  mpi_id: string;
  encounter_id: string;
  type: 'admissao' | 'diaria' | 'alta' | 'obito' | 'intercorrencia';
  role: string;
  content: string;
  structured_data: Record<string, unknown>;
  sofa_score?: number;
  bundles_confirmed?: string[];
  enrichment?: Record<string, unknown>;
  status: 'draft' | 'liberado' | 'assinado';
  content_hash: string;
  created_at: string;
  created_by: string;
}

export interface EvolutionListResponse { evolucoes: ClinicalEvolution[]; }

export async function fetchEvolucoes(mpiId: string, params?: { type?: string; offset?: number; limit?: number }): Promise<EvolutionListResponse> {
  const qs = new URLSearchParams();
  if (params?.type) qs.set('type', params.type);
  if (params?.offset) qs.set('offset', String(params.offset));
  if (params?.limit) qs.set('limit', String(params.limit));
  return request<EvolutionListResponse>(`/api/v1/patients/${encodeURIComponent(mpiId)}/evolucoes${qs.toString() ? '?' + qs : ''}`);
}
export async function createEvolucao(mpiId: string, data: { type: string; content: string; structured_data?: Record<string, unknown>; bundles_confirmed?: string[]; status?: string }): Promise<ClinicalEvolution> {
  return request<ClinicalEvolution>(`/api/v1/patients/${encodeURIComponent(mpiId)}/evolucoes`, {
    method: 'POST', body: JSON.stringify(data),
  });
}
export async function fetchEvolucao(evolutionId: string): Promise<ClinicalEvolution> {
  return request<ClinicalEvolution>(`/api/v1/evolucoes/${evolutionId}`);
}
```

### Grupo 1.6 — Domínios Clínicos (8 routers, 18 endpoints) ⭐ P1

```typescript
// ventilacao
export async function fetchVentilation(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/ventilation`); }
export async function fetchVentilationHistory(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/ventilation/history`); }

// stability
export async function fetchStability(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/stability`); }
export async function fetchStabilityTrend(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/stability/trend`); }

// sedacao
export async function fetchSedation(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/sedation`); }
export async function fetchSedationHistory(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/sedation/history`); }

// deterioration
export async function fetchDeterioration(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/deterioration`); }
export async function fetchDeteriorationHistory(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/deterioration/history`); }

// antimicrobial
export async function fetchAntimicrobialAssessments(): Promise<unknown> { return request('/api/v1/antimicrobial/assessments'); }
export async function createAntimicrobialAssessment(data: unknown): Promise<unknown> { return request('/api/v1/antimicrobial/assessments', { method: 'POST', body: JSON.stringify(data) }); }
export async function fetchAntimicrobialAssessment(id: string): Promise<unknown> { return request(`/api/v1/antimicrobial/assessments/${id}`); }
export async function fetchAntimicrobialCriteria(): Promise<unknown> { return request('/api/v1/antimicrobial/criteria'); }

// prophylaxis
export async function fetchProphylaxisBundles(): Promise<unknown> { return request('/api/v1/prophylaxis/bundles'); }
export async function fetchProphylaxisBundle(id: string): Promise<unknown> { return request(`/api/v1/prophylaxis/bundles/${id}`); }
export async function updateProphylaxisBundle(id: string, data: unknown): Promise<unknown> { return request(`/api/v1/prophylaxis/bundles/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
export async function fetchProphylaxisBundleCriteria(id: string): Promise<unknown> { return request(`/api/v1/prophylaxis/bundles/${id}/criteria`); }

// efficiency
export async function fetchEfficiency(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/efficiency`); }

// indicators
export async function fetchIndicators(): Promise<unknown> { return request('/api/v1/indicators'); }
export async function fetchIndicatorsSummary(): Promise<unknown> { return request('/api/v1/indicators/summary'); }
export async function fetchIndicator(id: string): Promise<unknown> { return request(`/api/v1/indicators/${id}`); }
```

### Grupo 1.7 — Admin + Infra (4 routers, 14 endpoints) ⭐ P2

```typescript
// documentacao
export async function fetchDocumentacao(mpiId: string): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/documentacao`); }
export async function createDocumentacao(mpiId: string, data: unknown): Promise<unknown> { return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/documentacao`, { method: 'POST', body: JSON.stringify(data) }); }

// alert_routing
export async function fetchAlertRoutingRules(): Promise<unknown> { return request('/api/v1/alert-routing'); }
export async function createAlertRoutingRule(data: unknown): Promise<unknown> { return request('/api/v1/alert-routing', { method: 'POST', body: JSON.stringify(data) }); }
export async function fetchAlertRoutingRule(id: string): Promise<unknown> { return request(`/api/v1/alert-routing/${id}`); }
export async function updateAlertRoutingRule(id: string, data: unknown): Promise<unknown> { return request(`/api/v1/alert-routing/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
export async function deleteAlertRoutingRule(id: string): Promise<void> { return request(`/api/v1/alert-routing/${id}`, { method: 'DELETE' }); }

// registry
export async function fetchEmpresas(): Promise<unknown> { return request('/api/v1/registry/empresas'); }
export async function createEmpresa(data: unknown): Promise<unknown> { return request('/api/v1/registry/empresas', { method: 'POST', body: JSON.stringify(data) }); }
export async function fetchEmpresa(id: string): Promise<unknown> { return request(`/api/v1/registry/empresas/${id}`); }
export async function updateEmpresa(id: string, data: unknown): Promise<unknown> { return request(`/api/v1/registry/empresas/${id}`, { method: 'PUT', body: JSON.stringify(data) }); }
export async function deleteEmpresa(id: string): Promise<void> { return request(`/api/v1/registry/empresas/${id}`, { method: 'DELETE' }); }
export async function fetchEstabelecimentos(): Promise<unknown> { return request('/api/v1/registry/estabelecimentos'); }
```

---

## ═══════ GAP 2: Páginas Mock → API Real ═══════

### Matriz de substituição: página × endpoint × prioridade

| Página | Mock atual | Endpoint(s) real(is) | Prioridade |
|--------|-----------|---------------------|------------|
| **care-pathways** | "mock: all in dropdown" | `fetchPathways()`, `fetchPatientPathways()`, `enrollPatientInPathway()` | ⭐ P0 |
| **prescription** | "Simula chamada à API" | `fetchPrescriptions()`, `createPrescription()`, `transitionPrescriptionState()` | ⭐ P0 |
| **patient-movement** | "Dados mock indisponíveis" | `fetchMovements()`, `fetchBedGrid()`, `registerMovement()` | ⭐ P0 |
| **clinical-forms** | fetch raw (parcial) | `fetchClinicalFormTypes()`, `submitClinicalForm()` | ⭐ P0 |
| **clinical-notes** | "Simulate initial load" | `fetchEvolucoes()`, `createEvolucao()` | ⭐ P0 |
| **ventilation** | "generateMockTrend" | `fetchVentilation()`, `fetchVentilationHistory()` | P1 |
| **stability** | "Mock Patients" | `fetchStability()`, `fetchStabilityTrend()` | P1 |
| **sedation** | "MockSedationPatient" | `fetchSedation()`, `fetchSedationHistory()` | P1 |
| **clinical-deterioration** | "using mock data" | `fetchDeterioration()`, `fetchDeteriorationHistory()` | P1 |
| **antimicrobial** | "Mock async save" | `fetchAntimicrobialAssessments()`, `createAntimicrobialAssessment()` | P1 |
| **prophylaxis-bundles** | "Simulate loading" | `fetchProphylaxisBundles()`, `updateProphylaxisBundle()` | P1 |
| **nutrition** | "Mock async save" | `fetchEfficiency()` ou endpoint específico | P1 |
| **fluid-balance** | "Simula carregamento" | endpoint de fluid-balance (verificar backend) | P1 |
| **indicators** | "Simula fetch — usa mock" | `fetchIndicators()`, `fetchIndicatorsSummary()` | P2 |
| **efficiency** | "Simula novo fetch" | `fetchEfficiency()` | P2 |
| **documentation** | "Mock submit" | `fetchDocumentacao()`, `createDocumentacao()` | P2 |
| **alert-routing** | "Simulated API call" | `fetchAlertRoutingRules()`, `createAlertRoutingRule()` | P2 |
| **handoff** | "Simulate data loading" | endpoint de handoff (verificar backend) | P2 |
| **communication** | "Simulated initial load" | endpoint de communication (verificar backend) | P2 |
| **admin/registry** | "Dados mock" | `fetchEmpresas()`, `createEmpresa()` | P2 |
| **admin/tenancy** | "mock data loads" | endpoint de tenancy (verificar backend) | P2 |
| **admin/audit-log** | "Simula carregamento" | endpoint de audit-log (verificar backend) | P2 |

### Padrão de substituição (exemplo para prescription)

ANTES (mock):
```tsx
// prescription/page.tsx atual
const [prescriptions, setPrescriptions] = useState<PrescriptionRecord[]>(MOCK_PRESCRIPTIONS);
const simulateLoading = useCallback(() => { /* ... */ }, []);
```

DEPOIS (API real):
```tsx
import { fetchPrescriptions, createPrescription, type PrescriptionRecord } from '@/lib/api';

const [prescriptions, setPrescriptions] = useState<PrescriptionRecord[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  fetchPrescriptions(mpiId)
    .then(data => setPrescriptions(data.prescriptions))
    .catch(err => setError(err.message))
    .finally(() => setLoading(false));
}, [mpiId]);
```

---

## ═══════ GAP 3: Breadcrumb no Layout ═══════

### Ação: 1 linha no `layout.tsx`

Editar `/Users/familia/intensicare/frontend-v2/app/layout.tsx`:

```tsx
import Breadcrumb from '@/components/Breadcrumb';  // ← NOVO import

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" data-theme="dark" data-tenant="default">
      <body className="min-h-screen">
        <TenantProvider tenant="default" />
        <OverlayStackProvider>
          <ErrorBoundary>
            <Breadcrumb />          {/* ← NOVO: uma linha */}
            {children}
          </ErrorBoundary>
        </OverlayStackProvider>
      </body>
    </html>
  );
}
```

**Verificação:** Navegar entre páginas deve mostrar breadcrumb: `Painel > Prescrições > ...`

---

## ═══════ GAP 4: RBAC Granular no Frontend ═══════

### 4.1 — Hook `useRole()`

Criar `/Users/familia/intensicare/frontend-v2/hooks/useRole.ts`:

```typescript
'use client';
import { useMemo } from 'react';

export type ClinicalRole = 'medico' | 'enfermeiro' | 'fisioterapeuta' | 'farmacia' | 'nutricao' | 'admin' | 'readonly';

const ROLE_HIERARCHY: Record<ClinicalRole, number> = {
  admin: 100,
  medico: 80,
  enfermeiro: 70,
  fisioterapeuta: 60,
  farmacia: 50,
  nutricao: 40,
  readonly: 10,
};

export function useRole(): { role: ClinicalRole | null; isAdmin: boolean; can: (requiredRole: ClinicalRole) => boolean } {
  // FUTURE: read from auth context or API /me endpoint
  // For now, derive from UserResponse.role after login
  const role: ClinicalRole | null = null; // placeholder
  
  return useMemo(() => ({
    role,
    isAdmin: role === 'admin',
    can: (required: ClinicalRole) => {
      if (!role) return false;
      return (ROLE_HIERARCHY[role] || 0) >= (ROLE_HIERARCHY[required] || 0);
    },
  }), [role]);
}
```

### 4.2 — Componente `RequireRole`

Criar `/Users/familia/intensicare/frontend-v2/components/RequireRole.tsx`:

```typescript
'use client';
import { useRole, type ClinicalRole } from '@/hooks/useRole';

interface RequireRoleProps {
  role: ClinicalRole;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

export default function RequireRole({ role, fallback = null, children }: RequireRoleProps) {
  const { can } = useRole();
  if (!can(role)) return <>{fallback}</>;
  return <>{children}</>;
}
```

### 4.3 — Atualizar `UserResponse`

Em `lib/api.ts`, o tipo `UserResponse` já tem `role: string | null`. Adicionar:

```typescript
export interface UserResponse {
  // ... existing fields
  role: ClinicalRole | null;  // atualizar de string para ClinicalRole
}
```

### 4.4 — Página admin/users: dropdown de role

Na página `/Users/familia/intensicare/frontend-v2/app/admin/users/page.tsx`, substituir o toggle `is_admin` por um dropdown `<select>` com as 7 roles:

```tsx
<select value={user.role || ''} onChange={(e) => updateUserRole2(user.id, e.target.value)}>
  <option value="">Nenhum</option>
  <option value="admin">Administrador</option>
  <option value="medico">Médico</option>
  <option value="enfermeiro">Enfermeiro</option>
  <option value="fisioterapeuta">Fisioterapeuta</option>
  <option value="farmacia">Farmácia</option>
  <option value="nutricao">Nutrição</option>
  <option value="readonly">Somente Leitura</option>
</select>
```

---

## ═══════ GAP 5: Tipos TypeScript Atualizados ═══════

### 5.1 — `PatientBedSummary` com `encounter_id`

```typescript
export interface PatientBedSummary {
  // ... existing fields
  encounter_id: string;  // NOVO (gap C4)
}
```

### 5.2 — `PatientDetailResponse` com `encounter_id`

```typescript
export interface PatientDetailResponse {
  // ... existing fields
  encounter_id: string;  // NOVO
}
```

### 5.3 — `AlertInfo` com `definition_version_id`

```typescript
export interface AlertInfo {
  // ... existing fields
  alert_definition_version?: string;  // já existe, verificar se é populado
  definition_version_id?: string;     // NOVO (gap C5 — SHA-256 hash)
}
```

---

## ═══════ AGENTIC-LOOP — REGRAS DE OURO ═══════

### 1. PLANS.md ANTES de qualquer edição

Para cada milestone (≤3 arquivos), escrever em `/Users/familia/intensicare/docs/audit/handoff-ive/PLANS.md`:

```markdown
## Milestone M1.1: API client — Pathways (6 funções)
- [ ] Adicionar tipos PathwayInfo, PatientPathway, etc.
- [ ] Adicionar 6 funções async
- [ ] Verificar com `npx tsc --noEmit`
- [ ] Gatekeeper: `grep -c 'export async function fetch' lib/api.ts` ≥ 23
```

### 2. RECON antes de editar

Antes de modificar qualquer página mock, ler o arquivo atual para entender a estrutura de componentes e estado.

### 3. Gatekeeper ≠ implementador

Após cada milestone, um agente DIFERENTE verifica:
- `npx tsc --noEmit` — zero erros
- `npm run build` — build passa
- `grep -c 'mock\|simul\|MOCK' app/<page>/page.tsx` — deve ser 0 após substituição

### 4. Máximo paralelismo

Páginas que não compartilham arquivos rodam em paralelo:
```
Batch 1 (paralelo): care-pathways ∥ prescription ∥ patient-movement
Batch 2 (paralelo): clinical-forms ∥ clinical-notes
Batch 3 (paralelo): ventilation ∥ stability ∥ sedation ∥ deterioration
Batch 4 (paralelo): antimicrobial ∥ prophylaxis ∥ nutrition ∥ fluid-balance
Batch 5 (paralelo): indicators ∥ efficiency ∥ documentation ∥ alert-routing
Batch 6 (paralelo): handoff ∥ communication ∥ admin/registry ∥ admin/tenancy ∥ admin/audit-log
```

### 5. Verificação com comandos reais

NUNCA confiar em self-report. Sempre verificar:
```bash
npx tsc --noEmit                              # TypeScript
npm run build                                  # Next.js build
grep -c 'export async function' lib/api.ts     # Contagem de funções
grep -rl 'mock\|simul\|MOCK' app/ --include='*.tsx' | wc -l  # Páginas mock restantes
```

### 6. PERSISTÊNCIA — Loop até 100%

Após CADA milestone:
1. Rodar gatekeeper
2. Se FALHAR → diagnosticar → agente DIFERENTE corrige → re-gatekeeper
3. Se PASSAR → próximo milestone
4. Loop NÃO termina até TODOS os milestones passarem

### 7. Estado no filesystem

Atualizar `/Users/familia/intensicare/docs/audit/handoff-ive/HANDOFF.yaml` após cada milestone:
```yaml
milestone: "M1.1"
status: DONE | FAILED | IN_PROGRESS
files_changed: ["lib/api.ts"]
gatekeeper: "npx tsc --noEmit: PASS | grep count: 23"
```

---

## ═══════ DONE WHEN ═══════

### GAP 1 — API Client
- [ ] `lib/api.ts` tem 67+ funções exportadas (17 existentes + 50 novas)
- [ ] `npx tsc --noEmit` passa sem erros
- [ ] Todos os tipos têm JSDoc mínimo

### GAP 2 — Páginas Mock
- [ ] 22 páginas com `fetch`/função API real (zero mock)
- [ ] Estados de loading/error implementados em cada página
- [ ] `npm run build` passa

### GAP 3 — Breadcrumb
- [ ] `<Breadcrumb />` no `layout.tsx`
- [ ] Navegação entre páginas mostra trilha correta
- [ ] PT-BR labels funcionam

### GAP 4 — RBAC
- [ ] `hooks/useRole.ts` existe e exporta `useRole()`
- [ ] `components/RequireRole.tsx` existe
- [ ] Página admin/users tem dropdown de 7 roles
- [ ] `updateUserRole2()` é chamada com string de role

### GAP 5 — Tipos
- [ ] `PatientBedSummary` tem `encounter_id`
- [ ] `PatientDetailResponse` tem `encounter_id`
- [ ] `AlertInfo` tem `definition_version_id`
- [ ] `UserResponse.role` usa `ClinicalRole` union type

### Verificação Final
```bash
cd /Users/familia/intensicare/frontend-v2
npx tsc --noEmit                    # DEVE: zero erros
npm run build                        # DEVE: build sucesso
grep -c 'export async function' lib/api.ts  # DEVE: ≥ 67
grep -rl 'mock\|simul\|MOCK' app/ --include='*.tsx' | wc -l  # DEVE: 0
grep 'Breadcrumb' app/layout.tsx     # DEVE: import + <Breadcrumb />
```

---

## ═══════ ANTI-PATTERNS ═══════

- ❌ Deixar `useState(MOCK_DATA)` depois de adicionar API function
- ❌ Não implementar estado de loading (tela branca enquanto carrega)
- ❌ Não implementar estado de erro (crash silencioso)
- ❌ Usar `any` em vez de tipos específicos nos Grupos 1.6 e 1.7 (substituir por tipos reais dos contratos OpenAPI)
- ❌ Breadcrumb com `display: none` ou `visibility: hidden`
- ❌ Role dropdown que não chama `updateUserRole2()`
- ❌ Pular gatekeeper "porque foi só uma linha"

## ═══════ REFERENCE ═══════

- Frontend audit: `/Users/familia/intensicare/docs/audit/FRONTEND_AUDIT.md`
- API client atual: `/Users/familia/intensicare/frontend-v2/lib/api.ts`
- Layout atual: `/Users/familia/intensicare/frontend-v2/app/layout.tsx`
- OpenAPI contracts: `/Users/familia/intensicare/docs/contracts/`
- Backend routers: `/Users/familia/intensicare/src/intensicare/api/v1/`
- Forensics synthesis: `/Users/familia/intensicare/docs/audit/FORENSICS_SYNTHESIS.md`
