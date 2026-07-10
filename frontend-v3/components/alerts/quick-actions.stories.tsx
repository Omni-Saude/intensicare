import type { Meta, StoryObj } from '@storybook/react';
import { QuickActions } from './quick-actions';
import type { AlertInfo } from '@/lib/api';

const pendingAlert: AlertInfo = {
  id: 1,
  type: 'threshold',
  severity: 'critical',
  title: 'Lactato Elevado',
  message: 'Lactato sérico 4.8 mmol/L',
  mpi_id: 'MPI-001',
  patient_name: 'Maria Silva',
  pathway_name: 'Sepse',
  created_at: '2026-07-09T07:30:00Z',
};

const resolvedAlert: AlertInfo = {
  ...pendingAlert,
  id: 2,
  severity: 'watch',
  resolved_at: '2026-07-09T08:00:00Z',
  resolution: 'Paciente estabilizado',
};

const meta: Meta<typeof QuickActions> = {
  title: 'Alerts/QuickActions',
  component: QuickActions,
  tags: ['autodocs'],
  argTypes: {
    alert: { control: 'object', description: 'Dados do alerta (AlertInfo)' },
    onAction: { action: 'action', description: 'Callback de ação realizada com alerta atualizado' },
    onError: { action: 'error', description: 'Callback de erro' },
  },
};

export default meta;
type Story = StoryObj<typeof QuickActions>;

export const Pending: Story = {
  args: { alert: pendingAlert },
};

export const Resolved: Story = {
  args: { alert: resolvedAlert },
};
