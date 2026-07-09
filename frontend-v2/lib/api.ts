'use client';

import { type ClinicalRole } from '@/hooks/useRole';

const BASE_URL = ''; // Uses Next.js rewrites to proxy to localhost:8000

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
    this.name = 'ApiError';
  }
}

// ── In-memory API token store (F-SEC-005) ──
// Token lives only in JS module scope — never persisted to sessionStorage,
// localStorage, or document.cookie. Lost on page refresh (user must
// re-authenticate). Survives SPA client-side navigations.
//
// The login page calls setApiToken() after successful authentication.
// On 401 responses or explicit logout, clearApiToken() is called.

let _apiToken: string | null = null;

export function setApiToken(token: string): void {
  _apiToken = token;
}

export function clearApiToken(): void {
  _apiToken = null;
}

export function getApiToken(): string | null {
  return _apiToken;
}

async function request<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (_apiToken) {
    headers['Authorization'] = `Bearer ${_apiToken}`;
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearApiToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new ApiError(401, 'Authentication required');
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const errorBody = await response.json();
      detail = errorBody.detail || errorBody.message || detail;
    } catch {
      // Use status text if body isn't JSON
    }
    throw new ApiError(response.status, detail);
  }

  return response.json();
}

// --- Auth API ---

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  display_name?: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  display_name: string | null;
  is_admin: boolean;
  is_active: boolean;
  role: ClinicalRole | null;
  created_at: string | null;
}

export async function loginApi(credentials: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

export async function registerApi(data: RegisterRequest): Promise<UserResponse> {
  return request<UserResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function logoutApi(): Promise<void> {
  try {
    await request('/auth/logout', { method: 'POST' });
  } catch {
    // Logout should succeed even if API call fails
  }
}

// --- Dashboard API ---

export interface LatestVitals {
  heart_rate: number | null;
  systolic_bp: number | null;
  diastolic_bp: number | null;
  spo2: number | null;
  respiratory_rate: number | null;
  temperature: number | null;
  recorded_at: string | null;
}

export interface PatientBedSummary {
  mpi_id: string;
  encounter_id: string;
  bed_id: string | null;
  display_name: string;
  unit: string | null;
  latest_mews: number | null;
  latest_news2: number | null;
  news2_risk: string | null;
  mews_trend: string | null;
  news2_trend: string | null;
  active_alerts_count: number;
  highest_alert_severity: string | null;
  latest_vitals: LatestVitals | null;
  last_updated: string | null;
}

export interface DashboardResponse {
  patients: PatientBedSummary[];
  total: number;
  active_alerts_total: number;
}

export async function fetchDashboard(unit?: string): Promise<DashboardResponse> {
  const params = unit ? `?unit=${encodeURIComponent(unit)}` : '';
  return request<DashboardResponse>(`/api/v1/dashboard${params}`);
}

// --- Patient API ---

export interface VitalsHistoryPoint {
  recorded_at: string;
  heart_rate: number | null;
  systolic_bp: number | null;
  diastolic_bp: number | null;
  temperature: number | null;
  spo2: number | null;
  respiratory_rate: number | null;
  avpu: string | null;
  supplemental_o2: boolean | null;
}

export interface ScoreHistoryPoint {
  calculated_at: string;
  score_type: string;
  score_value: number;
  trend: string | null;
}

export interface AlertInfo {
  id: number;
  mpi_id: string;
  score_id: number | null;
  severity: string;
  status: string;
  title: string;
  body: string | null;
  created_at: string;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
  resolved_at: string | null;
  resolution: string | null;
  // Why-panel fields (may not be present on all alerts)
  triggering_parameters?: TriggeringParameter[];
  rule_reference?: string;
  alert_definition_version?: string;
  definition_version_id?: string;
  data_coverage_note?: string;
}

export interface TriggeringParameter {
  name: string;
  value: number | string;
  threshold: number | string;
  unit?: string;
  breached: boolean;
}

export interface PatientDetailResponse {
  mpi_id: string;
  encounter_id: string;
  bed_id: string | null;
  display_name: string;
  unit: string | null;
  vitals_history: VitalsHistoryPoint[];
  mews_history: ScoreHistoryPoint[];
  news2_history: ScoreHistoryPoint[];
  active_alerts: AlertInfo[];
}

export async function fetchPatientDetail(mpiId: string): Promise<PatientDetailResponse> {
  return request<PatientDetailResponse>(
    `/api/v1/patients/${encodeURIComponent(mpiId)}/detail`
  );
}

// --- Alerts API ---

export interface AlertListResponse {
  alerts: AlertInfo[];
  total: number;
}

export async function fetchAlerts(params?: {
  status?: string;
  mpi_id?: string;
  limit?: number;
  offset?: number;
}): Promise<AlertListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.status) searchParams.set('status', params.status);
  if (params?.mpi_id) searchParams.set('mpi_id', params.mpi_id);
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  const qs = searchParams.toString();
  return request<AlertListResponse>(`/api/v1/alerts${qs ? '?' + qs : ''}`);
}

export async function acknowledgeAlert(alertId: number, notes?: string): Promise<AlertInfo> {
  return request<AlertInfo>(`/api/v1/alerts/${alertId}/acknowledge`, {
    method: 'POST',
    body: JSON.stringify({ notes: notes || null }),
  });
}

export async function resolveAlert(
  alertId: number,
  resolution: 'true_positive' | 'false_positive' | 'intervention_done',
  note?: string
): Promise<AlertInfo> {
  return request<AlertInfo>(`/api/v1/alerts/${alertId}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ resolution, note: note || null }),
  });
}

export async function escalateAlert(alertId: number, reason?: string): Promise<AlertInfo> {
  return request<AlertInfo>(`/api/v1/alerts/${alertId}/escalate`, {
    method: 'POST',
    body: JSON.stringify({ reason: reason || null }),
  });
}

// --- Admin API ---

export interface UserListResponse {
  users: UserResponse[];
  total: number;
}

export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  display_name?: string;
  is_admin?: boolean;
  is_active?: boolean;
  role?: string;
}

export interface UserUpdateRequest {
  display_name?: string | null;
  is_admin?: boolean | null;
  is_active?: boolean | null;
  email?: string | null;
  role?: string | null;
}

export async function fetchUsers(): Promise<UserListResponse> {
  return request<UserListResponse>('/admin/users');
}

export async function createUser(data: UserCreateRequest): Promise<UserResponse> {
  return request<UserResponse>('/admin/users', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateUser(userId: number, data: UserUpdateRequest): Promise<UserResponse> {
  return request<UserResponse>(`/admin/users/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export const updateUserRole = (userId: number, isAdmin: boolean) =>
  updateUser(userId, { is_admin: isAdmin });

export const toggleUserActive = (userId: number, isActive: boolean) =>
  updateUser(userId, { is_active: isActive });

export const updateUserRole2 = (userId: number, role: string) =>
  updateUser(userId, { role });

// --- Thresholds API ---

export interface ThresholdConfigResponse {
  id: number;
  tenant_id: string;
  unit: string | null;
  score_type: string;
  watch_threshold: number;
  urgent_threshold: number;
  critical_threshold: number;
  rate_limit_per_hour: number | null;
  cooldown_minutes: number | null;
  updated_at: string | null;
  updated_by: string | null;
}

export interface ThresholdConfigUpdate {
  tenant_id?: string;
  unit?: string | null;
  score_type?: string;
  watch_threshold?: number;
  urgent_threshold?: number;
  critical_threshold?: number;
  rate_limit_per_hour?: number | null;
  cooldown_minutes?: number | null;
}

export async function fetchThresholds(tenantId?: string): Promise<ThresholdConfigResponse[]> {
  const params = tenantId ? `?tenant_id=${encodeURIComponent(tenantId)}` : '';
  return request<ThresholdConfigResponse[]>(`/api/v1/thresholds${params}`);
}

export async function updateThreshold(
  thresholdId: number,
  data: ThresholdConfigUpdate
): Promise<ThresholdConfigResponse> {
  return request<ThresholdConfigResponse>(`/api/v1/thresholds/${thresholdId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function createThreshold(
  data: ThresholdConfigUpdate & { tenant_id: string; score_type: string }
): Promise<ThresholdConfigResponse> {
  return request<ThresholdConfigResponse>('/api/v1/thresholds', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// --- Stats API (admin dashboard) ---

export interface AdminStatsResponse {
  total_users: number;
  active_alerts: number;
  thresholds_configured: number;
}

export async function fetchAdminStats(): Promise<AdminStatsResponse> {
  // Aggregate from existing endpoints
  const [usersResult, thresholds] = await Promise.all([
    fetchUsers(),
    fetchThresholds(),
  ]);
  let activeAlerts = 0;
  try {
    const alertsResult = await request<{ total: number }>('/api/v1/alerts?status=active&limit=1');
    activeAlerts = alertsResult.total;
  } catch {
    activeAlerts = 0;
  }

  return {
    total_users: usersResult.total,
    active_alerts: activeAlerts,
    thresholds_configured: thresholds.length,
  };
}

// --- Health API ---

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  checks: Record<string, { status: string; latency_ms: number | null; detail: string | null }>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health');
}

// ═══════════════════════════════════════════════════════════════
// Pathways API (TDD domain — P0)
// ═══════════════════════════════════════════════════════════════

export interface PathwayInfo {
  id: number;
  name: string;
  slug: string;
  description: string;
  active: boolean;
  definition_version_id?: string;
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
  encounter_id: string;
  bed_id?: string;
  unit?: string;
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

// ═══════════════════════════════════════════════════════════════
// Prescricao API (TDD domain — P0)
// ═══════════════════════════════════════════════════════════════

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

// ═══════════════════════════════════════════════════════════════
// Movimentacao API (TDD domain — P0)
// ═══════════════════════════════════════════════════════════════

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

// ═══════════════════════════════════════════════════════════════
// Formularios API (TDD domain — P0)
// ═══════════════════════════════════════════════════════════════

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

// ═══════════════════════════════════════════════════════════════
// Evolucoes API (TDD domain — P0)
// ═══════════════════════════════════════════════════════════════

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

// ═══════════════════════════════════════════════════════════════
// Domínios Clínicos API (P1)
// ═══════════════════════════════════════════════════════════════

// ventilacao
export async function fetchVentilation(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/ventilation`);
}
export async function fetchVentilationHistory(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/ventilation/history`);
}

// stability
export async function fetchStability(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/stability`);
}
export async function fetchStabilityTrend(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/stability/trend`);
}

// sedacao
export async function fetchSedation(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/sedation`);
}
export async function fetchSedationHistory(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/sedation/history`);
}

// deterioration
export async function fetchDeterioration(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/deterioration`);
}
export async function fetchDeteriorationHistory(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/deterioration/history`);
}

// antimicrobial
export async function fetchAntimicrobialAssessments(): Promise<unknown> {
  return request('/api/v1/antimicrobial/assessments');
}
export async function createAntimicrobialAssessment(data: unknown): Promise<unknown> {
  return request('/api/v1/antimicrobial/assessments', { method: 'POST', body: JSON.stringify(data) });
}
export async function fetchAntimicrobialAssessment(id: string): Promise<unknown> {
  return request(`/api/v1/antimicrobial/assessments/${id}`);
}
export async function fetchAntimicrobialCriteria(): Promise<unknown> {
  return request('/api/v1/antimicrobial/criteria');
}

// prophylaxis
export async function fetchProphylaxisBundles(): Promise<unknown> {
  return request('/api/v1/prophylaxis/bundles');
}
export async function fetchProphylaxisBundle(id: string): Promise<unknown> {
  return request(`/api/v1/prophylaxis/bundles/${id}`);
}
export async function updateProphylaxisBundle(id: string, data: unknown): Promise<unknown> {
  return request(`/api/v1/prophylaxis/bundles/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}
export async function fetchProphylaxisBundleCriteria(id: string): Promise<unknown> {
  return request(`/api/v1/prophylaxis/bundles/${id}/criteria`);
}

// efficiency
export async function fetchEfficiency(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/efficiency`);
}

// indicators
export async function fetchIndicators(): Promise<unknown> {
  return request('/api/v1/indicators');
}
export async function fetchIndicatorsSummary(): Promise<unknown> {
  return request('/api/v1/indicators/summary');
}
export async function fetchIndicator(id: string): Promise<unknown> {
  return request(`/api/v1/indicators/${id}`);
}

// ═══════════════════════════════════════════════════════════════
// Admin + Infra API (P2)
// ═══════════════════════════════════════════════════════════════

// documentacao
export async function fetchDocumentacao(mpiId: string): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/documentacao`);
}
export async function createDocumentacao(mpiId: string, data: unknown): Promise<unknown> {
  return request(`/api/v1/patients/${encodeURIComponent(mpiId)}/documentacao`, { method: 'POST', body: JSON.stringify(data) });
}

// alert_routing
export async function fetchAlertRoutingRules(): Promise<unknown> {
  return request('/api/v1/alert-routing');
}
export async function createAlertRoutingRule(data: unknown): Promise<unknown> {
  return request('/api/v1/alert-routing', { method: 'POST', body: JSON.stringify(data) });
}
export async function fetchAlertRoutingRule(id: string): Promise<unknown> {
  return request(`/api/v1/alert-routing/${id}`);
}
export async function updateAlertRoutingRule(id: string, data: unknown): Promise<unknown> {
  return request(`/api/v1/alert-routing/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}
export async function deleteAlertRoutingRule(id: string): Promise<void> {
  return request(`/api/v1/alert-routing/${id}`, { method: 'DELETE' });
}

// registry
export async function fetchEmpresas(): Promise<unknown> {
  return request('/api/v1/registry/empresas');
}
export async function createEmpresa(data: unknown): Promise<unknown> {
  return request('/api/v1/registry/empresas', { method: 'POST', body: JSON.stringify(data) });
}
export async function fetchEmpresa(id: string): Promise<unknown> {
  return request(`/api/v1/registry/empresas/${id}`);
}
export async function updateEmpresa(id: string, data: unknown): Promise<unknown> {
  return request(`/api/v1/registry/empresas/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}
export async function deleteEmpresa(id: string): Promise<void> {
  return request(`/api/v1/registry/empresas/${id}`, { method: 'DELETE' });
}
export async function fetchEstabelecimentos(): Promise<unknown> {
  return request('/api/v1/registry/estabelecimentos');
}
export async function createEstabelecimento(data: unknown): Promise<unknown> {
  return request('/api/v1/registry/estabelecimentos', { method: 'POST', body: JSON.stringify(data) });
}
export async function fetchEstabelecimento(id: string): Promise<unknown> {
  return request(`/api/v1/registry/estabelecimentos/${id}`);
}
export async function updateEstabelecimento(id: string, data: unknown): Promise<unknown> {
  return request(`/api/v1/registry/estabelecimentos/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}
export async function deleteEstabelecimento(id: string): Promise<void> {
  return request(`/api/v1/registry/estabelecimentos/${id}`, { method: 'DELETE' });
}

// --- Registry: Setores CRUD ---

export async function fetchSetores(): Promise<unknown> {
  return request('/api/v1/registry/setores');
}
export async function createSetor(data: unknown): Promise<unknown> {
  return request('/api/v1/registry/setores', { method: 'POST', body: JSON.stringify(data) });
}
export async function fetchSetor(id: string): Promise<unknown> {
  return request(`/api/v1/registry/setores/${id}`);
}
export async function updateSetor(id: string, data: unknown): Promise<unknown> {
  return request(`/api/v1/registry/setores/${id}`, { method: 'PUT', body: JSON.stringify(data) });
}
export async function deleteSetor(id: string): Promise<void> {
  return request(`/api/v1/registry/setores/${id}`, { method: 'DELETE' });
}

// --- Handoff API ---

export interface HandoffPatient {
  mpi_id: string;
  name: string;
  bed_id?: string;
  status: 'stable' | 'watch' | 'critical';
}

export interface HandoffResponse {
  patients: HandoffPatient[];
  last_handoff_at: string | null;
}

export async function fetchHandoff(): Promise<HandoffResponse> {
  return request<HandoffResponse>('/api/v1/handoff');
}

export async function submitHandoff(data: {
  mpi_ids: string[];
  summary?: string;
  active_issues?: string;
  pending_actions?: string;
  medications?: string;
}): Promise<{ timestamp: string }> {
  return request<{ timestamp: string }>('/api/v1/handoff', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// --- Communication / Handoff Messages API ---

export interface HandoffMessageResponse {
  id: string;
  from_user: string;
  to_shift: string;
  sbar_s: string;
  sbar_b: string;
  sbar_a: string;
  sbar_r: string;
  created_at: string;
  read: boolean;
  urgent: boolean;
}

export interface ShiftOption {
  value: string;
  label: string;
}

export async function fetchHandoffMessages(): Promise<{ messages: HandoffMessageResponse[] }> {
  return request<{ messages: HandoffMessageResponse[] }>('/api/v1/communication/handoff');
}

export async function createHandoffMessage(data: {
  to_shift: string;
  sbar_s: string;
  sbar_b: string;
  sbar_a: string;
  sbar_r: string;
  urgent: boolean;
}): Promise<HandoffMessageResponse> {
  return request<HandoffMessageResponse>('/api/v1/communication/handoff', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function markHandoffMessageRead(id: string): Promise<void> {
  return request<void>(`/api/v1/communication/handoff/${id}/read`, {
    method: 'PUT',
  });
}

export async function fetchShifts(): Promise<{ shifts: ShiftOption[] }> {
  return request<{ shifts: ShiftOption[] }>('/api/v1/communication/shifts');
}

// --- Tenancy API ---

export async function fetchTenancy(): Promise<unknown> {
  return request('/api/v1/tenancy');
}

// --- Audit Log API ---

export async function fetchAuditLogs(params?: {
  actor?: string;
  action?: string;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}): Promise<{ logs: unknown[]; total: number }> {
  const searchParams = new URLSearchParams();
  if (params?.actor) searchParams.set('actor', params.actor);
  if (params?.action) searchParams.set('action', params.action);
  if (params?.date_from) searchParams.set('date_from', params.date_from);
  if (params?.date_to) searchParams.set('date_to', params.date_to);
  if (params?.limit) searchParams.set('limit', String(params.limit));
  if (params?.offset) searchParams.set('offset', String(params.offset));
  const qs = searchParams.toString();
  return request<{ logs: unknown[]; total: number }>(`/api/v1/audit-log${qs ? '?' + qs : ''}`);
}
