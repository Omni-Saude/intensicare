import type { Meta, StoryObj } from '@storybook/react';
import { CriteriaList } from './criteria-list';
import type { PathwayCriteria } from '@/lib/api';

const mockCriteria: PathwayCriteria[] = [
  { id: 'c1', name: 'Lactato > 2 mmol/L', category: 'lab', met: true, value: '3.2', unit: 'mmol/L', alert_threshold: '≥2.0', normal_range: '0.5–1.6' },
  { id: 'c2', name: 'Hipotensão (PAS < 90)', category: 'vital', met: true, value: '85', unit: 'mmHg', alert_threshold: '≥90', normal_range: '90–120' },
  { id: 'c3', name: 'FC > 90 bpm', category: 'vital', met: false, value: '72', unit: 'bpm', alert_threshold: '≥90', normal_range: '60–100' },
  { id: 'c4', name: 'FR > 20 rpm', category: 'vital', met: true, value: '24', unit: 'rpm' },
  { id: 'c5', name: 'Hemocultura positiva', category: 'lab', met: false },
  { id: 'c6', name: 'PCR elevada', category: 'lab' },
];

const summaryMet = { total: 6, met: 3, not_met: 2, pending: 1 };
const summaryAllMet = { total: 3, met: 3, not_met: 0, pending: 0 };
const summaryNoneMet = { total: 3, met: 0, not_met: 3, pending: 0 };

const meta: Meta<typeof CriteriaList> = {
  title: 'Pathway/CriteriaList',
  component: CriteriaList,
  tags: ['autodocs'],
  argTypes: {
    criteria: { control: 'object', description: 'Lista de critérios da trilha' },
    summary: { control: 'object', description: 'Resumo de critérios (total/met/not_met/pending)' },
    isLoading: { control: 'boolean', description: 'Estado de carregamento' },
    error: { control: 'text', description: 'Mensagem de erro' },
  },
};

export default meta;
type Story = StoryObj<typeof CriteriaList>;

export const Default: Story = {
  args: { criteria: mockCriteria, summary: summaryMet },
};

export const AllMet: Story = {
  args: { criteria: mockCriteria.slice(0, 3).map(c => ({ ...c, met: true })), summary: summaryAllMet },
};

export const NoneMet: Story = {
  args: { criteria: mockCriteria.slice(0, 3).map(c => ({ ...c, met: false })), summary: summaryNoneMet },
};

export const Loading: Story = {
  args: { criteria: undefined, summary: { total: 0, met: 0, not_met: 0, pending: 0 }, isLoading: true },
};

export const ErrorState: Story = {
  args: { criteria: undefined, summary: { total: 0, met: 0, not_met: 0, pending: 0 }, error: 'Falha na conexão com o servidor' },
};

export const Empty: Story = {
  args: { criteria: [], summary: { total: 0, met: 0, not_met: 0, pending: 0 } },
};
