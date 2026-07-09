import type { Meta, StoryObj } from '@storybook/react';
import ScoreDisplay from './ScoreDisplay';

// ─── Mock Data Factories ───────────────────────────────────────────────────

const sofaDetails = [
  { label: 'Respiratório', score: 2, max: 4 },
  { label: 'Coagulação', score: 1, max: 4 },
  { label: 'Hepático', score: 1, max: 4 },
  { label: 'Cardiovascular', score: 3, max: 4 },
  { label: 'Neurológico', score: 2, max: 4 },
  { label: 'Renal', score: 3, max: 4 },
];

const glasgowDetails = [
  { label: 'Abertura Ocular', score: 3, max: 4 },
  { label: 'Resposta Verbal', score: 4, max: 5 },
  { label: 'Resposta Motora', score: 5, max: 6 },
];

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof ScoreDisplay> = {
  title: 'Components/ScoreDisplay',
  component: ScoreDisplay,
  tags: ['autodocs'],
  argTypes: {
    formType: {
      control: 'select',
      options: ['sofa', 'glasgow', 'rass', 'cam_icu', 'bps_nrs'],
      description: 'Tipo de formulário clínico (SOFA, Glasgow, RASS, CAM-ICU, BPS/NRS)',
    },
    score: {
      control: { type: 'number', min: -5, max: 24 },
      description: 'Valor do escore',
    },
    maxScore: {
      control: { type: 'number', min: 1, max: 24 },
      description: 'Valor máximo possível do escore',
    },
    label: {
      control: 'text',
      description: 'Label do escore (ex: "SOFA", "Glasgow", "RASS")',
    },
    details: {
      control: 'object',
      description: 'Detalhamento dos sub-escores (para SOFA e Glasgow)',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ScoreDisplay>;

// ─── Stories ───────────────────────────────────────────────────────────────

export const SOFA: Story = {
  args: {
    formType: 'sofa',
    score: 12,
    maxScore: 24,
    label: 'SOFA',
    details: sofaDetails,
  },
  parameters: {
    docs: {
      description: {
        story:
          'SOFA 12/24 — disfunção orgânica grave. Barra de progresso laranja com detalhamento dos 6 sistemas.',
      },
    },
  },
};

export const Glasgow: Story = {
  args: {
    formType: 'glasgow',
    score: 14,
    maxScore: 15,
    label: 'Glasgow',
    details: glasgowDetails,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Glasgow 14/15 — nível de consciência normal. Escore verde com detalhamento dos 3 componentes.',
      },
    },
  },
};

export const RASS: Story = {
  args: {
    formType: 'rass',
    score: -2,
    maxScore: 4,
    label: 'RASS',
  },
  parameters: {
    docs: {
      description: {
        story:
          'RASS -2 (Sedação Leve) — exibe escala visual RASS de -5 a +4 com destaque para o valor atual.',
      },
    },
  },
};

export const Critical: Story = {
  args: {
    formType: 'sofa',
    score: 18,
    maxScore: 24,
    label: 'SOFA',
    details: [
      { label: 'Respiratório', score: 4, max: 4 },
      { label: 'Coagulação', score: 3, max: 4 },
      { label: 'Hepático', score: 2, max: 4 },
      { label: 'Cardiovascular', score: 4, max: 4 },
      { label: 'Neurológico', score: 3, max: 4 },
      { label: 'Renal', score: 2, max: 4 },
    ],
  },
  parameters: {
    docs: {
      description: {
        story:
          'SOFA 18/24 — falência múltipla de órgãos. Alerta crítico com banner de atenção. Escore e detalhamento em vermelho.',
      },
    },
  },
};

export const GlasgowGrave: Story = {
  args: {
    formType: 'glasgow',
    score: 6,
    maxScore: 15,
    label: 'Glasgow',
    details: [
      { label: 'Abertura Ocular', score: 1, max: 4 },
      { label: 'Resposta Verbal', score: 2, max: 5 },
      { label: 'Resposta Motora', score: 3, max: 6 },
    ],
  },
  parameters: {
    docs: {
      description: {
        story:
          'Glasgow 6/15 — coma/grave. Alerta crítico com banner de avaliação neurológica imediata.',
      },
    },
  },
};
