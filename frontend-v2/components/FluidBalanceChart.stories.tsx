import type { Meta, StoryObj } from '@storybook/react';
import FluidBalanceChart from './FluidBalanceChart';
import type { FluidBalanceTrend } from '@/lib/fluid-balance-types';

// ─── Mock Data ────────────────────────────────────────────────────────────────

function makeTrendData(): FluidBalanceTrend[] {
  const today = new Date();
  const records: FluidBalanceTrend[] = [];

  for (let i = 6; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const date = d.toISOString().slice(0, 10);

    const intake = 2000 + Math.round(Math.random() * 1200);
    const output = 1500 + Math.round(Math.random() * 1000);

    records.push({
      date,
      intake_ml: intake,
      output_ml: output,
      balance_ml: intake - output,
    });
  }

  return records;
}

// ─── Meta ─────────────────────────────────────────────────────────────────────

const meta: Meta<typeof FluidBalanceChart> = {
  title: 'Components/FluidBalanceChart',
  component: FluidBalanceChart,
  tags: ['autodocs'],
  argTypes: {
    data: {
      control: 'object',
      description: 'Dados da série temporal de balanço hídrico (7 dias)',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento',
    },
    error: {
      control: 'text',
      description: 'Mensagem de erro — exibe alerta no lugar do gráfico',
    },
  },
};

export default meta;
type Story = StoryObj<typeof FluidBalanceChart>;

// ─── Stories ──────────────────────────────────────────────────────────────────

export const Default: Story = {
  args: {
    data: makeTrendData(),
  },
  parameters: {
    docs: {
      description: {
        story:
          'Gráfico composto (barras + linha) com 7 dias de balanço hídrico. Barras exibem entradas (verde) e saídas (laranja); linha azul mostra o balanço líquido.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    data: [],
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado de carregamento — skeleton animado com role="status" e aria-label descritivo.',
      },
    },
  },
};

export const Error: Story = {
  args: {
    data: [],
    error: 'Erro ao carregar dados de balanço hídrico. Verifique a conexão com o servidor.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado de erro — alerta visual com ícone AlertTriangle e role="alert".',
      },
    },
  },
};

export const Empty: Story = {
  args: {
    data: [],
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado vazio — mensagem "Sem dados de balanço hídrico" centralizada quando o array de dados está vazio.',
      },
    },
  },
};
