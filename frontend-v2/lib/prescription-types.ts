// ─── Prescription Types ─────────────────────────────────────────────────────
// D2 — Tipos e dados mock para prescrições de medicamentos.
// Contrato: prescricao-openapi.yaml

import type { ComponentType } from 'react';
import {
  Syringe,
  Pill,
  Droplet,
  Stethoscope,
  FlaskConical,
  SprayCan,
} from 'lucide-react';

// ─── Enums / Union Types ────────────────────────────────────────────────────

export type PrescriptionRoute =
  | 'IV'
  | 'IM'
  | 'SC'
  | 'PO'
  | 'SN'
  | 'IT'
  | 'TOP'
  | 'INAL';

export type PrescriptionStatus = 'active' | 'completed' | 'discontinued';

// ─── Core Interfaces ────────────────────────────────────────────────────────

export interface Prescription {
  id: string;
  mpi_id: string;
  drug: string;
  dose: number;
  unit: string;
  route: PrescriptionRoute;
  frequency: string;
  start_time: string;
  end_time?: string;
  status: PrescriptionStatus;
  notes?: string;
  prescribed_by: string;
  created_at: string;
}

export interface PrescriptionCreate {
  mpi_id: string;
  drug: string;
  dose: number;
  unit: string;
  route: PrescriptionRoute;
  frequency: string;
  start_time?: string;
  notes?: string;
}

// ─── Labels PT-BR ───────────────────────────────────────────────────────────

export const ROUTE_LABELS: Record<PrescriptionRoute, string> = {
  IV: 'Intravenosa',
  IM: 'Intramuscular',
  SC: 'Subcutânea',
  PO: 'Oral',
  SN: 'Sonda Nasoenteral',
  IT: 'Intratecal',
  TOP: 'Tópica',
  INAL: 'Inalatória',
};

export const STATUS_LABELS: Record<PrescriptionStatus, string> = {
  active: 'Ativa',
  completed: 'Concluída',
  discontinued: 'Descontinuada',
};

// ─── Route → Icon Mapping ───────────────────────────────────────────────────

export const ROUTE_ICONS: Record<PrescriptionRoute, ComponentType<{ className?: string }>> = {
  IV: Syringe,
  IM: Syringe,
  SC: Syringe,
  PO: Pill,
  SN: Stethoscope,
  IT: FlaskConical,
  TOP: Droplet,
  INAL: SprayCan,
};

// ─── Mock Patients ──────────────────────────────────────────────────────────

export interface MockPatient {
  mpi_id: string;
  name: string;
  bed: string;
}

export const MOCK_PATIENTS: MockPatient[] = [
  { mpi_id: 'MPI-001', name: 'João Silva', bed: 'UTI-A 101' },
  { mpi_id: 'MPI-002', name: 'Maria Oliveira', bed: 'UTI-A 203' },
  { mpi_id: 'MPI-003', name: 'Carlos Santos', bed: 'UTI-B 115' },
];

// ─── Mock Prescriptions (8 ativas para 3 pacientes) ─────────────────────────

export const MOCK_PRESCRIPTIONS: Prescription[] = [
  // ── Paciente MPI-001: João Silva ──────────────────────────────────────────
  {
    id: 'rx-001',
    mpi_id: 'MPI-001',
    drug: 'Ceftriaxona',
    dose: 2,
    unit: 'g',
    route: 'IV',
    frequency: '12/12h',
    start_time: '2026-07-06T08:00:00Z',
    status: 'active',
    notes: 'Pneumonia comunitária grave. Manter por 7 dias.',
    prescribed_by: 'Dr. Ricardo Almeida',
    created_at: '2026-07-06T08:00:00Z',
  },
  {
    id: 'rx-002',
    mpi_id: 'MPI-001',
    drug: 'Enoxaparina',
    dose: 40,
    unit: 'mg',
    route: 'SC',
    frequency: '24/24h',
    start_time: '2026-07-06T08:00:00Z',
    status: 'active',
    notes: 'Profilaxia TEV. Ajustar se ClCr < 30.',
    prescribed_by: 'Dr. Ricardo Almeida',
    created_at: '2026-07-06T08:00:00Z',
  },
  {
    id: 'rx-003',
    mpi_id: 'MPI-001',
    drug: 'Omeprazol',
    dose: 40,
    unit: 'mg',
    route: 'IV',
    frequency: '24/24h',
    start_time: '2026-07-06T08:00:00Z',
    status: 'active',
    notes: 'Profilaxia de úlcera de estresse.',
    prescribed_by: 'Dr. Ricardo Almeida',
    created_at: '2026-07-06T08:00:00Z',
  },
  // ── Paciente MPI-002: Maria Oliveira ──────────────────────────────────────
  {
    id: 'rx-004',
    mpi_id: 'MPI-002',
    drug: 'Meropenem',
    dose: 1,
    unit: 'g',
    route: 'IV',
    frequency: '8/8h',
    start_time: '2026-07-05T14:00:00Z',
    status: 'active',
    notes: 'Sepse abdominal. Infundir em 3h (prolongada).',
    prescribed_by: 'Dra. Fernanda Costa',
    created_at: '2026-07-05T14:00:00Z',
  },
  {
    id: 'rx-005',
    mpi_id: 'MPI-002',
    drug: 'Noradrenalina',
    dose: 0.1,
    unit: 'mcg/kg/min',
    route: 'IV',
    frequency: 'Contínua',
    start_time: '2026-07-05T14:30:00Z',
    status: 'active',
    notes: 'Titular para PAM ≥ 65 mmHg. Dose atual: 0.1 mcg/kg/min.',
    prescribed_by: 'Dra. Fernanda Costa',
    created_at: '2026-07-05T14:30:00Z',
  },
  {
    id: 'rx-006',
    mpi_id: 'MPI-002',
    drug: 'Midazolam',
    dose: 5,
    unit: 'mg/h',
    route: 'IV',
    frequency: 'Contínua',
    start_time: '2026-07-05T20:00:00Z',
    status: 'active',
    notes: 'Sedação RASS alvo -2 a 0. Interromper diariamente para despertar.',
    prescribed_by: 'Dra. Fernanda Costa',
    created_at: '2026-07-05T20:00:00Z',
  },
  // ── Paciente MPI-003: Carlos Santos ───────────────────────────────────────
  {
    id: 'rx-007',
    mpi_id: 'MPI-003',
    drug: 'Vancomicina',
    dose: 1,
    unit: 'g',
    route: 'IV',
    frequency: '12/12h',
    start_time: '2026-07-07T06:00:00Z',
    status: 'active',
    notes: 'Infundir em 60 min. Monitorar nível sérico (vale).',
    prescribed_by: 'Dr. Paulo Mendes',
    created_at: '2026-07-07T06:00:00Z',
  },
  {
    id: 'rx-008',
    mpi_id: 'MPI-003',
    drug: 'Insulina Regular',
    dose: 2,
    unit: 'UI/h',
    route: 'IV',
    frequency: 'Contínua',
    start_time: '2026-07-07T02:00:00Z',
    status: 'active',
    notes: 'Protocolo de controle glicêmico intensivo. Meta 140-180 mg/dL.',
    prescribed_by: 'Dr. Paulo Mendes',
    created_at: '2026-07-07T02:00:00Z',
  },
];

// ─── Mock Drug Interactions ─────────────────────────────────────────────────

export interface DrugInteraction {
  /** IDs das prescrições envolvidas (drug_a + drug_b) */
  drugPair: [string, string];
  /** Descrição da interação em PT-BR */
  description: string;
  /** Severidade: 'contraindicado' | 'grave' | 'moderado' */
  severity: 'contraindicado' | 'grave' | 'moderado';
}

export const MOCK_DRUG_INTERACTIONS: DrugInteraction[] = [
  {
    drugPair: ['Ceftriaxona', 'Calcium'],
    description:
      'Ceftriaxona + Cálcio → risco de precipitação microcristalina em neonatos e risco de eventos cardiopulmonares. Administrar em vias separadas com intervalo mínimo de 48h.',
    severity: 'contraindicado',
  },
  {
    drugPair: ['Midazolam', 'Noradrenalina'],
    description:
      'Midazolam + Noradrenalina → risco de hipotensão aditiva e depressão respiratória. Monitorização hemodinâmica contínua recomendada.',
    severity: 'grave',
  },
];

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Formata dose + unidade para exibição (ex: "2 g", "0.1 mcg/kg/min") */
export function formatDose(dose: number, unit: string): string {
  const formatted = Number.isInteger(dose) ? dose.toString() : dose.toFixed(2).replace(/\.?0+$/, '');
  return `${formatted} ${unit}`;
}

/** Retorna o ícone Lucide apropriado para a via de administração */
export function getRouteIcon(route: PrescriptionRoute): ComponentType<{ className?: string }> {
  return ROUTE_ICONS[route];
}

/**
 * Retorna o token CSS de cor para o status da prescrição.
 * active → verde (normal), completed → azul, discontinued → cinza
 */
export function getStatusColor(
  status: PrescriptionStatus,
  variant: 'bg' | 'text' | 'border',
): string {
  switch (status) {
    case 'active':
      if (variant === 'bg') return 'var(--clinical-severity-normal-fill)';
      if (variant === 'text') return 'var(--clinical-severity-normal-on-fill)';
      return 'var(--clinical-severity-normal-signal)';
    case 'completed':
      // Blue tones — reuse info/watch band tokens for a blue accent
      if (variant === 'bg') return 'var(--clinical-severity-watch-fill)';
      if (variant === 'text') return 'var(--clinical-severity-watch-on-fill)';
      return 'var(--clinical-severity-watch-signal)';
    case 'discontinued':
    default:
      if (variant === 'bg') return 'var(--semantic-surface-overlay)';
      if (variant === 'text') return 'var(--semantic-text-secondary)';
      return 'var(--semantic-border-default)';
  }
}

/**
 * Mapa de interações por nome de fármaco para lookup rápido.
 * Retorna a interação se houver, ou null.
 */
export function findInteraction(
  drugName: string,
  interactions: DrugInteraction[],
): DrugInteraction | null {
  return (
    interactions.find(
      (ix) => ix.drugPair[0] === drugName || ix.drugPair[1] === drugName,
    ) ?? null
  );
}
