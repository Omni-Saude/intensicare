import type { Meta, StoryObj } from '@storybook/react';
import PathwayBoard from './PathwayBoard';
import type { PatientPathway, PathwayProgress } from '@/lib/pathway-types';
import {
  MOCK_PATIENT_PATHWAYS,
  MOCK_PROGRESS,
  MOCK_PATHWAYS,
} from '@/lib/pathway-types';

// ─── Mock Data Helpers ─────────────────────────────────────────────────────

function getSepsePathway(): PatientPathway {
  return MOCK_PATIENT_PATHWAYS[0]!; // Carlos — Sepse active, urgent, Bundle 1h
}

function getSepseProgress(): PathwayProgress {
  return MOCK_PROGRESS['pp-001']!;
}

function getTEVPathway(): PatientPathway {
  return MOCK_PATIENT_PATHWAYS[1]!; // Carlos — TEV active, normal
}

function getTEVProgress(): PathwayProgress {
  return MOCK_PROGRESS['pp-002']!;
}

function getOverduePathway(): PatientPathway {
  return MOCK_PATIENT_PATHWAYS[3]!; // Maria Helena — TEV overdue, critical
}

function getOverdueProgress(): PathwayProgress {
  return MOCK_PROGRESS['pp-004']!;
}

function getCompletedPathway(): PatientPathway {
  // Build a completed pathway from the Ventilação pathway with all criteria met
  const ventPathway = structuredClone(MOCK_PATIENT_PATHWAYS[2]!); // Maria Helena — Ventilação
  ventPathway.status = 'completed';
  ventPathway.severity = 'normal';
  ventPathway.completed_at = '2026-07-07T12:00:00Z';
  ventPathway.criteria = ventPathway.criteria.map((c) => ({ ...c, met: true }));
  return ventPathway;
}

function getCompletedProgress(): PathwayProgress {
  const progress = structuredClone(MOCK_PROGRESS['pp-005']!); // José — Desmame (all met, improving)
  progress.trend = 'none';
  progress.recommendation =
    'Paciente concluiu todos os estados do pathway. Alta da UTI programada.';
  return progress;
}

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof PathwayBoard> = {
  title: 'Components/PathwayBoard',
  component: PathwayBoard,
  tags: ['autodocs'],
  argTypes: {
    patientPathway: {
      control: 'object',
      description: 'Dados do paciente e pathway ativo (PatientPathway | null)',
    },
    progress: {
      control: 'object',
      description:
        'Progresso do pathway com histórico de estados e recomendação (PathwayProgress | null)',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento',
    },
    error: {
      control: 'text',
      description: 'Mensagem de erro (exibe alerta no lugar do board)',
    },
  },
};

export default meta;
type Story = StoryObj<typeof PathwayBoard>;

// ─── Stories ───────────────────────────────────────────────────────────────

/** Pathway ativo com estado "Bundle 1h" — critérios parcialmente atendidos, recomendação clínica e timeline de 3 transições. */
export const Default: Story = {
  args: {
    patientPathway: getSepsePathway(),
    progress: getSepseProgress(),
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Pathway de Sepse ativo (urgent) com 3/5 critérios atendidos, progresso de 60% e recomendação de ressuscitação volêmica. Exibe histórico de estados com 3 transições.',
      },
    },
  },
};

/** Estado de carregamento com skeleton animado de header, barra de progresso e conteúdo. */
export const Loading: Story = {
  args: {
    patientPathway: null,
    progress: null,
    isLoading: true,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Skeleton de carregamento com placeholders animados para header, barra de progresso e grid de conteúdo (4 itens à esquerda, 3 à direita).',
      },
    },
  },
};

/** Estado de erro com mensagem e ícone de alerta (role="alert"). */
export const Error: Story = {
  args: {
    patientPathway: null,
    progress: null,
    isLoading: false,
    error: 'Erro ao carregar dados do pathway. Verifique a conexão com o servidor.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Banner de erro com ícone AlertTriangle e mensagem descritiva. Usa tokens de feedback de erro (bg, text, border).',
      },
    },
  },
};

/** Estado vazio quando nenhum paciente está selecionado. */
export const Empty: Story = {
  args: {
    patientPathway: null,
    progress: null,
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Placeholder centralizado com ícone GitBranch e mensagem "Selecione um paciente". Exibido quando patientPathway é null.',
      },
    },
  },
};

/** Pathway concluído — todos os critérios atendidos, status "completed", sem recomendação pendente. */
export const Completed: Story = {
  args: {
    patientPathway: getCompletedPathway(),
    progress: getCompletedProgress(),
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Pathway de Ventilação Mecânica concluído com status "Concluído", 4/4 critérios atendidos (100%) e badge verde de conclusão.',
      },
    },
  },
};

/** Pathway em atraso (overdue) — severidade "critical", apenas 1/3 critérios atendidos, recomendação urgente com animação pulse. */
export const Overdue: Story = {
  args: {
    patientPathway: getOverduePathway(),
    progress: getOverdueProgress(),
    isLoading: false,
    error: null,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Pathway de Profilaxia de TEV com severidade "critical" e status overdue. Exibe recomendação urgente com animação pulse e alerta visual. Apenas 1/3 critérios atendidos.',
      },
    },
  },
};
