import type { Meta, StoryObj } from '@storybook/react';
import BundleCard from './BundleCard';
import type { BundleInfo } from './BundleCard';

// ─── Mock Data Factories ───────────────────────────────────────────────────

function makeBundleComplete(): BundleInfo {
  return {
    id: 'lamgd',
    name: 'LAMGD — Úlcera de Estresse',
    criteria: [
      { id: 'lamgd-1', label: 'Indicação documentada', met: true },
      { id: 'lamgd-2', label: 'Medicação prescrita', met: true },
      { id: 'lamgd-3', label: 'Dose ajustada para peso', met: true },
      { id: 'lamgd-4', label: 'Revisão em 72h', met: true },
    ],
    status: 'complete',
    score: 100,
  };
}

function makeBundlePartial(): BundleInfo {
  return {
    id: 'tev',
    name: 'TEV — Tromboembolismo Venoso',
    criteria: [
      { id: 'tev-1', label: 'Risco avaliado (Padua)', met: true },
      { id: 'tev-2', label: 'Profilaxia farmacológica', met: true },
      { id: 'tev-3', label: 'Profilaxia mecânica', met: false },
      { id: 'tev-4', label: 'Contraindicação documentada', met: true },
      { id: 'tev-5', label: 'Reavaliação diária', met: false },
    ],
    status: 'partial',
    score: 60,
  };
}

function makeBundlePending(): BundleInfo {
  return {
    id: 'pneumonia',
    name: 'Bundle de PAV — Pneumonia',
    criteria: [
      { id: 'pav-1', label: 'Cabeceira elevada 30-45°', met: false },
      { id: 'pav-2', label: 'Despertar diário (SAT)', met: false },
      { id: 'pav-3', label: 'Respiração espontânea (SBT)', met: false },
      { id: 'pav-4', label: 'Higiene oral com clorexidina', met: false },
    ],
    status: 'pending',
    score: 0,
  };
}

function makeBundleNA(): BundleInfo {
  return {
    id: 'dlp',
    name: 'DLP — Delirium (CAM-ICU negativo)',
    criteria: [
      { id: 'dlp-1', label: 'CAM-ICU — resultado negativo', met: true },
      { id: 'dlp-2', label: 'Mobilização precoce', met: true, na: true },
      { id: 'dlp-3', label: 'Sedação leve (RASS 0 a -2)', met: true, na: true },
    ],
    status: 'na',
  };
}

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof BundleCard> = {
  title: 'Components/BundleCard',
  component: BundleCard,
  tags: ['autodocs'],
  argTypes: {
    readOnly: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof BundleCard>;

const noop = () => {};

// ─── Stories ───────────────────────────────────────────────────────────────

export const Complete: Story = {
  args: {
    bundle: makeBundleComplete(),
    onToggle: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Bundle 100% atendido — barra de progresso verde completa, status "Completo".',
      },
    },
  },
};

export const Partial: Story = {
  args: {
    bundle: makeBundlePartial(),
    onToggle: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Bundle parcialmente atendido (60%) — barra de progresso amarela, status "Parcial".',
      },
    },
  },
};

export const Pending: Story = {
  args: {
    bundle: makeBundlePending(),
    onToggle: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Bundle não iniciado (0%) — barra de progresso cinza, status "Pendente".',
      },
    },
  },
};

export const NA: Story = {
  args: {
    bundle: makeBundleNA(),
  },
  parameters: {
    docs: {
      description: {
        story:
          'Bundle não aplicável — critérios marcados como N/A, sem barra de progresso.',
      },
    },
  },
};

export const ReadOnly: Story = {
  args: {
    bundle: makeBundlePartial(),
    readOnly: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Modo somente leitura — ícones de status no lugar dos checkboxes.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    bundle: {} as BundleInfo,
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com skeleton do card.',
      },
    },
  },
};

export const Error: Story = {
  args: {
    bundle: {} as BundleInfo,
    error: 'Erro ao carregar bundle. Tente novamente.',
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de erro com alerta visual.',
      },
    },
  },
};
