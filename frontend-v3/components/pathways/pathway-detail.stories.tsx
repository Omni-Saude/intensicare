import type { Meta, StoryObj } from '@storybook/react';
import { PathwayDetail } from './pathway-detail';
import type { Pathway } from '@/lib/api';

const mockPathway: Pathway = {
  id: 1,
  name: 'Sepse',
  slug: 'sepsis',
  description: 'Protocolo de manejo de sepse — identificação precoce e tratamento guiado por metas nas primeiras 6 horas.',
  active: true,
  states: [
    { id: 'triage', name: 'Triagem Inicial', order: 1, description: 'Avaliação dos critérios SIRS e qSOFA' },
    { id: 'diagnosis', name: 'Diagnóstico', order: 2, description: 'Coleta de exames e confirmação do foco infeccioso' },
    { id: 'treatment', name: 'Tratamento', order: 3, description: 'Antibioticoterapia e ressuscitação volêmica' },
    { id: 'monitoring', name: 'Monitorização', order: 4, description: 'Reavaliação seriada de lactato e SvO2' },
    { id: 'discharge', name: 'Alta', order: 5, description: 'Descontinuação de medidas e alta da UTI', is_terminal: true },
  ],
  criteria: [
    { id: 'c1', name: 'Lactato > 2 mmol/L', category: 'lab', description: 'Hiperlactatemia indica hipoperfusão tecidual', unit: 'mmol/L', normal_range: '0.5–1.6', alert_threshold: '≥2.0' },
    { id: 'c2', name: 'Hipotensão (PAS < 90)', category: 'vital', description: 'Pressão arterial sistólica baixa', unit: 'mmHg', normal_range: '90–120', alert_threshold: '≥90' },
    { id: 'c3', name: 'FC > 90 bpm', category: 'vital', description: 'Taquicardia como resposta compensatória', unit: 'bpm', normal_range: '60–100' },
    { id: 'c4', name: 'Hemocultura positiva', category: 'lab', description: 'Isolamento de patógeno em hemocultura' },
    { id: 'c5', name: 'PCR elevada', category: 'lab', description: 'Proteína C reativa como marcador inflamatório', unit: 'mg/L', normal_range: '<5', alert_threshold: '≥50' },
  ],
};

const minimalPathway: Pathway = {
  id: 2,
  name: 'Trilha Mínima',
  slug: 'minimal',
  active: true,
  states: [],
  criteria: [],
};

const meta: Meta<typeof PathwayDetail> = {
  title: 'Pathways/PathwayDetail',
  component: PathwayDetail,
  tags: ['autodocs'],
  parameters: {
    nextjs: {
      appDirectory: true,
    },
  },
  argTypes: {
    pathway: { control: 'object', description: 'Dados completos da trilha clínica (Pathway)' },
  },
};

export default meta;
type Story = StoryObj<typeof PathwayDetail>;

export const Default: Story = {
  args: { pathway: mockPathway },
};

export const MinimalPathway: Story = {
  args: { pathway: minimalPathway },
};

export const NoDescription: Story = {
  args: { pathway: { ...mockPathway, id: 3, description: undefined, states: mockPathway.states.slice(0, 2) } },
};

export const NoCriteria: Story = {
  args: { pathway: { ...mockPathway, id: 4, criteria: [] } },
};
