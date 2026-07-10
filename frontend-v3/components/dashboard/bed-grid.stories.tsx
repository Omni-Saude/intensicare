import type { Meta, StoryObj } from '@storybook/react';
import type { PatientBedSummary } from '@/lib/api';
import { BedGrid } from './bed-grid';

const mockPatients: PatientBedSummary[] = [
  {
    mpi_id: 'MPI-001',
    patient_name: 'Maria Silva Santos',
    bed: 'UTI-01',
    unit: 'UTI Adulto',
    severity: 'critical',
    mews: 7,
    news2: 8,
    last_vital_at: new Date(Date.now() - 5 * 60_000).toISOString(),
    active_pathways: [
      { slug: 'sepsis', severity: 'critical' },
      { slug: 'aki', severity: 'urgent' },
    ],
    vitals: { hr: 112, spo2: 91, bp_sys: 88, bp_dia: 56 },
  },
  {
    mpi_id: 'MPI-002',
    patient_name: 'João Pereira Oliveira',
    bed: 'UTI-02',
    unit: 'UTI Adulto',
    severity: 'urgent',
    mews: 5,
    news2: 6,
    last_vital_at: new Date(Date.now() - 15 * 60_000).toISOString(),
    active_pathways: [
      { slug: 'respiratory-failure', severity: 'urgent' },
    ],
    vitals: { hr: 98, spo2: 94, bp_sys: 130, bp_dia: 82 },
  },
  {
    mpi_id: 'MPI-003',
    patient_name: 'Ana Beatriz Costa',
    bed: 'UTI-03',
    unit: 'UTI Adulto',
    severity: 'watch',
    mews: 3,
    news2: 4,
    last_vital_at: new Date(Date.now() - 10 * 60_000).toISOString(),
    active_pathways: [
      { slug: 'post-op', severity: 'watch' },
    ],
    vitals: { hr: 82, spo2: 97, bp_sys: 118, bp_dia: 74 },
  },
  {
    mpi_id: 'MPI-004',
    patient_name: 'Carlos Eduardo Lima',
    bed: 'ENF-04',
    unit: 'Enfermaria',
    severity: 'normal',
    mews: 1,
    news2: 2,
    last_vital_at: new Date(Date.now() - 8 * 60_000).toISOString(),
    active_pathways: [],
    vitals: { hr: 72, spo2: 98, bp_sys: 122, bp_dia: 78 },
  },
  {
    mpi_id: 'MPI-005',
    patient_name: 'Fernanda Souza Ramos',
    bed: 'UTI-05',
    unit: 'UTI Adulto',
    severity: 'urgent',
    mews: 6,
    news2: 7,
    last_vital_at: new Date(Date.now() - 20 * 60_000).toISOString(),
    active_pathways: [
      { slug: 'sepsis', severity: 'urgent' },
      { slug: 'aki', severity: 'watch' },
      { slug: 'delirium', severity: 'watch' },
      { slug: 'vap', severity: 'urgent' },
    ],
    vitals: { hr: 105, spo2: 93, bp_sys: 100, bp_dia: 62 },
  },
];

const meta: Meta<typeof BedGrid> = {
  title: 'Dashboard/BedGrid',
  component: BedGrid,
  tags: ['autodocs'],
  argTypes: {
    onSelect: { action: 'selected', description: 'Callback ao selecionar um leito' },
  },
};

export default meta;
type Story = StoryObj<typeof BedGrid>;

export const Default: Story = {
  args: {
    patients: mockPatients,
    onSelect: (mpiId: string) => console.log('Selected:', mpiId),
  },
};

export const Loading: Story = {
  args: {
    patients: [],
    onSelect: (mpiId: string) => console.log('Selected:', mpiId),
    isLoading: true,
  },
};

export const Empty: Story = {
  args: {
    patients: [],
    onSelect: (mpiId: string) => console.log('Selected:', mpiId),
  },
};

export const ErrorState: Story = {
  args: {
    patients: [],
    onSelect: (mpiId: string) => console.log('Selected:', mpiId),
    error: new Error('Falha na conexão com o servidor'),
    onRetry: () => console.log('Retrying...'),
  },
};
