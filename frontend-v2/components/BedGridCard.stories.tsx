import type { Meta, StoryObj } from '@storybook/react';
import BedGridCard, { BedGridSkeleton, BedGridEmpty } from './BedGridCard';
import type { BedStatus } from '@/lib/movement-types';
import { MOCK_BEDS } from '@/lib/movement-types';

// ─── Mock Data Factories ───────────────────────────────────────────────────

const freeBed: BedStatus = MOCK_BEDS.find((b) => b.status === 'free')!;
const occupiedBed: BedStatus = MOCK_BEDS.find((b) => b.status === 'occupied')!;
const blockedBed: BedStatus = MOCK_BEDS.find((b) => b.status === 'blocked')!;
const cleaningBed: BedStatus = MOCK_BEDS.find((b) => b.status === 'cleaning')!;

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof BedGridCard> = {
  title: 'Components/BedGridCard',
  component: BedGridCard,
  tags: ['autodocs'],
  argTypes: {
    bed: {
      control: 'object',
      description: 'Dados do leito (BedStatus)',
    },
    onSelect: {
      action: 'selecionado',
      description: 'Callback disparado ao clicar no card do leito',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento',
    },
  },
};

export default meta;
type Story = StoryObj<typeof BedGridCard>;

const noop = () => {};

// ─── Stories ───────────────────────────────────────────────────────────────

export const Default: Story = {
  args: {
    bed: freeBed,
    onSelect: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Leito livre — card compacto com dot verde e label "Livre".',
      },
    },
  },
};

export const Occupied: Story = {
  args: {
    bed: occupiedBed,
    onSelect: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Leito ocupado — exibe nome do paciente e dot azul. Expansível para detalhes.',
      },
    },
  },
};

export const Blocked: Story = {
  args: {
    bed: blockedBed,
    onSelect: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Leito bloqueado — dot âmbar com nota de manutenção.',
      },
    },
  },
};

export const Cleaning: Story = {
  args: {
    bed: cleaningBed,
    onSelect: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Leito em limpeza — dot cinza com informação da última higienização.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    bed: {} as BedStatus,
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com skeleton do card de leito.',
      },
    },
  },
};

export const GridView: Story = {
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
        gap: '0.75rem',
        maxWidth: '720px',
      }}
    >
      {MOCK_BEDS.map((bed) => (
        <BedGridCard key={bed.id} bed={bed} onSelect={noop} />
      ))}
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          'Grade completa com todos os 12 leitos (UTI-1 + UTI-2) exibindo os 4 status (livre, ocupado, bloqueado, limpeza).',
      },
    },
  },
};
