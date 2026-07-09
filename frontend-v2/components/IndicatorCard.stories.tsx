import type { Meta, StoryObj } from '@storybook/react';
import IndicatorCard from './IndicatorCard';
import type { Indicator } from '@/lib/indicators-types';
import { MOCK_INDICATORS } from '@/lib/indicators-types';

// ─── Mock Data Factories ───────────────────────────────────────────────────

const tlpIndicator: Indicator = MOCK_INDICATORS[0]!; // TLP 87.3% improving
const worseningIndicator: Indicator = MOCK_INDICATORS[4]!; // Tempo Médio 7.2 dias worsening
const improvingIndicator: Indicator = MOCK_INDICATORS[8]!; // IPCS 1.4 improving
const atTarget: Indicator = MOCK_INDICATORS[2]!; // Ocupação 82.5% stable

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof IndicatorCard> = {
  title: 'Components/IndicatorCard',
  component: IndicatorCard,
  tags: ['autodocs'],
  argTypes: {
    indicator: {
      control: 'object',
      description: 'Dados do indicador (Indicator)',
    },
    onClick: {
      action: 'clicado',
      description: 'Callback ao clicar no card (torna o card interativo)',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento',
    },
  },
};

export default meta;
type Story = StoryObj<typeof IndicatorCard>;

const noop = () => {};

// ─── Stories ───────────────────────────────────────────────────────────────

export const Default: Story = {
  args: {
    indicator: tlpIndicator,
    onClick: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Indicador TLP — Adesão ao TLP 87.3%, tendência "Melhorando". Barra de progresso verde, badge de categoria indigo. Interativo (onClick).',
      },
    },
  },
};

export const Worsening: Story = {
  args: {
    indicator: worseningIndicator,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Indicador "Piorando" — Tempo Médio de Permanência 7.2 dias, tendência de piora. Barra de progresso vermelha indicando valor acima do range.',
      },
    },
  },
};

export const Improving: Story = {
  args: {
    indicator: improvingIndicator,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Indicador "Melhorando" — Densidade de IPCS 1.4 eventos/1000, tendência de melhora. Categoria Segurança (vermelho).',
      },
    },
  },
};

export const AtTarget: Story = {
  args: {
    indicator: atTarget,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Indicador na meta — Taxa de Ocupação 82.5%, tendência "Estável". Valor dentro do reference range, barra verde.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    indicator: {} as Indicator,
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com skeleton do card de indicador.',
      },
    },
  },
};

export const Comparison: Story = {
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '1rem',
        maxWidth: '900px',
      }}
    >
      <IndicatorCard indicator={MOCK_INDICATORS[0]!} /> {/* TLP */}
      <IndicatorCard indicator={MOCK_INDICATORS[2]!} /> {/* Ocupação */}
      <IndicatorCard indicator={MOCK_INDICATORS[4]!} /> {/* Tempo Médio */}
      <IndicatorCard indicator={MOCK_INDICATORS[8]!} /> {/* IPCS */}
      <IndicatorCard indicator={MOCK_INDICATORS[9]!} /> {/* Quedas */}
      <IndicatorCard indicator={MOCK_INDICATORS[11]!} /> {/* Reinternação */}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          'Grade com 6 indicadores de diferentes categorias (TLP, ocupação, stewardship, segurança, eficiência) para comparação lado a lado.',
      },
    },
  },
};
