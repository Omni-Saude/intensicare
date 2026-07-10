import type { Meta, StoryObj } from '@storybook/react';
import type { PatientDetailResponse, VitalRecord, ScoreRecord } from '@/lib/api';
import { PatientHeader } from './patient-header';

const mockVitals: VitalRecord[] = [
  { name: 'HR', value: 112, unit: 'bpm', measured_at: '2026-07-09T12:00:00Z', severity: 'urgent' },
  { name: 'BP_SYS', value: 88, unit: 'mmHg', measured_at: '2026-07-09T12:00:00Z', severity: 'critical' },
  { name: 'BP_DIA', value: 56, unit: 'mmHg', measured_at: '2026-07-09T12:00:00Z', severity: 'critical' },
  { name: 'SpO2', value: 91, unit: '%', measured_at: '2026-07-09T12:00:00Z', severity: 'urgent' },
  { name: 'TEMP', value: 38.7, unit: '°C', measured_at: '2026-07-09T12:00:00Z', severity: 'watch' },
];

const mockScores: ScoreRecord[] = [
  { name: 'MEWS', value: 7, measured_at: '2026-07-09T12:00:00Z', trend: 'up' },
  { name: 'MEWS', value: 5, measured_at: '2026-07-09T10:00:00Z', trend: 'up' },
  { name: 'MEWS', value: 3, measured_at: '2026-07-09T08:00:00Z', trend: 'stable' },
  { name: 'MEWS', value: 3, measured_at: '2026-07-09T06:00:00Z', trend: 'stable' },
  { name: 'NEWS2', value: 8, measured_at: '2026-07-09T12:00:00Z', trend: 'up' },
  { name: 'NEWS2', value: 6, measured_at: '2026-07-09T10:00:00Z', trend: 'up' },
  { name: 'NEWS2', value: 4, measured_at: '2026-07-09T08:00:00Z', trend: 'stable' },
];

const mockPatient: PatientDetailResponse = {
  mpi_id: 'MPI-001',
  patient_name: 'Maria Silva Santos',
  bed: 'UTI-01',
  unit: 'UTI Adulto',
  vitals: mockVitals,
  scores: mockScores,
  active_pathways_count: 3,
};

const meta: Meta<typeof PatientHeader> = {
  title: 'Patient/PatientHeader',
  component: PatientHeader,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof PatientHeader>;

export const Default: Story = {
  args: {
    patient: mockPatient,
  },
};

export const NormalScores: Story = {
  args: {
    patient: {
      ...mockPatient,
      mpi_id: 'MPI-002',
      patient_name: 'Ana Beatriz Costa',
      scores: [
        { name: 'MEWS', value: 1, measured_at: '2026-07-09T12:00:00Z', trend: 'stable' },
        { name: 'NEWS2', value: 2, measured_at: '2026-07-09T12:00:00Z', trend: 'stable' },
      ],
    },
  },
};

export const NoScores: Story = {
  args: {
    patient: {
      ...mockPatient,
      mpi_id: 'MPI-003',
      patient_name: 'Carlos Eduardo Lima',
      scores: [],
    },
  },
};

export const LongName: Story = {
  args: {
    patient: {
      ...mockPatient,
      mpi_id: 'MPI-004',
      patient_name: 'Francisco de Assis Albuquerque Nascimento',
      bed: 'ENF-12',
      unit: 'Enfermaria Cirúrgica',
    },
  },
};
