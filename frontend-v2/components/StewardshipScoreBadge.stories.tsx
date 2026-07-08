import type { Meta, StoryObj } from '@storybook/react';
import StewardshipScoreBadge from './StewardshipScoreBadge';

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof StewardshipScoreBadge> = {
  title: 'Components/StewardshipScoreBadge',
  component: StewardshipScoreBadge,
  tags: ['autodocs'],
  argTypes: {
    severity: {
      control: 'select',
      options: ['NEUTRO', 'AMARELO', 'VERMELHO'],
    },
    score: {
      control: { type: 'number', min: 0, max: 12 },
    },
    totalCriteria: {
      control: { type: 'number', min: 1, max: 12 },
    },
    isLoading: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof StewardshipScoreBadge>;

// ─── Stories ───────────────────────────────────────────────────────────────

export const NEUTRO: Story = {
  args: {
    score: 2,
    totalCriteria: 12,
    severity: 'NEUTRO',
    recommendation:
      'Prescrição adequada. Manter monitoramento padrão conforme protocolo institucional.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Score baixo (2/12) — prescrição adequada, sem necessidade de intervenção. Ícone ShieldCheck verde.',
      },
    },
  },
};

export const AMARELO: Story = {
  args: {
    score: 5,
    totalCriteria: 12,
    severity: 'AMARELO',
    recommendation:
      'Revisão recomendada em 48h. Considere descalonamento após resultado de culturas.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Score médio (5/12) — revisão recomendada. Ícone AlertTriangle amarelo.',
      },
    },
  },
};

export const VERMELHO: Story = {
  args: {
    score: 8,
    totalCriteria: 12,
    severity: 'VERMELHO',
    recommendation:
      'Intervenção imediata necessária. Antibiótico inadequado para o perfil de sensibilidade local.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Score alto (8/12) — intervenção imediata. Ícone AlertOctagon vermelho.',
      },
    },
  },
};

export const MaximumScore: Story = {
  args: {
    score: 12,
    totalCriteria: 12,
    severity: 'VERMELHO',
    recommendation:
      'Todos os critérios de inadequação presentes. Troca imediata de esquema antimicrobiano.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Score máximo (12/12) — cenário mais crítico, intervenção urgente.',
      },
    },
  },
};

export const WithoutRecommendation: Story = {
  args: {
    score: 3,
    totalCriteria: 12,
    severity: 'AMARELO',
  },
  parameters: {
    docs: {
      description: {
        story: 'Badge sem recomendação — apenas score e severidade.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    score: 0,
    totalCriteria: 12,
    severity: 'NEUTRO',
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com skeleton do badge.',
      },
    },
  },
};

export const Comparison: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-start' }}>
      <StewardshipScoreBadge
        score={1}
        totalCriteria={12}
        severity="NEUTRO"
        recommendation="Prescrição adequada."
      />
      <StewardshipScoreBadge
        score={5}
        totalCriteria={12}
        severity="AMARELO"
        recommendation="Revisão recomendada."
      />
      <StewardshipScoreBadge
        score={9}
        totalCriteria={12}
        severity="VERMELHO"
        recommendation="Intervenção imediata."
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          'Comparação lado a lado dos três níveis de severidade (NEUTRO, AMARELO, VERMELHO).',
      },
    },
  },
};
