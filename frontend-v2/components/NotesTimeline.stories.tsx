import type { Meta, StoryObj } from '@storybook/react';
import NotesTimeline from './NotesTimeline';
import type { Evolucao } from '@/lib/clinical-notes-types';
import { MOCK_NOTES } from '@/lib/clinical-notes-types';

// ─── Mock Data Factories ───────────────────────────────────────────────────

/** 3 notes para o paciente MPI-001 (admissão + diária + alta) */
const threeNotes: Evolucao[] = MOCK_NOTES.slice(0, 3);

/** 1 única nota */
const singleNote: Evolucao[] = [MOCK_NOTES[7]!]; // Carlos Santos — diária

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof NotesTimeline> = {
  title: 'Components/NotesTimeline',
  component: NotesTimeline,
  tags: ['autodocs'],
  argTypes: {
    notes: {
      control: 'object',
      description: 'Lista de evoluções clínicas (Evolucao[])',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento',
    },
    error: {
      control: 'text',
      description: 'Mensagem de erro, se houver',
    },
    emptyMessage: {
      control: 'text',
      description: 'Mensagem exibida quando a lista está vazia',
    },
  },
};

export default meta;
type Story = StoryObj<typeof NotesTimeline>;

// ─── Stories ───────────────────────────────────────────────────────────────

export const Default: Story = {
  args: {
    notes: threeNotes,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Timeline com 3 evoluções (admissão, diária, alta) do paciente João Silva. Cada nota é expansível com conteúdo markdown.',
      },
    },
  },
};

export const SingleNote: Story = {
  args: {
    notes: singleNote,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Timeline com apenas uma evolução — sem linha conectora entre cards.',
      },
    },
  },
};

export const Empty: Story = {
  args: {
    notes: [],
    emptyMessage: 'Nenhuma evolução registrada para este paciente',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado vazio — exibe ícone FileText e mensagem customizada.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    notes: [],
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com skeleton de 4 itens da timeline.',
      },
    },
  },
};

export const Error: Story = {
  args: {
    notes: [],
    error: 'Falha ao carregar evoluções clínicas. Verifique a conexão e tente novamente.',
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de erro com banner de alerta e ícone AlertTriangle.',
      },
    },
  },
};
