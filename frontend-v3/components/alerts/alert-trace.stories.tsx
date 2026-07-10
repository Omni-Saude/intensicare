import type { Meta, StoryObj } from '@storybook/react';
import { AlertTrace } from './alert-trace';
import type { AlertInfo } from '@/lib/api';

const mockAlert: AlertInfo = {
  id: 42,
  type: 'threshold',
  severity: 'critical',
  title: 'Lactato > 4.0 mmol/L',
  message: 'Lactato sérico 4.8 mmol/L — acima do limiar crítico para paciente em protocolo de sepse.',
  mpi_id: 'MPI-001',
  patient_name: 'Maria Silva',
  pathway_name: 'Sepse',
  created_at: '2026-07-09T07:30:00Z',
};

const alertNoPathway: AlertInfo = {
  ...mockAlert,
  id: 43,
  pathway_name: undefined,
  message: 'Alerta sem associação a trilha clínica específica.',
};

const meta: Meta<typeof AlertTrace> = {
  title: 'Alerts/AlertTrace',
  component: AlertTrace,
  tags: ['autodocs'],
  argTypes: {
    alert: { control: 'object', description: 'Dados do alerta para rastreabilidade (AlertInfo)' },
  },
};

export default meta;
type Story = StoryObj<typeof AlertTrace>;

export const Default: Story = {
  args: { alert: mockAlert },
};

export const NoPathwayAssociated: Story = {
  args: { alert: alertNoPathway },
};
