import type { Meta, StoryObj } from '@storybook/react';
import ClinicalTimeline from './ClinicalTimeline';
import type { TimelineEvent } from './ClinicalTimeline';

// ─── Mock Data Factories ───────────────────────────────────────────────────

function makeSepsisTimeline(): TimelineEvent[] {
  const now = Date.now();
  return [
    {
      id: 'evt-1',
      status: 'completed',
      label: 'qSOFA Screening',
      description: 'qSOFA = 2 (GCS < 15 + RR > 22)',
      timestamp: new Date(now - 120 * 60 * 1000).toISOString(),
    },
    {
      id: 'evt-2',
      status: 'completed',
      label: 'Coleta de Lactato',
      description: 'Lactato sérico = 3.4 mmol/L',
      timestamp: new Date(now - 90 * 60 * 1000).toISOString(),
    },
    {
      id: 'evt-3',
      status: 'completed',
      label: 'Coleta de Culturas',
      description: 'Hemocultura + urocultura coletadas',
      timestamp: new Date(now - 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'evt-4',
      status: 'in-progress',
      label: 'Antibioticoterapia Empírica',
      description: 'Ceftriaxone 2g EV — em administração',
      timestamp: new Date(now - 30 * 60 * 1000).toISOString(),
    },
    {
      id: 'evt-5',
      status: 'pending',
      label: 'Reavaliação do Bundle (3h)',
      description: 'Reavaliar lactato e resposta hemodinâmica',
    },
    {
      id: 'evt-6',
      status: 'pending',
      label: 'Reavaliação do Bundle (6h)',
      description: 'Reavaliar culturas e ajustar antibiótico',
    },
  ];
}

function makeSingleEvent(): TimelineEvent[] {
  return [
    {
      id: 'evt-single',
      status: 'completed',
      label: 'Avaliação Inicial',
      description: 'Paciente admitido na UTI — avaliação inicial completa',
      timestamp: new Date().toISOString(),
    },
  ];
}

function makeOverdueTimeline(): TimelineEvent[] {
  return [
    {
      id: 'evt-a',
      status: 'completed',
      label: 'qSOFA Screening',
      timestamp: new Date(Date.now() - 240 * 60 * 1000).toISOString(),
    },
    {
      id: 'evt-b',
      status: 'completed',
      label: 'Coleta de Lactato',
      timestamp: new Date(Date.now() - 210 * 60 * 1000).toISOString(),
    },
    {
      id: 'evt-c',
      status: 'overdue',
      label: 'Antibioticoterapia (1h)',
      description: 'Prazo: 1h após diagnóstico. Atrasado em 45 min.',
      timestamp: new Date(Date.now() - 120 * 60 * 1000).toISOString(),
    },
    {
      id: 'evt-d',
      status: 'pending',
      label: 'Reavaliação do Bundle (3h)',
    },
  ];
}

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof ClinicalTimeline> = {
  title: 'Components/ClinicalTimeline',
  component: ClinicalTimeline,
  tags: ['autodocs'],
  argTypes: {
    domain: {
      control: 'select',
      options: ['sepsis', 'general'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof ClinicalTimeline>;

// ─── Stories ───────────────────────────────────────────────────────────────

export const Default: Story = {
  args: {
    events: makeSepsisTimeline(),
    domain: 'sepsis',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Timeline de confirmação de sepse com eventos concluídos, em progresso e pendentes.',
      },
    },
  },
};

export const Overdue: Story = {
  args: {
    events: makeOverdueTimeline(),
    domain: 'sepsis',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Timeline com evento atrasado (overdue) destacado em vermelho com animação de pulso.',
      },
    },
  },
};

export const SingleEvent: Story = {
  args: {
    events: makeSingleEvent(),
    domain: 'sepsis',
  },
  parameters: {
    docs: {
      description: {
        story: 'Timeline com apenas um evento — sem linha conectora.',
      },
    },
  },
};

export const GeneralDomain: Story = {
  args: {
    events: [
      {
        id: 'gen-1',
        status: 'completed',
        label: 'Admissão na UTI',
        timestamp: new Date().toISOString(),
      },
      {
        id: 'gen-2',
        status: 'in-progress',
        label: 'Avaliação de Risco',
        description: 'NEWS2 em andamento',
      },
      {
        id: 'gen-3',
        status: 'pending',
        label: 'Plano Terapêutico',
      },
    ],
    domain: 'general',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Timeline no domínio general — usa tokens semânticos para pending.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    events: [],
    domain: 'sepsis',
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com skeleton de timeline.',
      },
    },
  },
};

export const Empty: Story = {
  args: {
    events: [],
    domain: 'sepsis',
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado vazio — "Nenhum evento registrado".',
      },
    },
  },
};

export const Error: Story = {
  args: {
    events: [],
    domain: 'sepsis',
    error: 'Falha ao carregar timeline. Tente novamente.',
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de erro com alerta visual.',
      },
    },
  },
};
