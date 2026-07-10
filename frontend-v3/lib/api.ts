// =============================================================================
// IntensiCare Frontend v3 — API Client (derived from pathways-openapi.yaml)
// =============================================================================
// JWT in-memory (never localStorage/sessionStorage). All requests go through
// the request<T>() wrapper which attaches the Bearer token, handles 401 →
// redirect /login, and throws typed ApiError on non-2xx responses.
// =============================================================================

// ---------------------------------------------------------------------------
// Severity
// ---------------------------------------------------------------------------

export type SeverityLevel = 'normal' | 'watch' | 'urgent' | 'critical';

// ---------------------------------------------------------------------------
// Domain types (derived from pathways-openapi.yaml schemas)
// ---------------------------------------------------------------------------

export interface Pathway {
  id: number;
  name: string;
  slug?: string;
  description?: string;
  active?: boolean;
  states: PathwayState[];
  criteria?: PathwayCriteria[];
  created_at?: string;
  updated_at?: string;
}

export interface PathwayState {
  id: string;
  name: string;
  order: number;
  description?: string;
  is_terminal?: boolean;
}

export interface PathwayCriteria {
  id: string;
  name: string;
  category: string;
  description?: string;
  unit?: string;
  normal_range?: string;
  alert_threshold?: string;
  met?: boolean;
  value?: string;
  evaluated_at?: string;
}

export interface PatientPathway {
  id: number;
  mpi_id: string;
  pathway: Pathway;
  current_state: PathwayState;
  criteria?: PathwayCriteria[];
  status: 'active' | 'completed' | 'archived';
  severity?: SeverityLevel;
  enrolled_at: string;
  enrolled_by?: string;
  completed_at?: string;
  updated_at?: string;
}

export interface PathwayProgress {
  patient_pathway_id: number;
  mpi_id: string;
  pathway_name: string;
  current_state: PathwayState;
  criteria_summary: {
    total: number;
    met: number;
    not_met: number;
    pending: number;
  };
  criteria?: PathwayCriteria[];
  state_history?: StateTransition[];
  trend: 'improving' | 'stable' | 'worsening' | 'none';
  last_evaluated_at?: string;
  recommendation?: string;
}

export interface StateTransition {
  from_state?: string;
  to_state: string;
  changed_at: string;
  reason?: string;
}

export interface AlertInfo {
  id: number;
  type: string;
  severity: SeverityLevel;
  title: string;
  message: string;
  mpi_id?: string;
  patient_name?: string;
  pathway_name?: string;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  resolved_by?: string;
  resolution?: string;
}

export interface DashboardResponse {
  patients: PatientBedSummary[];
  total: number;
  critical_count: number;
  unit_counts?: Record<string, number>;
}

export interface PatientBedSummary {
  mpi_id: string;
  patient_name: string;
  bed: string;
  unit: string;
  mews?: number;
  news2?: number;
  severity: SeverityLevel;
  last_vital_at?: string;
  active_pathways?: { slug: string; severity: SeverityLevel }[];
  vitals?: {
    hr?: number;
    spo2?: number;
    bp_sys?: number;
    bp_dia?: number;
  };
}

export interface PatientDetailResponse {
  mpi_id: string;
  patient_name: string;
  bed: string;
  unit: string;
  vitals: VitalRecord[];
  scores: ScoreRecord[];
  active_pathways_count: number;
}

export interface VitalRecord {
  name: string;
  value: number;
  unit: string;
  measured_at: string;
  severity?: SeverityLevel;
}

export interface ScoreRecord {
  name: string;
  value: number;
  measured_at: string;
  trend?: string;
}

export interface AlertListResponse {
  items: AlertInfo[];
  total: number;
}

export interface UserInfo {
  id: string;
  name: string;
  email: string;
  role: string;
  is_admin: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

// ---------------------------------------------------------------------------
// Filter types
// ---------------------------------------------------------------------------

export interface AlertFilters {
  severity?: SeverityLevel;
  type?: string;
  acknowledged?: boolean;
  resolved?: boolean;
  limit?: number;
  offset?: number;
}

// ---------------------------------------------------------------------------
// ApiError
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

// ---------------------------------------------------------------------------
// JWT storage (in-memory)
// ---------------------------------------------------------------------------

let _token: string | null = null;

export function getToken(): string | null {
  return _token;
}

export function setToken(token: string): void {
  _token = token;
}

function clearToken(): void {
  _token = null;
}

// ---------------------------------------------------------------------------
// request<T> — generic fetch wrapper
// ---------------------------------------------------------------------------

const API_BASE = '/api/v1';

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    // Only redirect if we're in the browser
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    throw new ApiError(401, 'Não autorizado');
  }

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // ignore parse error
    }
    throw new ApiError(response.status, detail);
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Auth endpoints
// ---------------------------------------------------------------------------

export async function login(username: string, password: string): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  });

  if (!response.ok) {
    let detail = 'Falha na autenticação';
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // ignore
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<LoginResponse>;
}

export async function logout(): Promise<void> {
  clearToken();
}

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export async function fetchDashboard(unit?: string): Promise<DashboardResponse> {
  const params = unit ? `?unit=${encodeURIComponent(unit)}` : '';
  return request<DashboardResponse>(`/dashboard${params}`);
}

// ---------------------------------------------------------------------------
// Patient
// ---------------------------------------------------------------------------

export async function fetchPatientDetail(mpiId: string): Promise<PatientDetailResponse> {
  return request<PatientDetailResponse>(`/patients/${encodeURIComponent(mpiId)}`);
}

export async function fetchPatientPathways(
  mpiId: string,
  status: 'active' | 'completed' | 'archived' = 'active',
): Promise<{ items: PatientPathway[]; total: number }> {
  return request<{ items: PatientPathway[]; total: number }>(
    `/patients/${encodeURIComponent(mpiId)}/pathways?status=${status}`,
  );
}

export async function fetchPathwayProgress(
  mpiId: string,
  ppId: number,
): Promise<PathwayProgress> {
  return request<PathwayProgress>(
    `/patients/${encodeURIComponent(mpiId)}/pathways/${ppId}/progress`,
  );
}

// ---------------------------------------------------------------------------
// Pathways catalog
// ---------------------------------------------------------------------------

export async function fetchPathways(
  activeOnly: boolean = true,
): Promise<{ items: Pathway[]; total: number }> {
  return request<{ items: Pathway[]; total: number }>(
    `/pathways?active_only=${activeOnly}`,
  );
}

export async function fetchPathway(id: number): Promise<Pathway> {
  return request<Pathway>(`/pathways/${id}`);
}

// ---------------------------------------------------------------------------
// Alerts
// ---------------------------------------------------------------------------

export async function fetchAlerts(params: AlertFilters = {}): Promise<AlertListResponse> {
  const searchParams = new URLSearchParams();
  if (params.severity) searchParams.set('severity', params.severity);
  if (params.type) searchParams.set('type', params.type);
  if (params.acknowledged !== undefined) searchParams.set('acknowledged', String(params.acknowledged));
  if (params.resolved !== undefined) searchParams.set('resolved', String(params.resolved));
  if (params.limit) searchParams.set('limit', String(params.limit));
  if (params.offset) searchParams.set('offset', String(params.offset));

  const qs = searchParams.toString();
  return request<AlertListResponse>(`/alerts${qs ? `?${qs}` : ''}`);
}

export async function acknowledgeAlert(id: number): Promise<AlertInfo> {
  return request<AlertInfo>(`/alerts/${id}/acknowledge`, { method: 'POST' });
}

export async function escalateAlert(id: number): Promise<AlertInfo> {
  return request<AlertInfo>(`/alerts/${id}/escalate`, { method: 'POST' });
}

export async function resolveAlert(id: number, resolution: string): Promise<AlertInfo> {
  return request<AlertInfo>(`/alerts/${id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ resolution }),
  });
}

// ---------------------------------------------------------------------------
// Admin — Users
// ---------------------------------------------------------------------------

export async function fetchUsers(): Promise<{ items: UserInfo[]; total: number }> {
  return request<{ items: UserInfo[]; total: number }>('/admin/users');
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export async function fetchHealth(): Promise<{ status: string; version: string }> {
  return request<{ status: string; version: string }>('/health');
}
