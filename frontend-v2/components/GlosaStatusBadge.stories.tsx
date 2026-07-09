import type { Meta, StoryObj } from '@storybook/react';
import GlosaStatusBadge from './GlosaStatusBadge';
import type { GlosaStatus } from '@/lib/doc-types';

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof GlosaStatusBadge> = {
  title: 'Components/GlosaStatusBadge',
  component: GlosaStatusBadge,
  tags: ['autodocs'],
  argTypes: {
    status: {
      control: 'select',
      options: ['pendente', 'em_analise', 'glosado', 'liberado', 'recorrido'],
      description: 'Status da glosa',
    },
    valor: {
      control: { type: 'number', min: 0, max: 10000 },
      description: 'Valor glosado em reais (opcional, exibido para glosado e recorrido)',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento do badge',
    },
  },
};

export default meta;
type Story = StoryObj<typeof GlosaStatusBadge>;

// ─── Stories ───────────────────────────────────────────────────────────────

export const Pendente: Story = {
  args: {
    status: 'pendente',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Status "Pendente" — badge âmbar com ícone Clock. Aguardando análise do auditor.',
      },
    },
  },
};

export const EmAnalise: Story = {
  args: {
    status: 'em_analise',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Status "Em Análise" — badge azul com ícone Search. Documentação sendo revisada.',
      },
    },
  },
};

export const Glosado: Story = {
  args: {
    status: 'glosado',
    valor: 1250.75,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Status "Glosado" — badge vermelho com ícone Ban e valor glosado (R$ 1.250,75).',
      },
    },
  },
};

export const Liberado: Story = {
  args: {
    status: 'liberado',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Status "Liberado" — badge verde com ícone CheckCircle. Documentação aprovada sem glosa.',
      },
    },
  },
};

export const Recorrido: Story = {
  args: {
    status: 'recorrido',
    valor: 890.50,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Status "Recorrido" — badge cinza com ícone RefreshCw e valor (R$ 890,50). Recurso em andamento.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    status: 'pendente',
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com spinner e skeleton do badge.',
      },
    },
  },
};

export const Comparacao: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
      <GlosaStatusBadge status="pendente" />
      <GlosaStatusBadge status="em_analise" />
      <GlosaStatusBadge status="glosado" valor={1250.75} />
      <GlosaStatusBadge status="liberado" />
      <GlosaStatusBadge status="recorrido" valor={890.50} />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          'Todos os 5 status lado a lado para comparação visual.',
      },
    },
  },
};
