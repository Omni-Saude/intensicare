import type { Meta, StoryObj } from '@storybook/react';
import type { AlertInfo } from '@/lib/api';
import { AlertsPanel } from './alerts-panel';

const mockAlerts: AlertInfo[] = [
  {
    id: 1,
    type: 'score_increase',
    severity: 'critical',
    title: 'MEWS elevado (7 → 9)',
    message: 'Paciente apresentou piora clínica significativa nas últimas 2 horas. MEWS subiu de 7 para 9 com hipotensão refratária.',
    mpi_id: 'MPI-001',
    pathway_name: 'Sepse',
    created_at: '2026-07-09T12:00:00Z',
  },
  {
    id: 2,
    type: 'criteria_met',
    severity: 'urgent',
    title: 'Critérios de IRA atendidos',
    message: 'Creatinina 2.1 mg/dL (1.8x basal) e débito urinário reduzido. Iniciar protocolo de IRA.',
    mpi_id: 'MPI-001',
    pathway_name: 'IRA',
    created_at: '2026-07-09T10:30:00Z',
  },
  {
    id: 3,
    type: 'vital_out_of_range',
    severity: 'watch',
    title: 'SpO₂ abaixo do limiar',
    message: 'Saturação de O₂ caiu para 91% em ar ambiente. Considerar oxigenoterapia.',
    mpi_id: 'MPI-001',
    created_at: '2026-07-09T11:15:00Z',
  },
  {
    id: 4,
    type: 'protocol_step',
    severity: 'normal',
    title: 'Etapa do protocolo concluída',
    message: 'Coleta de hemoculturas realizada conforme protocolo de sepse.',
    mpi_id: 'MPI-001',
    pathway_name: 'Sepse',
    created_at: '2026-07-09T09:00:00Z',
    acknowledged_at: '2026-07-09T09:15:00Z',
  },
];

const meta: Meta<typeof AlertsPanel> = {
  title: 'Patient/AlertsPanel',
  component: AlertsPanel,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof AlertsPanel>;

export const Default: Story = {
  args: {
    alerts: mockAlerts,
    onAcknowledge: async (id: number) => console.log('Acknowledged:', id),
    onEscalate: async (id: number) => console.log('Escalated:', id),
  },
};

export const Loading: Story = {
  args: {
    alerts: [],
    isLoading: true,
  },
};

export const ErrorState: Story = {
  args: {
    alerts: [],
    error: 'Falha ao carregar alertas',
  },
};

export const Empty: Story = {
  args: {
    alerts: [],
  },
};

export const WithoutActions: Story = {
  args: {
    alerts: mockAlerts,
  },
};
