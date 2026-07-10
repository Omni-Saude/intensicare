import type { Meta, StoryObj } from '@storybook/react';
import type { PatientBedSummary } from '@/lib/api';
import { BedCard } from './bed-card';

const mockPatient: PatientBedSummary = {
  mpi_id: 'MPI-001',
  patient_name: 'Maria Silva Santos',
  bed: 'UTI-01',
  unit: 'UTI Adulto',
  severity: 'urgent',
  mews: 6,
  news2: 7,
  last_vital_at: new Date(Date.now() - 5 * 60_000).toISOString(),
  active_pathways: [
    { slug: 'sepsis', severity: 'critical' },
    { slug: 'aki', severity: 'urgent' },
  ],
  vitals: { hr: 112, spo2: 91, bp_sys: 88, bp_dia: 56 },
};

const meta: Meta<typeof BedCard> = {
  title: 'Dashboard/BedCard',
  component: BedCard,
  tags: ['autodocs'],
  argTypes: {
    onClick: { action: 'clicked', description: 'Callback ao clicar no card' },
  },
};

export default meta;
type Story = StoryObj<typeof BedCard>;

export const Urgent: Story = {
  args: {
    patient: mockPatient,
    onClick: () => console.log('Clicked card'),
  },
};

export const Critical: Story = {
  args: {
    patient: {
      ...mockPatient,
      mpi_id: 'MPI-002',
      patient_name: 'João Pereira Oliveira',
      severity: 'critical',
      mews: 8,
      news2: 9,
      last_vital_at: new Date(Date.now() - 2 * 60_000).toISOString(),
    },
    onClick: () => console.log('Clicked card'),
  },
};

export const Normal: Story = {
  args: {
    patient: {
      ...mockPatient,
      mpi_id: 'MPI-003',
      patient_name: 'Ana Beatriz Costa',
      severity: 'normal',
      mews: 1,
      news2: 2,
      active_pathways: [],
      vitals: { hr: 72, spo2: 98, bp_sys: 122, bp_dia: 78 },
      last_vital_at: new Date(Date.now() - 8 * 60_000).toISOString(),
    },
    onClick: () => console.log('Clicked card'),
  },
};

export const StaleVitals: Story = {
  args: {
    patient: {
      ...mockPatient,
      mpi_id: 'MPI-004',
      patient_name: 'Carlos Eduardo Lima',
      severity: 'watch',
      mews: 3,
      news2: 4,
      last_vital_at: new Date(Date.now() - 120 * 60_000).toISOString(),
      active_pathways: [{ slug: 'post-op', severity: 'watch' }],
    },
    onClick: () => console.log('Clicked card'),
  },
};

export const MultiplePathways: Story = {
  args: {
    patient: {
      ...mockPatient,
      mpi_id: 'MPI-005',
      patient_name: 'Fernanda Souza Ramos',
      severity: 'urgent',
      mews: 5,
      news2: 6,
      active_pathways: [
        { slug: 'sepsis', severity: 'urgent' },
        { slug: 'aki', severity: 'watch' },
        { slug: 'delirium', severity: 'normal' },
        { slug: 'vap', severity: 'urgent' },
      ],
    },
    onClick: () => console.log('Clicked card'),
  },
};
