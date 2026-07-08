// ─── Audit Trail Types ────────────────────────────────────────────────────
// Tipos, labels, helpers e dados mock para a Trilha de Auditoria (Fase 5).
// Model: AuditTrail — id, event_ts, tenant_id, actor, action, entity_table,
//        entity_id, mpi_id, request_id

export type AuditAction =
  | 'CREATE'
  | 'UPDATE'
  | 'DELETE'
  | 'ACKNOWLEDGE'
  | 'RESOLVE'
  | 'ESCALATE'
  | 'LOGIN'
  | 'LOGOUT'
  | 'EXPORT';

export interface AuditLogEntry {
  id: number;
  event_ts: string; // ISO 8601
  tenant_id: string | null;
  actor: string;
  action: AuditAction;
  entity_table: string;
  entity_id: string;
  mpi_id: string | null;
  request_id: string | null;
}

export interface AuditLogFilter {
  actor?: string;
  action?: AuditAction;
  entity_table?: string;
  mpi_id?: string;
  dateFrom?: string; // YYYY-MM-DD
  dateTo?: string; // YYYY-MM-DD
}

// ─── Labels em PT-BR ─────────────────────────────────────────────────────

export const ACTION_LABELS: Record<AuditAction, string> = {
  CREATE: 'Criou',
  UPDATE: 'Atualizou',
  DELETE: 'Removeu',
  ACKNOWLEDGE: 'Reconheceu',
  RESOLVE: 'Resolveu',
  ESCALATE: 'Escalou',
  LOGIN: 'Login',
  LOGOUT: 'Logout',
  EXPORT: 'Exportou',
};

// ─── Cores usando tokens feedback ─────────────────────────────────────────

export const ACTION_COLORS: Record<
  AuditAction,
  { bg: string; text: string; border: string }
> = {
  CREATE: {
    bg: 'var(--feedback-success-bg-dark)',
    text: 'var(--feedback-success-text-dark)',
    border: 'var(--feedback-success-border-dark)',
  },
  UPDATE: {
    bg: 'var(--feedback-info-bg-dark)',
    text: 'var(--feedback-info-text-dark)',
    border: 'var(--feedback-info-border-dark)',
  },
  DELETE: {
    bg: 'var(--feedback-error-bg-dark)',
    text: 'var(--feedback-error-text-dark)',
    border: 'var(--feedback-error-border-dark)',
  },
  ACKNOWLEDGE: {
    bg: 'var(--feedback-success-bg-dark)',
    text: 'var(--feedback-success-text-dark)',
    border: 'var(--feedback-success-border-dark)',
  },
  RESOLVE: {
    bg: 'var(--feedback-info-bg-dark)',
    text: 'var(--feedback-info-text-dark)',
    border: 'var(--feedback-info-border-dark)',
  },
  ESCALATE: {
    bg: 'var(--feedback-warning-bg-dark)',
    text: 'var(--feedback-warning-text-dark)',
    border: 'var(--feedback-warning-border-dark)',
  },
  LOGIN: {
    bg: 'var(--feedback-info-bg-dark)',
    text: 'var(--feedback-info-text-dark)',
    border: 'var(--feedback-info-border-dark)',
  },
  LOGOUT: {
    bg: 'rgba(255,255,255,0.05)',
    text: 'var(--semantic-text-secondary)',
    border: 'var(--semantic-border-default)',
  },
  EXPORT: {
    bg: 'var(--feedback-warning-bg-dark)',
    text: 'var(--feedback-warning-text-dark)',
    border: 'var(--feedback-warning-border-dark)',
  },
};

// ─── Helpers ──────────────────────────────────────────────────────────────

/** Formata ISO 8601 → "dd/MM/yyyy HH:mm" */
export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  const dd = String(d.getDate()).padStart(2, '0');
  const MM = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  const HH = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  return `${dd}/${MM}/${yyyy} ${HH}:${mm}`;
}

/** Formata tempo relativo: "há X min/horas/dias" */
export function formatRelativeTime(iso: string): string {
  const now = Date.now();
  const then = new Date(iso).getTime();
  const diffMs = now - then;

  if (diffMs < 0) return 'agora mesmo';

  const minutes = Math.floor(diffMs / (1000 * 60));
  if (minutes < 1) return 'agora mesmo';
  if (minutes === 1) return 'há 1 minuto';
  if (minutes < 60) return `há ${minutes} minutos`;

  const hours = Math.floor(minutes / 60);
  if (hours === 1) return 'há 1 hora';
  if (hours < 24) return `há ${hours} horas`;

  const days = Math.floor(hours / 24);
  if (days === 1) return 'há 1 dia';
  return `há ${days} dias`;
}

// ─── Mock Data: 25 registros variados (últimos 7 dias) ────────────────────

const NOW = Date.now();
const MINUTE = 60_000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

function ago(hoursAgo: number, minutesAgo = 0): string {
  return new Date(NOW - hoursAgo * HOUR - minutesAgo * MINUTE).toISOString();
}

export const MOCK_LOGS: AuditLogEntry[] = [
  {
    id: 1,
    event_ts: ago(0, 5),
    tenant_id: 'tenant-001',
    actor: 'Dra. Camila Rocha',
    action: 'LOGIN',
    entity_table: 'session',
    entity_id: 'sess-8842',
    mpi_id: null,
    request_id: 'req-a1b2c3',
  },
  {
    id: 2,
    event_ts: ago(0, 12),
    tenant_id: 'tenant-001',
    actor: 'Dra. Camila Rocha',
    action: 'UPDATE',
    entity_table: 'patient',
    entity_id: 'pat-101',
    mpi_id: 'MPI-001',
    request_id: 'req-d4e5f6',
  },
  {
    id: 3,
    event_ts: ago(0, 28),
    tenant_id: 'tenant-001',
    actor: 'Enf. Marcos Teixeira',
    action: 'CREATE',
    entity_table: 'vitals',
    entity_id: 'vit-5501',
    mpi_id: 'MPI-002',
    request_id: 'req-g7h8i9',
  },
  {
    id: 4,
    event_ts: ago(1, 10),
    tenant_id: 'tenant-001',
    actor: 'Dr. Rafael Cunha',
    action: 'ACKNOWLEDGE',
    entity_table: 'alert',
    entity_id: 'alrt-201',
    mpi_id: 'MPI-003',
    request_id: 'req-j1k2l3',
  },
  {
    id: 5,
    event_ts: ago(1, 45),
    tenant_id: 'tenant-001',
    actor: 'Dra. Camila Rocha',
    action: 'RESOLVE',
    entity_table: 'alert',
    entity_id: 'alrt-189',
    mpi_id: 'MPI-001',
    request_id: 'req-m4n5o6',
  },
  {
    id: 6,
    event_ts: ago(2, 15),
    tenant_id: 'tenant-002',
    actor: 'Enf. Juliana Andrade',
    action: 'CREATE',
    entity_table: 'handoff',
    entity_id: 'hnd-012',
    mpi_id: 'MPI-004',
    request_id: 'req-p7q8r9',
  },
  {
    id: 7,
    event_ts: ago(2, 50),
    tenant_id: 'tenant-001',
    actor: 'Sistema (Automático)',
    action: 'ESCALATE',
    entity_table: 'alert',
    entity_id: 'alrt-215',
    mpi_id: 'MPI-002',
    request_id: 'req-s1t2u3',
  },
  {
    id: 8,
    event_ts: ago(3, 5),
    tenant_id: 'tenant-001',
    actor: 'Dr. Thiago Menezes',
    action: 'LOGIN',
    entity_table: 'session',
    entity_id: 'sess-9012',
    mpi_id: null,
    request_id: 'req-v4w5x6',
  },
  {
    id: 9,
    event_ts: ago(3, 20),
    tenant_id: 'tenant-001',
    actor: 'Dr. Thiago Menezes',
    action: 'UPDATE',
    entity_table: 'medication',
    entity_id: 'med-3301',
    mpi_id: 'MPI-005',
    request_id: 'req-y7z8a9',
  },
  {
    id: 10,
    event_ts: ago(3, 40),
    tenant_id: 'tenant-002',
    actor: 'Farm. Ana Beatriz',
    action: 'CREATE',
    entity_table: 'medication',
    entity_id: 'med-3305',
    mpi_id: 'MPI-006',
    request_id: 'req-b1c2d3',
  },
  {
    id: 11,
    event_ts: ago(4, 10),
    tenant_id: 'tenant-001',
    actor: 'Dra. Camila Rocha',
    action: 'LOGOUT',
    entity_table: 'session',
    entity_id: 'sess-8842',
    mpi_id: null,
    request_id: 'req-e4f5g6',
  },
  {
    id: 12,
    event_ts: ago(4, 30),
    tenant_id: 'tenant-001',
    actor: 'Enf. Marcos Teixeira',
    action: 'DELETE',
    entity_table: 'vitals',
    entity_id: 'vit-5499',
    mpi_id: 'MPI-002',
    request_id: 'req-h7i8j9',
  },
  {
    id: 13,
    event_ts: ago(4, 55),
    tenant_id: 'tenant-003',
    actor: 'Dr. Rafael Cunha',
    action: 'EXPORT',
    entity_table: 'patient',
    entity_id: 'pat-101',
    mpi_id: 'MPI-001',
    request_id: 'req-k1l2m3',
  },
  {
    id: 14,
    event_ts: ago(5, 8),
    tenant_id: 'tenant-001',
    actor: 'Dr. Rafael Cunha',
    action: 'RESOLVE',
    entity_table: 'alert',
    entity_id: 'alrt-220',
    mpi_id: 'MPI-003',
    request_id: 'req-n4o5p6',
  },
  {
    id: 15,
    event_ts: ago(5, 25),
    tenant_id: 'tenant-002',
    actor: 'Enf. Juliana Andrade',
    action: 'ACKNOWLEDGE',
    entity_table: 'alert',
    entity_id: 'alrt-198',
    mpi_id: 'MPI-004',
    request_id: 'req-q7r8s9',
  },
  {
    id: 16,
    event_ts: ago(5, 50),
    tenant_id: 'tenant-001',
    actor: 'Sistema (Automático)',
    action: 'CREATE',
    entity_table: 'alert',
    entity_id: 'alrt-230',
    mpi_id: 'MPI-001',
    request_id: 'req-t1u2v3',
  },
  {
    id: 17,
    event_ts: ago(6, 10),
    tenant_id: 'tenant-001',
    actor: 'Dr. Thiago Menezes',
    action: 'ESCALATE',
    entity_table: 'alert',
    entity_id: 'alrt-225',
    mpi_id: 'MPI-005',
    request_id: 'req-w4x5y6',
  },
  {
    id: 18,
    event_ts: ago(6, 35),
    tenant_id: 'tenant-001',
    actor: 'Farm. Ana Beatriz',
    action: 'UPDATE',
    entity_table: 'medication',
    entity_id: 'med-3301',
    mpi_id: 'MPI-005',
    request_id: 'req-z7a8b9',
  },
  {
    id: 19,
    event_ts: ago(6, 55),
    tenant_id: 'tenant-002',
    actor: 'Enf. Marcos Teixeira',
    action: 'LOGIN',
    entity_table: 'session',
    entity_id: 'sess-7733',
    mpi_id: null,
    request_id: 'req-c1d2e3',
  },
  {
    id: 20,
    event_ts: ago(7, 5),
    tenant_id: 'tenant-001',
    actor: 'Dra. Camila Rocha',
    action: 'CREATE',
    entity_table: 'threshold',
    entity_id: 'thr-001',
    mpi_id: null,
    request_id: 'req-f4g5h6',
  },
  {
    id: 21,
    event_ts: ago(7, 20),
    tenant_id: 'tenant-001',
    actor: 'Dr. Rafael Cunha',
    action: 'LOGIN',
    entity_table: 'session',
    entity_id: 'sess-6601',
    mpi_id: null,
    request_id: 'req-i7j8k9',
  },
  {
    id: 22,
    event_ts: ago(7, 40),
    tenant_id: 'tenant-003',
    actor: 'Enf. Juliana Andrade',
    action: 'UPDATE',
    entity_table: 'patient',
    entity_id: 'pat-205',
    mpi_id: 'MPI-004',
    request_id: 'req-l1m2n3',
  },
  {
    id: 23,
    event_ts: ago(7, 50),
    tenant_id: 'tenant-001',
    actor: 'Sistema (Automático)',
    action: 'LOGOUT',
    entity_table: 'session',
    entity_id: 'sess-6601',
    mpi_id: null,
    request_id: 'req-o4p5q6',
  },
  {
    id: 24,
    event_ts: ago(7, 58),
    tenant_id: 'tenant-002',
    actor: 'Dr. Thiago Menezes',
    action: 'DELETE',
    entity_table: 'handoff',
    entity_id: 'hnd-008',
    mpi_id: 'MPI-006',
    request_id: 'req-r7s8t9',
  },
  {
    id: 25,
    event_ts: ago(7, 65),
    tenant_id: 'tenant-001',
    actor: 'Farm. Ana Beatriz',
    action: 'EXPORT',
    entity_table: 'medication',
    entity_id: 'med-list',
    mpi_id: null,
    request_id: 'req-u1v2w3',
  },
];
