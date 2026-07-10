import type { Meta, StoryObj } from '@storybook/react';
import { PathwayDefCard } from './pathway-def-card';
import type { Pathway } from '@/lib/api';

const mockPathway: Pathway = {
  id: 1,
  name: 'Sepse',
  slug: 'sepsis',
  description: 'Protocolo de manejo de sepse — identificação precoce e tratamento guiado por metas',
  active: true,
  states: [
    { id: 'triage', name: 'Triagem', order: 1 },
    { id: 'diagnosis', name: 'Diagnóstico', order: 2 },
    { id: 'treatment', name: 'Tratamento', order: 3 },
  ],
  criteria: [
    { id: 'c1', name: 'Lactato > 2', category: 'lab' },
    { id: 'c2', name: 'Hipotensão', category: 'vital' },
  ],
};

const inactivePathway: Pathway = {
  ...mockPathway,
  id: 2,
  name: 'Protocolo Antigo',
  slug: 'old-protocol',
  active: false,
};

const emptyPathway: Pathway = {
  id: 3,
  name: 'Trilha Vazia',
  slug: 'empty',
  active: true,
  states: [],
  criteria: [],
};

const meta: Meta<typeof PathwayDefCard> = {
  title: 'Pathways/PathwayDefCard',
  component: PathwayDefCard,
  tags: ['autodocs'],
  argTypes: {
    pathway: { control: 'object', description: 'Dados da trilha clínica (Pathway)' },
    isExpanded: { control: 'boolean', description: 'Estado expandido do card' },
    onToggle: { action: 'toggled', description: 'Callback de toggle expandir/recolher' },
  },
};

export default meta;
type Story = StoryObj<typeof PathwayDefCard>;

export const Default: Story = {
  args: { pathway: mockPathway, isExpanded: false },
};

export const Expanded: Story = {
  args: { pathway: mockPathway, isExpanded: true },
};

export const Inactive: Story = {
  args: { pathway: inactivePathway, isExpanded: false },
};

export const EmptyStatesAndCriteria: Story = {
  args: { pathway: emptyPathway, isExpanded: false },
};

export const NoDescription: Story = {
  args: { pathway: { ...mockPathway, id: 4, description: undefined }, isExpanded: false },
};

export const LongDescription: Story = {
  args: {
    pathway: {
      ...mockPathway,
      id: 5,
      description: 'Protocolo abrangente de manejo que inclui avaliação inicial detalhada, exames complementares, terapias específicas e acompanhamento prolongado do paciente crítico em UTI.',
    },
    isExpanded: false,
  },
};
