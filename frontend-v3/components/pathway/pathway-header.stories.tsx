import type { Meta, StoryObj } from '@storybook/react';
import { PathwayHeader } from './pathway-header';

const meta: Meta<typeof PathwayHeader> = {
  title: 'Pathway/PathwayHeader',
  component: PathwayHeader,
  tags: ['autodocs'],
  parameters: {
    nextjs: {
      appDirectory: true,
    },
  },
  argTypes: {
    pathwayName: { control: 'text', description: 'Nome da trilha clínica' },
    patientName: { control: 'text', description: 'Nome do paciente' },
    mpiId: { control: 'text', description: 'ID do paciente (MPI)' },
    currentState: { control: 'text', description: 'Estado atual do paciente na trilha' },
    severity: { control: 'select', options: ['normal', 'watch', 'urgent', 'critical'], description: 'Nível de severidade' },
    trend: { control: 'select', options: ['improving', 'stable', 'worsening', 'none'], description: 'Tendência clínica' },
  },
};

export default meta;
type Story = StoryObj<typeof PathwayHeader>;

export const Default: Story = {
  args: {
    pathwayName: 'Sepse',
    patientName: 'Maria Silva',
    mpiId: 'MPI-001',
    currentState: 'Tratamento',
    severity: 'urgent',
    trend: 'improving',
  },
};

export const CriticalWorsening: Story = {
  args: {
    pathwayName: 'DVA',
    patientName: 'João Santos',
    mpiId: 'MPI-042',
    currentState: 'Diagnóstico',
    severity: 'critical',
    trend: 'worsening',
  },
};

export const NormalStable: Story = {
  args: {
    pathwayName: 'Monitorização Pós-Cirúrgica',
    patientName: 'Ana Costa',
    mpiId: 'MPI-103',
    currentState: 'Monitorização',
    severity: 'normal',
    trend: 'stable',
  },
};

export const WatchNoTrend: Story = {
  args: {
    pathwayName: 'Insuficiência Respiratória',
    patientName: 'Carlos Lima',
    mpiId: 'MPI-207',
    currentState: 'Triagem Inicial',
    severity: 'watch',
    trend: 'none',
  },
};
