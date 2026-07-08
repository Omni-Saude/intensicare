import type { Meta, StoryObj } from '@storybook/react';
import CriteriaChecklist from './CriteriaChecklist';
import type { Criterion } from './CriteriaChecklist';

// ─── Mock Data Factories ───────────────────────────────────────────────────

function makeSepsisCriteria(): Criterion[] {
  return [
    {
      id: 'major-1',
      label: 'Hipotensão (PAS < 90 mmHg)',
      description: 'Pressão arterial sistólica abaixo do limiar de choque séptico',
      category: 'major',
      met: true,
      value: 'PAS 82',
      threshold: '< 90 mmHg',
    },
    {
      id: 'major-2',
      label: 'Lactato > 2 mmol/L',
      description: 'Marcador de hipoperfusão tecidual',
      category: 'major',
      met: true,
      value: '3.4 mmol/L',
      threshold: '> 2 mmol/L',
    },
    {
      id: 'major-3',
      label: 'qSOFA ≥ 2',
      description: 'Quick SOFA score para triagem de sepse',
      category: 'major',
      met: true,
      value: '2',
      threshold: '≥ 2',
    },
    {
      id: 'major-4',
      label: 'Necessidade de Vasopressor',
      category: 'major',
      met: false,
    },
    {
      id: 'minor-1',
      label: 'Leucocitose > 12.000',
      category: 'minor',
      met: true,
      value: '14.200',
      threshold: '> 12.000',
    },
    {
      id: 'minor-2',
      label: 'Febre > 38°C',
      category: 'minor',
      met: true,
      value: '38.5°C',
      threshold: '> 38°C',
    },
    {
      id: 'minor-3',
      label: 'Taquipneia (FR > 22)',
      category: 'minor',
      met: false,
      value: '18 rpm',
      threshold: '> 22 rpm',
    },
    {
      id: 'minor-4',
      label: 'Creatinina elevada',
      category: 'minor',
      met: false,
    },
    {
      id: 'minor-5',
      label: 'Bilirrubina > 2 mg/dL',
      category: 'minor',
      met: false,
    },
  ];
}

function makeNutritionCriteria(): Criterion[] {
  return [
    {
      id: 'nut-1',
      label: 'Triagem nutricional (NRS-2002)',
      description: 'Nutritional Risk Screening nas primeiras 24h de admissão na UTI',
      category: 'triagem',
      met: true,
      value: 'NRS 5',
      threshold: '≥ 3',
    },
    {
      id: 'nut-2',
      label: 'Nutrição enteral iniciada em < 48h',
      description: 'Início precoce da terapia nutricional enteral',
      category: 'inicio',
      met: true,
      value: '32h',
      threshold: '< 48h',
    },
    {
      id: 'nut-3',
      label: 'Aporte calórico ≥ 80% da meta',
      category: 'aporte',
      met: false,
      value: '62%',
      threshold: '≥ 80%',
    },
    {
      id: 'nut-4',
      label: 'Proteína ≥ 1.2 g/kg/dia',
      category: 'proteina',
      met: true,
      value: '1.4 g/kg',
      threshold: '≥ 1.2 g/kg',
    },
    {
      id: 'nut-5',
      label: 'Controle glicêmico (80-180 mg/dL)',
      category: 'glicemia',
      met: true,
      value: '142 mg/dL',
      threshold: '80-180 mg/dL',
    },
    {
      id: 'nut-6',
      label: 'Monitorização de resíduo gástrico',
      category: 'monitorizacao',
      met: false,
      value: '280 ml/6h',
      threshold: '< 250 ml/6h',
    },
    {
      id: 'nut-7',
      label: 'Suplementação de micronutrientes',
      category: 'suplementacao',
      met: false,
    },
  ];
}

function makeAllMetCriteria(): Criterion[] {
  return makeSepsisCriteria().map((c) => ({ ...c, met: true }));
}

function makeAntimicrobialCriteria(): Criterion[] {
  return [
    {
      id: 'am-1',
      label: 'Cultura antes do antibiótico',
      category: 'coleta',
      met: true,
    },
    {
      id: 'am-2',
      label: 'Antibiótico em < 1h (sepse)',
      category: 'tempo',
      met: true,
      value: '42 min',
      threshold: '< 60 min',
    },
    {
      id: 'am-3',
      label: 'Ajuste para função renal',
      category: 'dose',
      met: false,
    },
    {
      id: 'am-4',
      label: 'Espectro adequado à fonte',
      category: 'espectro',
      met: true,
    },
    {
      id: 'am-5',
      label: 'Revisão em 48-72h',
      category: 'duracao',
      met: false,
    },
    {
      id: 'am-6',
      label: 'Descalonamento documentado',
      category: 'espectro',
      met: false,
    },
  ];
}

// ─── Meta ──────────────────────────────────────────────────────────────────

const meta: Meta<typeof CriteriaChecklist> = {
  title: 'Components/CriteriaChecklist',
  component: CriteriaChecklist,
  tags: ['autodocs'],
  argTypes: {
    domain: {
      control: 'select',
      options: ['sepsis', 'antimicrobial', 'nutrition'],
    },
    readOnly: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof CriteriaChecklist>;

const noop = () => {};

// ─── Stories ───────────────────────────────────────────────────────────────

export const Default: Story = {
  args: {
    items: makeSepsisCriteria(),
    domain: 'sepsis',
    onToggle: noop,
    readOnly: false,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Checklist de critérios de sepse com itens atendidos (verde) e não atendidos (cinza), valores e limiares.',
      },
    },
  },
};

export const Antimicrobial: Story = {
  args: {
    items: makeAntimicrobialCriteria(),
    domain: 'antimicrobial',
    onToggle: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Checklist de stewardship antimicrobiano usando tokens do domínio antimicrobiano.',
      },
    },
  },
};

export const Nutrition: Story = {
  args: {
    items: makeNutritionCriteria(),
    domain: 'nutrition',
    onToggle: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Checklist de terapia nutricional — critérios de triagem, aporte calórico, proteico, controle glicêmico e monitorização. Usa tokens do domínio nutrition.',
      },
    },
  },
};

export const AllMet: Story = {
  args: {
    items: makeAllMetCriteria(),
    domain: 'sepsis',
    onToggle: noop,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Todos os critérios atendidos — indicadores verdes consistentes.',
      },
    },
  },
};

export const ReadOnly: Story = {
  args: {
    items: makeSepsisCriteria(),
    domain: 'sepsis',
    readOnly: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Modo somente leitura — sem checkboxes interativos, apenas ícones de status.',
      },
    },
  },
};

export const Loading: Story = {
  args: {
    items: [],
    domain: 'sepsis',
    isLoading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de carregamento com skeleton rows animados.',
      },
    },
  },
};

export const Empty: Story = {
  args: {
    items: [],
    domain: 'sepsis',
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado vazio quando nenhum critério foi configurado para o domínio.',
      },
    },
  },
};

export const Error: Story = {
  args: {
    items: [],
    domain: 'sepsis',
    error: 'Erro ao carregar critérios. Verifique a conexão com o servidor.',
  },
  parameters: {
    docs: {
      description: {
        story: 'Estado de erro com mensagem e ícone de alerta (role="alert").',
      },
    },
  },
};

export const Pathway: Story = {
  args: {
    items: makePathwayCriteria(),
    domain: 'pathway',
    readOnly: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Checklist de critérios de pathway clínico — tokens visuais do domínio pathway (active/overdue). Modo somente leitura com ícones de status (CheckCircle/XCircle).',
      },
    },
  },
};

// ─── Pathway mock data ─────────────────────────────────────────────────────

function makePathwayCriteria(): Criterion[] {
  return [
    {
      id: 'path-lactato',
      label: 'Lactato sérico',
      description: 'Dosagem de lactato na primeira hora',
      category: 'Laboratorial',
      met: true,
      value: '3.2 mmol/L',
      threshold: '< 2.0',
    },
    {
      id: 'path-hemocultura',
      label: 'Hemoculturas',
      description: 'Coleta de 2 pares de hemoculturas antes do antibiótico',
      category: 'Microbiologia',
      met: true,
    },
    {
      id: 'path-antibiotico',
      label: 'Antibiótico IV',
      description: 'Antibioticoterapia endovenosa de amplo espectro iniciada',
      category: 'Medicação',
      met: true,
    },
    {
      id: 'path-fluidos',
      label: 'Fluidos EV',
      description: 'Ressuscitação volêmica com 30 mL/kg de cristaloide',
      category: 'Intervenção',
      met: false,
      value: '1000 mL',
      threshold: '30 mL/kg',
    },
    {
      id: 'path-vasopressor',
      label: 'Vasopressor',
      description: 'Iniciar vasopressor se PAM < 65 mmHg após fluidos',
      category: 'Intervenção',
      met: false,
    },
  ];
}
