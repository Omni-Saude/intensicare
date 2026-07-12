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
  /**
   * Highest severity among the patient's active alerts, independent of the
   * aggregate `severity` field above. Backend may send null when there are
   * no active alerts. (Dim B/D audit: backend field added alongside the
   * always-present `severity`.)
   */
  highest_alert_severity?: string | null;
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
  // Backend UserResponse.id is the numeric DB PK (int). Kept as a union
  // rather than switching fully to `number` because lib/auth.tsx also
  // synthesizes a UserInfo client-side by decoding the JWT payload, where
  // `id` is populated from the `sub` claim (the username, a string).
  id: number | string;
  name: string;
  email: string;
  role: string;
  is_admin: boolean;
  // Additive fields present on the backend UserResponse but not always
  // populated by the JWT-decode fallback in lib/auth.tsx.
  username?: string;
  display_name?: string | null;
  is_active?: boolean;
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
  const token = getToken();
  clearToken();

  // Best-effort server-side revocation: POST /api/v1/auth/logout blacklists
  // the JWT in Redis (see src/intensicare/api/v1/auth.py) so it can no longer
  // authenticate API requests even if leaked/replayed. The backend route is
  // now mounted and reachable via the Next.js rewrite proxy. If the call fails
  // (network error), it is non-fatal since client-side session state is already
  // cleared.
  if (token) {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      // Network error or 404 (see note above) — non-fatal, session state
      // is already cleared client-side.
    }
  }

  // KNOWN LIMITATION (audit Dim B/D, verified in auth.py
  // _build_login_response): the `token` and `access_token` cookies set on
  // login are HttpOnly + Secure-flagged-off-only-for-dev, so client-side JS
  // cannot read or delete them — `document.cookie` writes to an HttpOnly
  // cookie are silently ignored by the browser (they are not thrown, they
  // just do nothing). The line below is therefore a best-effort no-op
  // against the current backend cookie config, kept for defense-in-depth
  // (e.g. if a deployment ever sets these non-HttpOnly) and cleared as
  // requested by the audit. It does NOT solve the underlying issue: the
  // Next.js middleware (middleware.ts) only checks for the *presence* of
  // the `token` cookie, so the browser keeps looking "authenticated" for
  // page-routing purposes for up to ~30 min (cookie max_age=1800) after
  // logout, even though the JWT itself is blacklisted server-side (once
  // the call above is reachable). A full fix is out of this task's 3-file
  // scope: the backend /auth/logout handler must call
  // `response.delete_cookie(...)` for both cookies (it currently returns a
  // plain dict, not a Response with Set-Cookie headers), and must be
  // reachable at /api/v1/auth/logout (or the rewrite proxy extended) for
  // this client call to reach it in the first place.
  if (typeof document !== 'undefined') {
    document.cookie = 'token=; Max-Age=0; path=/';
    document.cookie = 'access_token=; Max-Age=0; path=/';
  }
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

// Backend enum — src/intensicare/api/v1/alerts.py ResolveRequest.resolution
// (`valid_resolutions` set); any other value gets a 422.
export type AlertResolution = 'true_positive' | 'false_positive' | 'intervention_done';

export async function resolveAlert(
  id: number,
  resolution: AlertResolution,
  note?: string,
): Promise<AlertInfo> {
  return request<AlertInfo>(`/alerts/${id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ resolution, ...(note?.trim() ? { note: note.trim() } : {}) }),
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
