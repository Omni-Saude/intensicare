'use client';

import { getToken, clearToken } from './auth';

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

async function request<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
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
  role: string | null;
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

export interface PatientBedSummary {
  mpi_id: string;
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
