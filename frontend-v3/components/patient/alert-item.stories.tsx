import type { Meta, StoryObj } from '@storybook/react';
import type { AlertInfo } from '@/lib/api';
import { AlertItem } from './alert-item';

const mockAlert: AlertInfo = {
  id: 1,
  type: 'score_increase',
  severity: 'critical',
  title: 'MEWS elevado (7 → 9)',
  message: 'Paciente apresentou piora clínica significativa nas últimas 2 horas. MEWS subiu de 7 para 9 com hipotensão refratária e taquicardia persistente.',
  mpi_id: 'MPI-001',
  pathway_name: 'Sepse',
  created_at: '2026-07-09T12:00:00Z',
};

const meta: Meta<typeof AlertItem> = {
  title: 'Patient/AlertItem',
  component: AlertItem,
  tags: ['autodocs'],
  argTypes: {
    onAcknowledge: { action: 'acknowledged', description: 'Confirmar alerta' },
    onEscalate: { action: 'escalated', description: 'Escalar alerta' },
  },
};

export default meta;
type Story = StoryObj<typeof AlertItem>;

export const Critical: Story = {
  args: {
    alert: mockAlert,
    onAcknowledge: (id: number) => console.log('Acknowledged:', id),
    onEscalate: (id: number) => console.log('Escalated:', id),
  },
};

export const Urgent: Story = {
  args: {
    alert: {
      ...mockAlert,
      id: 2,
      severity: 'urgent',
      title: 'Critérios de IRA atendidos',
      message: 'Creatinina 2.1 mg/dL (1.8x basal) e débito urinário reduzido.',
      pathway_name: 'IRA',
      created_at: '2026-07-09T10:30:00Z',
    },
    onAcknowledge: (id: number) => console.log('Acknowledged:', id),
    onEscalate: (id: number) => console.log('Escalated:', id),
  },
};

export const Watch: Story = {
  args: {
    alert: {
      ...mockAlert,
      id: 3,
      severity: 'watch',
      title: 'SpO₂ abaixo do limiar',
      message: 'Saturação de O₂ caiu para 91% em ar ambiente.',
      created_at: '2026-07-09T11:15:00Z',
      pathway_name: undefined,
    },
  },
};

export const Acknowledged: Story = {
  args: {
    alert: {
      ...mockAlert,
      id: 4,
      severity: 'urgent',
      title: 'Alerta reconhecido',
      message: 'Este alerta já foi reconhecido pela equipe.',
      acknowledged_at: '2026-07-09T12:15:00Z',
    },
  },
};

export const Resolved: Story = {
  args: {
    alert: {
      ...mockAlert,
      id: 5,
      severity: 'normal',
      title: 'Alerta resolvido',
      message: 'Paciente estabilizado após intervenção.',
      resolved_at: '2026-07-09T14:00:00Z',
      resolved_by: 'Dr. Silva',
      resolution: 'Administrado fluidos IV e iniciado antibiótico.',
    },
  },
};

export const Disabled: Story = {
  args: {
    alert: mockAlert,
    onAcknowledge: (id: number) => console.log('Acknowledged:', id),
    onEscalate: (id: number) => console.log('Escalated:', id),
    disabled: true,
  },
};
