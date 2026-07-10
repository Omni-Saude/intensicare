import type { Meta, StoryObj } from '@storybook/react';
import { CriteriaRow } from './criteria-row';
import type { PathwayCriteria } from '@/lib/api';

const metCriterion: PathwayCriteria = {
  id: 'c1',
  name: 'Lactato > 2 mmol/L',
  category: 'lab',
  description: 'Nível de lactato sérico acima do limiar de alerta',
  met: true,
  value: '3.2',
  unit: 'mmol/L',
  normal_range: '0.5–1.6',
  alert_threshold: '≥2.0',
  evaluated_at: '2026-07-09T08:00:00Z',
};

const notMetCriterion: PathwayCriteria = {
  id: 'c2',
  name: 'FC > 90 bpm',
  category: 'vital',
  description: 'Frequência cardíaca elevada',
  met: false,
  value: '72',
  unit: 'bpm',
  normal_range: '60–100',
  alert_threshold: '≥90',
  evaluated_at: '2026-07-09T07:45:00Z',
};

const pendingCriterion: PathwayCriteria = {
  id: 'c3',
  name: 'Hemocultura positiva',
  category: 'lab',
  description: 'Resultado de hemocultura com crescimento bacteriano',
};

const meta: Meta<typeof CriteriaRow> = {
  title: 'Pathway/CriteriaRow',
  component: CriteriaRow,
  tags: ['autodocs'],
  argTypes: {
    criterion: { control: 'object', description: 'Dados do critério (PathwayCriteria)' },
    isExpanded: { control: 'boolean', description: 'Estado expandido do critério' },
    onToggle: { action: 'toggled', description: 'Callback de toggle expandir/recolher' },
  },
};

export default meta;
type Story = StoryObj<typeof CriteriaRow>;

export const Met: Story = {
  args: { criterion: metCriterion, isExpanded: false },
};

export const NotMet: Story = {
  args: { criterion: notMetCriterion, isExpanded: false },
};

export const Pending: Story = {
  args: { criterion: pendingCriterion, isExpanded: false },
};

export const Expanded: Story = {
  args: { criterion: metCriterion, isExpanded: true },
};

export const WithoutValue: Story = {
  args: {
    criterion: { id: 'c4', name: 'Critério sem valor', category: 'clinical', met: false },
    isExpanded: false,
  },
};
