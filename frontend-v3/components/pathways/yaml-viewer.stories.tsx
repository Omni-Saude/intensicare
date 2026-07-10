import type { Meta, StoryObj } from '@storybook/react';
import { YamlViewer } from './yaml-viewer';
import type { Pathway } from '@/lib/api';

const mockPathway: Pathway = {
  id: 1,
  name: 'Sepse',
  slug: 'sepsis',
  description: 'Protocolo de manejo de sepse',
  active: true,
  states: [
    { id: 'triage', name: 'Triagem Inicial', order: 1, description: 'Avaliação dos critérios SIRS e qSOFA' },
    { id: 'diagnosis', name: 'Diagnóstico', order: 2, description: 'Coleta de exames e confirmação do foco infeccioso' },
    { id: 'treatment', name: 'Tratamento', order: 3, description: 'Antibioticoterapia e ressuscitação volêmica' },
    { id: 'discharge', name: 'Alta', order: 4, description: 'Descontinuação de medidas e alta da UTI', is_terminal: true },
  ],
  criteria: [
    { id: 'c1', name: 'Lactato > 2 mmol/L', category: 'lab', unit: 'mmol/L', normal_range: '0.5–1.6', alert_threshold: '≥2.0' },
    { id: 'c2', name: 'Hipotensão (PAS < 90)', category: 'vital', unit: 'mmHg', normal_range: '90–120', alert_threshold: '≥90' },
  ],
};

const meta: Meta<typeof YamlViewer> = {
  title: 'Pathways/YamlViewer',
  component: YamlViewer,
  tags: ['autodocs'],
  argTypes: {
    pathway: { control: 'object', description: 'Dados da trilha (Pathway) para gerar YAML' },
    isLoading: { control: 'boolean', description: 'Estado de carregamento' },
    error: { control: 'text', description: 'Mensagem de erro' },
  },
};

export default meta;
type Story = StoryObj<typeof YamlViewer>;

export const Default: Story = {
  args: { pathway: mockPathway, isLoading: false },
};

export const Loading: Story = {
  args: { pathway: null, isLoading: true },
};

export const ErrorState: Story = {
  args: { pathway: null, isLoading: false, error: 'Falha ao carregar a definição YAML da trilha' },
};

export const Empty: Story = {
  args: { pathway: null, isLoading: false },
};
