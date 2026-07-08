import type { Meta, StoryObj } from '@storybook/react';
import HandoffMessageCard from './HandoffMessageCard';
import type { HandoffMessage } from '@/lib/communication-types';

// ─── Mock Data ────────────────────────────────────────────────────────────────

function makeUnreadMessage(): HandoffMessage {
  return {
    id: 'msg-001',
    from_user: 'Dra. Camila Rocha',
    to_shift: 'Tarde (13:00-19:00)',
    sbar_s:
      'Paciente João, 68a, pós-op cardíaco (revascularização), extubado há 4h. Glasgow 15, estável hemodinamicamente.',
    sbar_b:
      'IMC 29, DM2 controlado, IAM há 2 anos. Cirurgia sem intercorrências. CEC 72 min. Dreno mediastinal com débito sero-hemático 50 mL/h.',
    sbar_a:
      'Evolução favorável. Sem sinais de tamponamento ou sangramento ativo. Gasometria arterial com PaO2 92 mmHg, lactato 1.4 mmol/L.',
    sbar_r:
      'Manter monitorização do débito do dreno a cada hora. Previsão de retirada do dreno amanhã cedo. Iniciar deambulação assistida se mantiver estabilidade.',
    created_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    read: false,
    urgent: false,
  };
}

function makeReadMessage(): HandoffMessage {
  return {
    id: 'msg-003',
    from_user: 'Dr. Rafael Cunha',
    to_shift: 'Manhã (07:00-13:00)',
    sbar_s:
      'Paciente Carlos, 55a, TCE grave, pós-craniectomia descompressiva. PIC controlada, sedação com propofol e fentanil.',
    sbar_b:
      'Vítima de acidente automobilístico há 5 dias. Craniectomia frontotemporal direita. Monitorização com cateter de PIC (valores 12-18 mmHg).',
    sbar_a:
      'PIC estável nas últimas 12h, sem ondas plateau. Tomografia de controle sem novas lesões. Edema cerebral em regressão.',
    sbar_r:
      'Manter cabeceira elevada 30°, sedação profunda (RASS -4). Evitar hipertermia e hiponatremia. Coletar eletrólitos às 6h.',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    read: true,
    urgent: false,
  };
}

function makeUrgentMessage(): HandoffMessage {
  return {
    id: 'msg-002',
    from_user: 'Enf. Marcos Teixeira',
    to_shift: 'Noite (19:00-07:00)',
    sbar_s:
      'Paciente Maria, 74a, sepse urinária, em meropenem. PAM 68 mmHg, noradrenalina 0.12 mcg/kg/min.',
    sbar_b:
      'Admitida há 48h por ITU complicada com progressão para choque séptico. Hemoculturas colhidas na admissão com E. coli sensível a meropenem.',
    sbar_a:
      'Ainda dependente de vasopressor em dose baixa-moderada. Diurese mantida (~0.6 mL/kg/h). Procalcitonina em queda (12 → 4.5 ng/mL).',
    sbar_r:
      'Tentar desmame da noradrenalina durante a noite (meta PAM ≥ 65). Colher nova procalcitonina às 23h.',
    created_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    read: false,
    urgent: true,
  };
}

// ─── Meta ─────────────────────────────────────────────────────────────────────

const meta: Meta<typeof HandoffMessageCard> = {
  title: 'Components/HandoffMessageCard',
  component: HandoffMessageCard,
  tags: ['autodocs'],
  argTypes: {
    message: {
      control: 'object',
      description: 'Mensagem de handoff no formato SBAR (Situation, Background, Assessment, Recommendation)',
    },
    onMarkRead: {
      action: 'marked-read',
      description: 'Callback executado quando o usuário marca a mensagem como lida',
    },
    isLoading: {
      control: 'boolean',
      description: 'Exibe skeleton de carregamento do card',
    },
    error: {
      control: 'text',
      description: 'Mensagem de erro — exibe alerta no lugar do card',
    },
  },
};

export default meta;
type Story = StoryObj<typeof HandoffMessageCard>;

// ─── Stories ──────────────────────────────────────────────────────────────────

export const Unread: Story = {
  args: {
    message: makeUnreadMessage(),
    onMarkRead: undefined,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Mensagem não lida — dot indicador azul, borda esquerda destacada (4px), seções SBAR colapsáveis e botão "Marcar como lida".',
      },
    },
  },
};

export const Read: Story = {
  args: {
    message: makeReadMessage(),
  },
  parameters: {
    docs: {
      description: {
        story:
          'Mensagem já lida — sem dot indicador, borda padrão (1px), sem botão "Marcar como lida".',
      },
    },
  },
};

export const Urgent: Story = {
  args: {
    message: makeUrgentMessage(),
    onMarkRead: undefined,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Mensagem urgente — badge "Urgente" com ícone AlertTriangle, borda na cor de severidade urgente, dot de não lida ativo.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    message: {} as HandoffMessage,
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado de carregamento — skeleton animado com avatar, linhas de texto e aria-busy="true".',
      },
    },
  },
};

export const Error: Story = {
  args: {
    message: {} as HandoffMessage,
    error: 'Erro ao carregar mensagem de handoff. Tente novamente.',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado de erro — alerta visual com role="alert", ícone AlertTriangle e mensagem descritiva.',
      },
    },
  },
};
