import type { Meta, StoryObj } from '@storybook/react';
import { AlertTable } from './alert-table';
import type { AlertInfo } from '@/lib/api';

const mockAlerts: AlertInfo[] = [
  {
    id: 1,
    type: 'threshold',
    severity: 'critical',
    title: 'Lactato Elevado',
    message: 'Lactato sérico 4.8 mmol/L — acima do limiar crítico de 4.0 mmol/L para paciente em protocolo de sepse.',
    mpi_id: 'MPI-001',
    patient_name: 'Maria Silva',
    pathway_name: 'Sepse',
    created_at: '2026-07-09T07:30:00Z',
    acknowledged_at: '2026-07-09T07:35:00Z',
  },
  {
    id: 2,
    type: 'deviation',
    severity: 'urgent',
    title: 'PAM < 65 mmHg',
    message: 'Pressão arterial média abaixo de 65 mmHg por mais de 15 minutos. Iniciar vasopressor.',
    mpi_id: 'MPI-042',
    patient_name: 'João Santos',
    pathway_name: 'DVA',
    created_at: '2026-07-09T08:00:00Z',
  },
  {
    id: 3,
    type: 'missing_data',
    severity: 'watch',
    title: 'Hemocultura Pendente',
    message: 'Hemoculturas não coletadas dentro da janela de 1 hora após identificação de sepse.',
    mpi_id: 'MPI-015',
    patient_name: 'Ana Costa',
    pathway_name: 'Sepse',
    created_at: '2026-07-09T06:15:00Z',
    resolved_at: '2026-07-09T07:00:00Z',
    resolution: 'Coletado com atraso — antibioticoterapia já iniciada',
  },
  {
    id: 4,
    type: 'info',
    severity: 'normal',
    title: 'Critérios Atualizados',
    message: 'Critérios da trilha de Monitorização Pós-Cirúrgica foram atualizados. Revisar protocolo.',
    mpi_id: 'MPI-207',
    patient_name: 'Carlos Lima',
    pathway_name: 'Monitorização Pós-Cirúrgica',
    created_at: '2026-07-09T08:30:00Z',
  },
];

const meta: Meta<typeof AlertTable> = {
  title: 'Alerts/AlertTable',
  component: AlertTable,
  tags: ['autodocs'],
  argTypes: {
    alerts: { control: 'object', description: 'Lista de alertas (AlertInfo[])' },
    isLoading: { control: 'boolean', description: 'Estado de carregamento' },
    isEmpty: { control: 'boolean', description: 'Estado vazio (sem alertas)' },
    error: { control: 'text', description: 'Mensagem de erro' },
    onAlertUpdate: { action: 'alertUpdated', description: 'Callback de atualização de alerta' },
    onError: { action: 'error', description: 'Callback de erro' },
  },
};

export default meta;
type Story = StoryObj<typeof AlertTable>;

export const Default: Story = {
  args: { alerts: mockAlerts, isLoading: false, isEmpty: false, error: null },
};

export const Loading: Story = {
  args: { alerts: [], isLoading: true, isEmpty: false, error: null },
};

export const ErrorState: Story = {
  args: { alerts: [], isLoading: false, isEmpty: false, error: 'Erro de conexão com o servidor' },
};

export const Empty: Story = {
  args: { alerts: [], isLoading: false, isEmpty: true, error: null },
};
