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

// Backend contract — src/intensicare/api/v1/alerts.py list_alerts.
// `status` supersedes the old acknowledged/resolved booleans; `type` was
// never accepted by the backend and has been dropped.
export type AlertStatusFilter =
  | 'active'
  | 'acknowledged'
  | 'escalated'
  | 'resolved'
  | 'all';

export interface AlertFilters {
  status?: AlertStatusFilter;
  severity?: SeverityLevel;
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
  // A fresh bootstrap must be attempted (and hit the network again) after
  // logout — the cached promise from a previous successful bootstrap
  // already fired its setToken() side effect once and won't repeat it, so
  // reusing it here would be harmless but stale. Resetting it means the
  // next ensureSession() call re-checks the refresh_token cookie for real,
  // which correctly comes back 401 once the backend has blacklisted it
  // (see _perform_logout in src/intensicare/api/v1/auth.py).
  _bootstrapPromise = null;
}

const API_BASE = '/api/v1';

// ---------------------------------------------------------------------------
// Session bootstrap — recover the in-memory access token from the HttpOnly
// refresh_token cookie on mount (reload / deep-link).
// ---------------------------------------------------------------------------
// The JWT is intentionally in-memory only (see module header — XSS
// hardening, never localStorage/sessionStorage). On a full page load this
// module is re-instantiated with `_token = null`, even though the browser
// may still hold a valid HttpOnly `refresh_token` cookie set by the backend
// on login. Without recovering it, the *first* API call made by any page
// (several pages fetch via useSWR immediately on mount, before
// AuthProvider's own effect has a chance to run — see lib/auth.tsx) would
// go out with no Authorization header, get a 401, and trip the hard
// redirect below — discarding a perfectly valid session.
//
// `ensureSession()` is a memoized, single-flight bootstrap: whichever
// caller reaches it first (AuthProvider's mount effect, or request<T> from
// an eager page fetch) triggers exactly one POST /api/v1/auth/refresh;
// every other concurrent caller awaits that same in-flight promise instead
// of racing ahead with a token-less request or firing duplicate refreshes.
interface RefreshResponse {
  access_token: string;
  token_type: string;
  user: UserInfo;
}

let _bootstrapPromise: Promise<UserInfo | null> | null = null;

export function ensureSession(): Promise<UserInfo | null> {
  if (_token) {
    // Already authenticated in this module instance (e.g. AuthProvider
    // re-mounting during client-side navigation) — nothing to bootstrap.
    return Promise.resolve(null);
  }
  if (!_bootstrapPromise) {
    _bootstrapPromise = fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      // Same-origin via the Next.js rewrite proxy, so cookies flow by
      // default — 'include' is explicit belt-and-suspenders documentation
      // of that requirement, not strictly required for same-origin fetch.
      credentials: 'include',
    })
      .then(async (response) => {
        if (!response.ok) {
          return null;
        }
        const data = (await response.json()) as RefreshResponse;
        setToken(data.access_token);
        return data.user;
      })
      .catch(() => null); // network error / no valid refresh cookie → stay unauthenticated
  }
  return _bootstrapPromise;
}

// ---------------------------------------------------------------------------
// request<T> — generic fetch wrapper
// ---------------------------------------------------------------------------

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  // Block on the session bootstrap so the very first request of a fresh
  // page load doesn't race ahead of the refresh-cookie exchange (see
  // ensureSession() above). Once a token is in memory this resolves
  // synchronously-fast (no extra network round trip).
  await ensureSession();

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

  // FIXED (was KNOWN LIMITATION, audit Dim B/D): the `token`, `access_token`
  // and `refresh_token` cookies are HttpOnly, so client-side JS can never
  // read or delete them — `document.cookie` writes below remain a no-op
  // against them (kept only as defense-in-depth for any deployment that
  // ever sets these non-HttpOnly). The real fix lives server-side: the
  // /api/v1/auth/logout handler (`_perform_logout` in
  // src/intensicare/api/v1/auth.py) now returns a `Response` that calls
  // `delete_cookie(...)` for all three cookies, so as long as the POST
  // above reaches the backend, the browser actually drops them — closing
  // the ~30 min "still looks authenticated" window this comment used to
  // describe, and (now that POST /auth/refresh exists to bootstrap a
  // session from `refresh_token`) preventing a logged-out session from
  // being silently resurrected on the next reload.
  if (typeof document !== 'undefined') {
    document.cookie = 'token=; Max-Age=0; path=/';
    document.cookie = 'access_token=; Max-Age=0; path=/';
    document.cookie = 'refresh_token=; Max-Age=0; path=/';
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
  if (params.status) searchParams.set('status', params.status);
  if (params.severity) searchParams.set('severity', params.severity);
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
