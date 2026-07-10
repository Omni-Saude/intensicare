import type { Meta, StoryObj } from '@storybook/react';
import { AlertRow } from './alert-row';
import type { AlertInfo } from '@/lib/api';

const baseAlert: AlertInfo = {
  id: 1,
  type: 'threshold',
  severity: 'critical',
  title: 'Lactato Elevado',
  message: 'Lactato sérico 4.8 mmol/L — acima do limiar crítico de 4.0 mmol/L para paciente em protocolo de sepse.',
  mpi_id: 'MPI-001',
  patient_name: 'Maria Silva',
  pathway_name: 'Sepse',
  created_at: '2026-07-09T07:30:00Z',
};

const resolvedAlert: AlertInfo = {
  ...baseAlert,
  id: 3,
  severity: 'watch',
  title: 'Hemocultura Pendente',
  message: 'Hemoculturas não coletadas dentro da janela de 1 hora após identificação de sepse.',
  resolved_at: '2026-07-09T07:00:00Z',
  resolution: 'Coletado com atraso — antibioticoterapia já iniciada',
};

const acknowledgedAlert: AlertInfo = {
  ...baseAlert,
  id: 2,
  severity: 'urgent',
  title: 'PAM < 65 mmHg',
  message: 'Pressão arterial média abaixo de 65 mmHg por mais de 15 minutos.',
  acknowledged_at: '2026-07-09T08:05:00Z',
};

const meta: Meta<typeof AlertRow> = {
  title: 'Alerts/AlertRow',
  component: AlertRow,
  tags: ['autodocs'],
  argTypes: {
    alert: { control: 'object', description: 'Dados do alerta (AlertInfo)' },
    onAlertUpdate: { action: 'alertUpdated', description: 'Callback de atualização do alerta' },
    onError: { action: 'error', description: 'Callback de erro' },
  },
};

export default meta;
type Story = StoryObj<typeof AlertRow>;

export const Default: Story = {
  args: { alert: baseAlert },
};

export const Acknowledged: Story = {
  args: { alert: acknowledgedAlert },
};

export const Resolved: Story = {
  args: { alert: resolvedAlert },
};

export const NoPatientLink: Story = {
  args: { alert: { ...baseAlert, id: 5, mpi_id: undefined, patient_name: undefined } },
};

export const NoPathwayLink: Story = {
  args: { alert: { ...baseAlert, id: 6, pathway_name: undefined } },
};
