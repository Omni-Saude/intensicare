import type { Meta, StoryObj } from '@storybook/react';
import PrescriptionCard from './PrescriptionCard';
import type { Prescription, DrugInteraction } from '@/lib/prescription-types';
import { MOCK_PRESCRIPTIONS, MOCK_DRUG_INTERACTIONS } from '@/lib/prescription-types';

// ─── Mock Data Factories ───────────────────────────────────────────────────

const activeRx: Prescription = MOCK_PRESCRIPTIONS[0]!; // Ceftriaxona — active
const completedRx: Prescription = {
  ...MOCK_PRESCRIPTIONS[0]!,
  id: 'rx-completed',
  status: 'completed',
};
const discontinuedRx: Prescription = {
  ...MOCK_PRESCRIPTIONS[1]!,
  id: 'rx-disc',
  status: 'discontinued',
};
const interaction: DrugInteraction = MOCK_DRUG_INTERACTIONS[1]!; // Midazolam + Noradrenalina — grave

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof PrescriptionCard> = {
  title: 'Components/PrescriptionCard',
  component: PrescriptionCard,
  tags: ['autodocs'],
  argTypes: {
    prescription: {
      control: 'object',
      description: 'Dados da prescrição (Prescription)',
    },
    onStatusChange: {
      action: 'status alterado',
      description: 'Callback para alteração de status (concluir/descontinuar)',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento',
    },
    interaction: {
      control: 'object',
      description: 'Interação medicamentosa relevante, se houver',
    },
  },
};

export default meta;
type Story = StoryObj<typeof PrescriptionCard>;

const noop = () => {};

// ─── Stories ───────────────────────────────────────────────────────────────

export const Default: Story = {
  args: {
    prescription: activeRx,
    onStatusChange: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Prescrição ativa (Ceftriaxona 2g IV 12/12h) — exibe badge verde "Ativa", botões de concluir e descontinuar.',
      },
    },
  },
};

export const Completed: Story = {
  args: {
    prescription: completedRx,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Prescrição concluída — badge azul "Concluída", sem botões de ação.',
      },
    },
  },
};

export const Discontinued: Story = {
  args: {
    prescription: discontinuedRx,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Prescrição descontinuada — badge cinza "Descontinuada", sem botões de ação.',
      },
    },
  },
};

export const WithInteraction: Story = {
  args: {
    prescription: MOCK_PRESCRIPTIONS[5]!, // Midazolam
    onStatusChange: noop,
    interaction,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Prescrição ativa com alerta de interação medicamentosa grave (Midazolam + Noradrenalina). Banner de alerta no topo do card.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    prescription: {} as Prescription,
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com skeleton do card de prescrição.',
      },
    },
  },
};
