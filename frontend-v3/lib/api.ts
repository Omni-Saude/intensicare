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

// ---------------------------------------------------------------------------
// Alert groups (ADR-0039 — read-side aggregation, FASE 2B.1)
// ---------------------------------------------------------------------------
// GET /api/v1/alerts?group_by=signal groups the *current* filter result by
// (mpi_id, score_type). The source of truth (`alert` rows) is never merged
// or altered server-side — every original alert stays individually
// addressable inside `members` (zero-information-loss invariant, ADR-0039
// §1). Without `group_by`, the contract above (AlertListResponse) is
// unchanged — this is a purely additive shape.
export interface AlertGroup {
  mpi_id: string;
  patient_name: string;
  score_type: string;
  max_severity: SeverityLevel;
  count: number;
  first_created_at: string;
  latest_created_at: string;
  /**
   * True when the newest active member's severity outranks the oldest
   * active member's — ADR-0039 §3: escalation always "fura o rollup"; the
   * UI must surface this prominently and never suppress it, even collapsed.
   */
  escalating: boolean;
  members: AlertInfo[];
}

export interface AlertGroupListResponse {
  groups: AlertGroup[];
  total_groups: number;
  total_alerts: number;
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
// Error detail normalization (handles Pydantic validation error arrays)
// ---------------------------------------------------------------------------

/**
 * Normalizes API error detail into a human-readable string.
 * Handles Pydantic validation error arrays (e.g., [{"type":"missing","loc":["body","username"],"msg":"Field required"}])
 * as well as string, object, and fallback cases.
 */
function normalizeApiDetail(detail: unknown, fallback: string): string {
  // String: return as-is
  if (typeof detail === 'string') {
    return detail;
  }

  // Array of Pydantic validation errors
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === 'object' && item !== null && 'msg' in item) {
          const msg = item.msg;
          // Extract the field name from loc (e.g., ["body", "username"] → "username")
          const loc = Array.isArray(item.loc) && item.loc.length > 0
            ? item.loc[item.loc.length - 1]
            : null;

          if (loc && msg) {
            return `${loc}: ${msg}`;
          }
          return msg;
        }
        return null;
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join('; ');
    }
  }

  // Object with .msg or .message field
  if (typeof detail === 'object' && detail !== null) {
    const obj = detail as Record<string, unknown>;
    if ('msg' in obj && typeof obj.msg === 'string') {
      return obj.msg;
    }
    if ('message' in obj && typeof obj.message === 'string') {
      return obj.message;
    }
  }

  // Fallback for unknown types
  return fallback;
}

// ---------------------------------------------------------------------------
// JWT storage (in-memory)
// ---------------------------------------------------------------------------

let _token: string | null = null;

export function getToken(): string | null {
  return _token;
}

// BUG-F7-05 fix: notify listeners the moment a token becomes available.
// lib/websocket.ts's connectWS() only checks getToken() once per connection
// attempt; on a fresh reload/deep-link that attempt fires (from a page's
// useRealtimeChannel mount) before the async session bootstrap below
// (ensureSession(), via POST /auth/refresh) has resolved, sees no token, and
// gives up permanently — no page ever explicitly retries. Rather than have
// lib/websocket.ts poll or duplicate this module's session logic, it
// subscribes here once and reattempts the connection when a token shows up.
const tokenListeners = new Set<() => void>();

export function onTokenAvailable(listener: () => void): () => void {
  tokenListeners.add(listener);
  return () => {
    tokenListeners.delete(listener);
  };
}

export function setToken(token: string): void {
  _token = token;
  tokenListeners.forEach((fn) => fn());
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
      detail = normalizeApiDetail(body.detail, detail);
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
      detail = normalizeApiDetail(body.detail, detail);
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

// ADR-0039 §1/§2: read-side aggregation, adjudicated contract. `params`
// reuses AlertFilters as-is — status/severity/limit/offset apply to the
// underlying members before grouping ("filtros existentes aplicam-se aos
// membros"). group_by currently only accepts the literal "signal" (group
// by mpi_id+score_type); no other value is defined by the contract.
export async function fetchAlertGroups(
  params: AlertFilters = {},
): Promise<AlertGroupListResponse> {
  const searchParams = new URLSearchParams();
  searchParams.set('group_by', 'signal');
  if (params.status) searchParams.set('status', params.status);
  if (params.severity) searchParams.set('severity', params.severity);
  if (params.limit) searchParams.set('limit', String(params.limit));
  if (params.offset) searchParams.set('offset', String(params.offset));

  return request<AlertGroupListResponse>(`/alerts?${searchParams.toString()}`);
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

// Backend enum — src/intensicare/auth/dependencies.py CLINICAL_ROLES; the
// UserCreate.role validator in src/intensicare/api/v1/admin.py rejects any
// other value with 422. Keep this list in sync with the backend.
export type ClinicalRole =
  | 'admin'
  | 'medico'
  | 'enfermeiro'
  | 'fisioterapeuta'
  | 'farmacia'
  | 'nutricao'
  | 'readonly';

export const CLINICAL_ROLE_OPTIONS: { value: ClinicalRole; label: string }[] = [
  { value: 'admin', label: 'Administrador' },
  { value: 'medico', label: 'Médico' },
  { value: 'enfermeiro', label: 'Enfermeiro' },
  { value: 'fisioterapeuta', label: 'Fisioterapeuta' },
  { value: 'farmacia', label: 'Farmácia' },
  { value: 'nutricao', label: 'Nutrição' },
  { value: 'readonly', label: 'Somente leitura' },
];

export interface UserCreatePayload {
  username: string;
  email: string;
  password: string;
  display_name?: string;
  is_admin: boolean;
  is_active: boolean;
  role: ClinicalRole;
}

// POST /admin/users — 201 UserOut on success (shape matches UserInfo). 409
// on duplicate username, 422 on validation failure (see UserCreate in
// src/intensicare/api/v1/admin.py) — ApiError.detail carries the FastAPI
// `detail` payload, which for 422s is a Pydantic error array rather than a
// string; callers must not render it directly (see formatApiErrorDetail
// in components/admin/user-manager.tsx).
export async function createUser(payload: UserCreatePayload): Promise<UserInfo> {
  return request<UserInfo>('/admin/users', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export async function fetchHealth(): Promise<{ status: string; version: string }> {
  return request<{ status: string; version: string }>('/health');
}
