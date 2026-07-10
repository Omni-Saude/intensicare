import type { Meta, StoryObj } from '@storybook/react';
import { PathwayCard } from '../components/patient/pathway-card';
import type { PatientPathway } from '../lib/api';

const mockPathway: PatientPathway = {
  id: 1,
  mpi_id: 'MPI-001',
  pathway: {
    id: 10,
    name: 'Sepse',
    slug: 'sepsis',
    description: 'Protocolo de manejo de sepse',
    states: [],
  },
  current_state: {
    id: 'active',
    name: 'Triagem Inicial',
    order: 1,
    description: 'Avaliação inicial do paciente',
  },
  criteria: [
    { id: 'c1', name: 'Lactato > 2 mmol/L', category: 'lab', met: true, value: '3.2', unit: 'mmol/L' },
    { id: 'c2', name: 'Hipotensão (PAS < 90)', category: 'vital', met: true, value: '85', unit: 'mmHg' },
    { id: 'c3', name: 'FC > 90 bpm', category: 'vital', met: false, value: '72', unit: 'bpm' },
    { id: 'c4', name: 'FR > 20 rpm', category: 'vital', met: true, value: '24', unit: 'rpm' },
    { id: 'c5', name: 'Hemocultura positiva', category: 'lab', met: false },
  ],
  status: 'active',
  severity: 'urgent',
  enrolled_at: '2026-06-15T10:30:00Z',
  enrolled_by: 'Dr. Silva',
  updated_at: '2026-07-09T08:00:00Z',
};

const meta: Meta<typeof PathwayCard> = {
  title: 'Patient/PathwayCard',
  component: PathwayCard,
  tags: ['autodocs'],
  parameters: {
    nextjs: {
      appDirectory: true,
    },
  },
  argTypes: {
    pathway: {
      control: 'object',
      description: 'Dados da trilha do paciente (PatientPathway)',
    },
  },
};

export default meta;
type Story = StoryObj<typeof PathwayCard>;

export const Default: Story = {
  args: {
    pathway: mockPathway,
  },
};

export const NormalSeverity: Story = {
  args: {
    pathway: {
      ...mockPathway,
      severity: 'normal',
      id: 2,
    },
  },
};

export const CriticalSeverity: Story = {
  args: {
    pathway: {
      ...mockPathway,
      severity: 'critical',
      id: 3,
    },
  },
};

export const NoCriteria: Story = {
  args: {
    pathway: {
      ...mockPathway,
      criteria: [],
      id: 4,
    },
  },
};
