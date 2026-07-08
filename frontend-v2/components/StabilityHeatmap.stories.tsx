import type { Meta, StoryObj } from '@storybook/react';
import StabilityHeatmap from './StabilityHeatmap';
import { MOCK_CRITERIA } from '@/lib/stability-types';
import type { StabilityCriterion } from '@/lib/stability-types';

// ─── Mock Data Helpers ─────────────────────────────────────────────────────

function getVasopressorOnly(): StabilityCriterion[] {
  return MOCK_CRITERIA.filter((c) => c.category === 'vasopressor');
}

function getEmptyCriteria(): StabilityCriterion[] {
  return [];
}

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof StabilityHeatmap> = {
  title: 'Components/StabilityHeatmap',
  component: StabilityHeatmap,
  tags: ['autodocs'],
  argTypes: {
    criteria: {
      control: 'object',
      description: 'Lista de critérios de estabilidade (StabilityCriterion[])',
    },
    categoryFilter: {
      control: 'select',
      options: [
        '',
        'vasopressor',
        'perfusion',
        'cardiac_output',
        'fluid_balance',
        'lactate',
        'combined',
      ],
      description:
        'Categoria inicialmente filtrada (vazio = todas as 6 categorias)',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento com grid e tabs',
    },
    error: {
      control: 'text',
      description: 'Mensagem de erro (exibe alerta no lugar do heatmap)',
    },
  },
};

export default meta;
type Story = StoryObj<typeof StabilityHeatmap>;

// ─── Stories ───────────────────────────────────────────────────────────────

/** Heatmap completo com 27 critérios distribuídos em 6 categorias — grid com dots coloridos (normal/atenção/crítico) e tooltip no hover. */
export const Default: Story = {
  args: {
    criteria: MOCK_CRITERIA,
    categoryFilter: undefined,
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Visualização padrão com todas as 6 categorias (vasopressor, perfusão, débito cardíaco, balanço hídrico, lactato, combinados) e 27 critérios. Cada célula exibe um ícone colorido (verde/amarelo/vermelho) e tooltip com detalhes no hover.',
      },
    },
  },
};

/** Heatmap filtrado apenas para a categoria "Vasopressor" — 5 critérios exibidos em coluna única. */
export const FilteredVasopressor: Story = {
  args: {
    criteria: MOCK_CRITERIA,
    categoryFilter: 'vasopressor',
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Heatmap com filtro ativo para categoria "Vasopressor". Exibe apenas a coluna de vasopressor com 5 critérios (2 críticos, 2 atenção, 1 normal). Demonstra o comportamento de clique nas abas de filtro (toggle).',
      },
    },
  },
};

/** Estado de carregamento com skeleton de abas de filtro e grid placeholder. */
export const Loading: Story = {
  args: {
    criteria: [],
    categoryFilter: undefined,
    isLoading: true,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Skeleton de carregamento com 7 abas de filtro em placeholder e grid 6×5 com dots circulares animados (pulse).',
      },
    },
  },
};

/** Estado de erro com banner de alerta crítico. */
export const Error: Story = {
  args: {
    criteria: [],
    categoryFilter: undefined,
    isLoading: false,
    error: 'Erro ao carregar critérios de estabilidade. Tente novamente.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Banner de erro usando tokens de severidade crítica (wash/signal/on-surface do clinical-severity-critical).',
      },
    },
  },
};

/** Estado vazio — nenhum critério configurado. */
export const Empty: Story = {
  args: {
    criteria: getEmptyCriteria(),
    categoryFilter: undefined,
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Placeholder centralizado com ícone Filter e mensagem "Nenhum critério configurado". Exibido quando o array criteria está vazio.',
      },
    },
  },
};
