// ─── Movement Types ───────────────────────────────────────────────────────────
// D1 — Tipos e dados mock para movimentação de pacientes (leitos UTI).
// Contrato alinhado com movimentacao-openapi.yaml.

import type { TimelineEvent, TimelineStatus } from '@/components/ClinicalTimeline';

// ─── Movement Type ──────────────────────────────────────────────────────────

export type MovementType = 'admission' | 'transfer' | 'discharge';

// ─── Bed Status Type ────────────────────────────────────────────────────────

export type BedStatusType = 'free' | 'occupied' | 'blocked' | 'cleaning';

// ─── Patient Movement ───────────────────────────────────────────────────────

export interface PatientMovement {
  id: string;
  mpi_id: string;
  type: MovementType;
  from_unit?: string;
  to_unit?: string;
  from_bed?: string;
  to_bed?: string;
  timestamp: string;
  notes?: string;
  registered_by?: string;
  created_at: string;
}

// ─── Bed Status ─────────────────────────────────────────────────────────────

export interface BedStatus {
  id: string;
  unit: string;
  room: string;
  status: BedStatusType;
  current_patient_mpi_id?: string;
  current_patient_name?: string;
  occupied_since?: string;
  last_cleaned_at?: string;
  notes?: string;
}

// ─── Labels (PT-BR) ─────────────────────────────────────────────────────────

export const TYPE_LABELS: Record<MovementType, string> = {
  admission: 'Admissão',
  transfer: 'Transferência',
  discharge: 'Alta',
};

export const STATUS_LABELS: Record<BedStatusType, string> = {
  free: 'Livre',
  occupied: 'Ocupado',
  blocked: 'Bloqueado',
  cleaning: 'Limpeza',
};

// ─── Status Colors (CSS custom property tokens) ─────────────────────────────

export interface StatusColorSet {
  bg: string;
  text: string;
  border: string;
  dot: string;
}

export const STATUS_COLORS: Record<BedStatusType, StatusColorSet> = {
  free: {
    bg: 'var(--feedback-success-bg-light, rgba(34,197,94,0.1))',
    text: 'var(--feedback-success-text-light, #15803d)',
    border: 'var(--feedback-success-border-light, #86efac)',
    dot: 'var(--feedback-success-bg-dark, #22c55e)',
  },
  occupied: {
    bg: 'var(--clinical-severity-normal-wash, rgba(59,130,246,0.1))',
    text: 'var(--clinical-severity-normal-on-surface, #1d4ed8)',
    border: 'var(--clinical-severity-normal-signal, #93c5fd)',
    dot: 'var(--clinical-severity-normal-signal, #3b82f6)',
  },
  blocked: {
    bg: 'var(--clinical-severity-watch-wash, rgba(245,158,11,0.1))',
    text: 'var(--clinical-severity-watch-on-surface, #92400e)',
    border: 'var(--clinical-severity-watch-signal, #fcd34d)',
    dot: 'var(--clinical-severity-watch-signal, #f59e0b)',
  },
  cleaning: {
    bg: 'var(--semantic-surface-overlay, rgba(148,163,184,0.1))',
    text: 'var(--semantic-text-secondary, #64748b)',
    border: 'var(--semantic-border-default, #cbd5e1)',
    dot: 'var(--semantic-text-secondary, #94a3b8)',
  },
};

// ─── Bed Summary ────────────────────────────────────────────────────────────

export interface BedSummary {
  total: number;
  free: number;
  occupied: number;
  blocked: number;
  cleaning: number;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Retorna o label PT-BR para o tipo de movimentação */
export function formatMovementType(type: MovementType): string {
  return TYPE_LABELS[type] ?? type;
}

/** Retorna o conjunto de cores CSS para um status de leito */
export function getBedStatusColor(status: BedStatusType): StatusColorSet {
  return STATUS_COLORS[status] ?? STATUS_COLORS.free;
}

/** Calcula o resumo de leitos a partir da lista */
export function computeBedSummary(beds: BedStatus[]): BedSummary {
  const summary: BedSummary = { total: 0, free: 0, occupied: 0, blocked: 0, cleaning: 0 };
  for (const bed of beds) {
    summary.total++;
    switch (bed.status) {
      case 'free':
        summary.free++;
        break;
      case 'occupied':
        summary.occupied++;
        break;
      case 'blocked':
        summary.blocked++;
        break;
      case 'cleaning':
        summary.cleaning++;
        break;
    }
  }
  return summary;
}

/** Converte PatientMovement → TimelineEvent para uso no ClinicalTimeline */
export function movementToTimelineEvent(movement: PatientMovement): TimelineEvent {
  const typeLabel = formatMovementType(movement.type);
  const description = [
    movement.from_unit && movement.from_bed
      ? `De: ${movement.from_unit} / Leito ${movement.from_bed}`
      : null,
    movement.to_unit && movement.to_bed
      ? `Para: ${movement.to_unit} / Leito ${movement.to_bed}`
      : null,
    movement.notes ?? null,
  ]
    .filter(Boolean)
    .join(' | ');

  const statusMap: Record<MovementType, TimelineStatus> = {
    admission: 'completed',
    transfer: 'in-progress',
    discharge: 'completed',
  };

  return {
    id: movement.id,
    status: statusMap[movement.type] ?? 'completed',
    label: `${typeLabel} — Paciente ${movement.mpi_id}`,
    description: description || undefined,
    timestamp: movement.timestamp,
    icon: movement.type,
  };
}

// ═════════════════════════════════════════════════════════════════════════════
// MOCK DATA
// ═════════════════════════════════════════════════════════════════════════════

// ─── Mock Movements (8 movimentações, 3 pacientes) ──────────────────────────

export const MOCK_MOVEMENTS: PatientMovement[] = [
  {
    id: 'mov-001',
    mpi_id: 'MPI-001',
    type: 'admission',
    from_unit: undefined,
    to_unit: 'UTI-1',
    from_bed: undefined,
    to_bed: '101-I',
    timestamp: '2026-07-01T08:00:00Z',
    registered_by: 'Dr. Carlos',
    notes: 'Admissão pós-cirurgia cardíaca',
    created_at: '2026-07-01T08:05:00Z',
  },
  {
    id: 'mov-002',
    mpi_id: 'MPI-002',
    type: 'admission',
    from_unit: undefined,
    to_unit: 'UTI-1',
    from_bed: undefined,
    to_bed: '102-I',
    timestamp: '2026-07-02T14:30:00Z',
    registered_by: 'Dr. Carlos',
    notes: 'Admissão por sepse abdominal',
    created_at: '2026-07-02T14:35:00Z',
  },
  {
    id: 'mov-003',
    mpi_id: 'MPI-003',
    type: 'admission',
    from_unit: undefined,
    to_unit: 'UTI-2',
    from_bed: undefined,
    to_bed: '201-II',
    timestamp: '2026-07-03T10:15:00Z',
    registered_by: 'Dra. Ana',
    notes: 'Pós-operatório neurocirurgia',
    created_at: '2026-07-03T10:20:00Z',
  },
  {
    id: 'mov-004',
    mpi_id: 'MPI-001',
    type: 'transfer',
    from_unit: 'UTI-1',
    to_unit: 'UTI-1',
    from_bed: '101-I',
    to_bed: '103-I',
    timestamp: '2026-07-04T09:00:00Z',
    registered_by: 'Dr. Carlos',
    notes: 'Transferência para leito com monitorização hemodinâmica',
    created_at: '2026-07-04T09:05:00Z',
  },
  {
    id: 'mov-005',
    mpi_id: 'MPI-002',
    type: 'transfer',
    from_unit: 'UTI-1',
    to_unit: 'UTI-2',
    from_bed: '102-I',
    to_bed: '202-II',
    timestamp: '2026-07-05T16:00:00Z',
    registered_by: 'Dra. Ana',
    notes: 'Transferência para UTI-2 por necessidade de isolamento',
    created_at: '2026-07-05T16:10:00Z',
  },
  {
    id: 'mov-006',
    mpi_id: 'MPI-001',
    type: 'discharge',
    from_unit: 'UTI-1',
    to_unit: undefined,
    from_bed: '103-I',
    to_bed: undefined,
    timestamp: '2026-07-06T11:00:00Z',
    registered_by: 'Dr. Carlos',
    notes: 'Alta da UTI — transferido para enfermaria',
    created_at: '2026-07-06T11:05:00Z',
  },
  {
    id: 'mov-007',
    mpi_id: 'MPI-004',
    type: 'admission',
    from_unit: undefined,
    to_unit: 'UTI-1',
    from_bed: undefined,
    to_bed: '101-I',
    timestamp: '2026-07-07T07:45:00Z',
    registered_by: 'Dr. Carlos',
    notes: 'Admissão por insuficiência respiratória aguda',
    created_at: '2026-07-07T07:50:00Z',
  },
  {
    id: 'mov-008',
    mpi_id: 'MPI-003',
    type: 'transfer',
    from_unit: 'UTI-2',
    to_unit: 'UTI-1',
    from_bed: '201-II',
    to_bed: '104-I',
    timestamp: '2026-07-08T08:30:00Z',
    registered_by: 'Dra. Ana',
    notes: 'Transferência para UTI-1 — melhora neurológica, desmame ventilatório',
    created_at: '2026-07-08T08:35:00Z',
  },
];

// ─── Mock Beds (12 leitos: 6 UTI-1 + 6 UTI-2) ──────────────────────────────

export const MOCK_BEDS: BedStatus[] = [
  // UTI-1
  {
    id: 'bed-101',
    unit: 'UTI-1',
    room: '101-I',
    status: 'occupied',
    current_patient_mpi_id: 'MPI-004',
    current_patient_name: 'Maria Santos',
    occupied_since: '2026-07-07T07:45:00Z',
    notes: 'VM, FiO₂ 40%',
  },
  {
    id: 'bed-102',
    unit: 'UTI-1',
    room: '102-I',
    status: 'free',
    last_cleaned_at: '2026-07-06T14:00:00Z',
    notes: 'Pronto para admissão',
  },
  {
    id: 'bed-103',
    unit: 'UTI-1',
    room: '103-I',
    status: 'cleaning',
    last_cleaned_at: '2026-07-08T07:00:00Z',
    notes: 'Higienização terminal em andamento',
  },
  {
    id: 'bed-104',
    unit: 'UTI-1',
    room: '104-I',
    status: 'occupied',
    current_patient_mpi_id: 'MPI-003',
    current_patient_name: 'Pedro Almeida',
    occupied_since: '2026-07-08T08:30:00Z',
    notes: 'Desmame ventilatório, Glasgow 14',
  },
  {
    id: 'bed-105',
    unit: 'UTI-1',
    room: '105-I',
    status: 'blocked',
    notes: 'Manutenção do ventilador — indisponível até 09/07',
  },
  {
    id: 'bed-106',
    unit: 'UTI-1',
    room: '106-I',
    status: 'free',
    last_cleaned_at: '2026-07-08T06:00:00Z',
    notes: 'Pronto para admissão',
  },
  // UTI-2
  {
    id: 'bed-201',
    unit: 'UTI-2',
    room: '201-II',
    status: 'free',
    last_cleaned_at: '2026-07-08T06:00:00Z',
    notes: 'Pronto para admissão',
  },
  {
    id: 'bed-202',
    unit: 'UTI-2',
    room: '202-II',
    status: 'occupied',
    current_patient_mpi_id: 'MPI-002',
    current_patient_name: 'João Oliveira',
    occupied_since: '2026-07-05T16:00:00Z',
    notes: 'Sepse abdominal, DVA em desmame',
  },
  {
    id: 'bed-203',
    unit: 'UTI-2',
    room: '203-II',
    status: 'free',
    last_cleaned_at: '2026-07-07T18:00:00Z',
    notes: 'Pronto para admissão',
  },
  {
    id: 'bed-204',
    unit: 'UTI-2',
    room: '204-II',
    status: 'occupied',
    current_patient_mpi_id: 'MPI-005',
    current_patient_name: 'Ana Costa',
    occupied_since: '2026-07-07T20:00:00Z',
    notes: 'Pós-PCR, hipotermia terapêutica',
  },
  {
    id: 'bed-205',
    unit: 'UTI-2',
    room: '205-II',
    status: 'occupied',
    current_patient_mpi_id: 'MPI-006',
    current_patient_name: 'Lucas Ferreira',
    occupied_since: '2026-07-08T02:00:00Z',
    notes: 'Trauma cranioencefálico grave',
  },
  {
    id: 'bed-206',
    unit: 'UTI-2',
    room: '206-II',
    status: 'cleaning',
    last_cleaned_at: '2026-07-08T05:30:00Z',
    notes: 'Higienização em andamento',
  },
];

// ─── Mock Bed Summary ───────────────────────────────────────────────────────

export const MOCK_BED_SUMMARY: BedSummary = computeBedSummary(MOCK_BEDS);

// ─── Unit list ──────────────────────────────────────────────────────────────

export const MOCK_UNITS: string[] = ['UTI-1', 'UTI-2'];
