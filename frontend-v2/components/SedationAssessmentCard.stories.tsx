import type { Meta, StoryObj } from '@storybook/react';
import SedationAssessmentCard from './SedationAssessmentCard';
import type { SedationAssessment } from '@/lib/sedation-types';
import { MOCK_ASSESSMENT } from '@/lib/sedation-types';

// ─── Mock Data Factories ───────────────────────────────────────────────────

const defaultAssessment: SedationAssessment = MOCK_ASSESSMENT; // RASS -2, BPS 4, CAM-ICU negativo

const deepSedation: SedationAssessment = {
  ...MOCK_ASSESSMENT,
  id: 'sed-deep',
  rass_score: -5,
  bps_nrs_score: 3,
  bps_nrs_type: 'BPS',
  cam_icu_positive: null,
  assessed_at: new Date().toISOString(),
  assessed_by: 'Dr. Pedro Lima',
  notes: 'Paciente em sedação profunda conforme protocolo de TCE. RASS alvo -5.',
};

const agitated: SedationAssessment = {
  ...MOCK_ASSESSMENT,
  id: 'sed-agitated',
  rass_score: 3,
  bps_nrs_score: 8,
  bps_nrs_type: 'NRS',
  cam_icu_positive: true,
  assessed_at: new Date().toISOString(),
  assessed_by: 'Enf. Maria Silva',
  notes: 'Paciente com agitação psicomotora. CAM-ICU positivo para delirium.',
};

const delirium: SedationAssessment = {
  ...MOCK_ASSESSMENT,
  id: 'sed-delirium',
  rass_score: 1,
  bps_nrs_score: 5,
  bps_nrs_type: 'NRS',
  cam_icu_positive: true,
  assessed_at: new Date().toISOString(),
  assessed_by: 'Dr(a). Ana Costa',
  notes: 'Paciente inquieto, desorientado. CAM-ICU positivo — iniciar protocolo de delirium.',
};

const noPain: SedationAssessment = {
  ...MOCK_ASSESSMENT,
  id: 'sed-nopain',
  rass_score: 0,
  bps_nrs_score: undefined,
  bps_nrs_type: undefined,
  cam_icu_positive: false,
  assessed_at: new Date().toISOString(),
  assessed_by: 'Dr(a). Ana Costa',
  notes: 'Paciente alerta, calmo e sem dor. RASS 0 — alvo terapêutico.',
};

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof SedationAssessmentCard> = {
  title: 'Components/SedationAssessmentCard',
  component: SedationAssessmentCard,
  tags: ['autodocs'],
  argTypes: {
    assessment: {
      control: 'object',
      description: 'Dados da avaliação de sedação (SedationAssessment)',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento',
    },
    error: {
      control: 'text',
      description: 'Mensagem de erro, se houver',
    },
  },
};

export default meta;
type Story = StoryObj<typeof SedationAssessmentCard>;

// ─── Stories ───────────────────────────────────────────────────────────────

export const Default: Story = {
  args: {
    assessment: defaultAssessment,
  },
  parameters: {
    docs: {
      description: {
        story:
          'RASS -2 (Sedação Leve) — BPS 4 (Dor leve) — CAM-ICU negativo (Sem delirium). Cenário típico de paciente em sedação leve controlada.',
      },
    },
  },
};

export const DeepSedation: Story = {
  args: {
    assessment: deepSedation,
  },
  parameters: {
    docs: {
      description: {
        story:
          'RASS -5 (Incapaz de despertar) — sedação profunda. CAM-ICU não avaliado. Cenário de TCE com sedação máxima.',
      },
    },
  },
};

export const Agitated: Story = {
  args: {
    assessment: agitated,
  },
  parameters: {
    docs: {
      description: {
        story:
          'RASS +3 (Muito agitado) — NRS 8 (Dor moderada) — CAM-ICU positivo (Delirium). Cenário de agitação com delirium e dor.',
      },
    },
  },
};

export const Delirium: Story = {
  args: {
    assessment: delirium,
  },
  parameters: {
    docs: {
      description: {
        story:
          'RASS +1 (Inquieto) — CAM-ICU positivo. Foco no diagnóstico de delirium com paciente levemente agitado.',
      },
    },
  },
};

export const NoPain: Story = {
  args: {
    assessment: noPain,
  },
  parameters: {
    docs: {
      description: {
        story:
          'RASS 0 (Alerta e calmo) — dor não avaliada — sem delirium. Paciente no alvo terapêutico ideal.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado de carregamento com skeleton completo do card (RASS, BPS/NRS, CAM-ICU).',
      },
    },
  },
};

export const Error: Story = {
  args: {
    error: 'Falha ao carregar avaliação de sedação. Verifique a conexão com o servidor.',
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de erro com banner de alerta e ícone AlertTriangle.',
      },
    },
  },
};
