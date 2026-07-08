import type { Meta, StoryObj } from '@storybook/react';
import VentilationTrendChart from './VentilationTrendChart';
import { generateMockTrend } from '@/lib/ventilation-types';

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof VentilationTrendChart> = {
  title: 'Components/VentilationTrendChart',
  component: VentilationTrendChart,
  tags: ['autodocs'],
  argTypes: {
    trend: {
      control: 'object',
      description: 'Dados da tendência ventilatória (VentilationTrend | null)',
    },
    selectedParam: {
      control: 'select',
      options: [
        'FiO2',
        'PEEP',
        'VC',
        'FR',
        'Pplat',
        'driving_pressure',
        'PaO2_FiO2_ratio',
      ],
      description: 'Parâmetro selecionado para visualização no gráfico',
    },
    onParamChange: {
      action: 'paramChanged',
      description: 'Callback disparado ao trocar de parâmetro',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento com tabs e gráfico',
    },
    error: {
      control: 'text',
      description: 'Mensagem de erro (exibe alerta no lugar do gráfico)',
    },
  },
};

export default meta;
type Story = StoryObj<typeof VentilationTrendChart>;

// ─── Stories ───────────────────────────────────────────────────────────────

/** Gráfico de tendência com parâmetro FiO₂ selecionado — série temporal 24h, sumário com direção, média, mín e máx. */
export const Default: Story = {
  args: {
    trend: generateMockTrend(24),
    selectedParam: 'FiO2',
    onParamChange: undefined,
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Visualização padrão com FiO₂ selecionado. Exibe gráfico de linha com 24 pontos horários, abas de parâmetros e sumário de tendência (direção, % mudança, média, mín, máx).',
      },
    },
  },
};

/** Gráfico exibindo o parâmetro PEEP com suas cores e unidade (cmH₂O). */
export const PEEPView: Story = {
  args: {
    trend: generateMockTrend(24),
    selectedParam: 'PEEP',
    onParamChange: undefined,
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Alternância para o parâmetro PEEP. Demonstra a troca de cor da linha (token clinical-ventilation-peep), unidade cmH₂O e tooltip adaptado.',
      },
    },
  },
};

/** Estado de carregamento com skeleton de abas e área do gráfico. */
export const Loading: Story = {
  args: {
    trend: null,
    selectedParam: 'FiO2',
    onParamChange: undefined,
    isLoading: true,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Skeleton de carregamento exibindo 5 abas de parâmetros em placeholder e uma área de gráfico (300px) com animação pulse.',
      },
    },
  },
};

/** Estado de erro com banner de alerta e mensagem descritiva. */
export const Error: Story = {
  args: {
    trend: null,
    selectedParam: 'FiO2',
    onParamChange: undefined,
    isLoading: false,
    error: 'Falha ao carregar dados de tendência ventilatória. Serviço indisponível.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Banner de erro com ícone AlertTriangle e mensagem. Usa tokens de feedback de erro (bg, text, border).',
      },
    },
  },
};

/** Estado vazio — sem dados de tendência disponíveis. */
export const Empty: Story = {
  args: {
    trend: null,
    selectedParam: 'FiO2',
    onParamChange: undefined,
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Placeholder centralizado com borda arredondada e mensagem "Sem dados de tendência". Exibido quando trend é null.',
      },
    },
  },
};
