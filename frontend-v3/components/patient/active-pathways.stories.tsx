import type { Meta, StoryObj } from '@storybook/react';
import type { PatientPathway, Pathway, PathwayState, PathwayCriteria } from '@/lib/api';
import { ActivePathways } from './active-pathways';

const mockPathwayDefinition: Pathway = {
  id: 10,
  name: 'Sepse',
  slug: 'sepsis',
  description: 'Protocolo de manejo de sepse',
  states: [],
};

const mockState: PathwayState = {
  id: 'active',
  name: 'Triagem Inicial',
  order: 1,
  description: 'Avaliação inicial do paciente',
};

const mockCriteria: PathwayCriteria[] = [
  { id: 'c1', name: 'Lactato > 2 mmol/L', category: 'lab', met: true, value: '3.2', unit: 'mmol/L' },
  { id: 'c2', name: 'Hipotensão (PAS < 90)', category: 'vital', met: true, value: '85', unit: 'mmHg' },
  { id: 'c3', name: 'FC > 90 bpm', category: 'vital', met: false, value: '72', unit: 'bpm' },
  { id: 'c4', name: 'FR > 20 rpm', category: 'vital', met: true, value: '24', unit: 'rpm' },
  { id: 'c5', name: 'Hemocultura positiva', category: 'lab', met: false },
];

const mockPathways: PatientPathway[] = [
  {
    id: 1,
    mpi_id: 'MPI-001',
    pathway: { ...mockPathwayDefinition, id: 10, name: 'Sepse', slug: 'sepsis' },
    current_state: mockState,
    criteria: mockCriteria,
    status: 'active',
    severity: 'urgent',
    enrolled_at: '2026-06-15T10:30:00Z',
    enrolled_by: 'Dr. Silva',
    updated_at: '2026-07-09T08:00:00Z',
  },
  {
    id: 2,
    mpi_id: 'MPI-001',
    pathway: { ...mockPathwayDefinition, id: 11, name: 'IRA (Lesão Renal Aguda)', slug: 'aki' },
    current_state: { id: 'monitoring', name: 'Monitoramento', order: 2, description: 'Acompanhamento da função renal' },
    criteria: [
      { id: 'c6', name: 'Creatinina > 1.5x basal', category: 'lab', met: true, value: '2.1', unit: 'mg/dL' },
      { id: 'c7', name: 'Débito urinário < 0.5 mL/kg/h', category: 'output', met: false },
    ],
    status: 'active',
    severity: 'watch',
    enrolled_at: '2026-07-08T14:00:00Z',
    enrolled_by: 'Dr. Silva',
    updated_at: '2026-07-09T08:00:00Z',
  },
  {
    id: 3,
    mpi_id: 'MPI-001',
    pathway: { ...mockPathwayDefinition, id: 12, name: 'Delirium', slug: 'delirium' },
    current_state: { id: 'screening', name: 'Rastreamento', order: 1, description: 'Avaliação com CAM-ICU' },
    criteria: [
      { id: 'c8', name: 'CAM-ICU positivo', category: 'assessment', met: true },
    ],
    status: 'active',
    severity: 'normal',
    enrolled_at: '2026-07-09T08:00:00Z',
    enrolled_by: 'Enf. Costa',
    updated_at: '2026-07-09T08:00:00Z',
  },
];

const meta: Meta<typeof ActivePathways> = {
  title: 'Patient/ActivePathways',
  component: ActivePathways,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ActivePathways>;

export const Default: Story = {
  args: {
    pathways: mockPathways,
  },
};

export const Loading: Story = {
  args: {
    pathways: [],
    isLoading: true,
  },
};

export const ErrorState: Story = {
  args: {
    pathways: [],
    error: 'Falha ao carregar trilhas',
  },
};

export const Empty: Story = {
  args: {
    pathways: [],
  },
};

export const SinglePathway: Story = {
  args: {
    pathways: [mockPathways[0]],
  },
};
