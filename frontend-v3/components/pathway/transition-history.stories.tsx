import type { Meta, StoryObj } from '@storybook/react';
import { TransitionHistory } from './transition-history';
import type { StateTransition } from '@/lib/api';

const mockHistory: StateTransition[] = [
  { to_state: 'Triagem Inicial', changed_at: '2026-07-08T10:00:00Z' },
  { from_state: 'Triagem Inicial', to_state: 'Diagnóstico', changed_at: '2026-07-08T14:30:00Z', reason: 'Critérios de triagem atendidos — lactato elevado' },
  { from_state: 'Diagnóstico', to_state: 'Tratamento', changed_at: '2026-07-09T08:00:00Z', reason: 'Diagnóstico de sepse confirmado' },
  { from_state: 'Tratamento', to_state: 'Monitorização', changed_at: '2026-07-09T16:00:00Z', reason: 'Paciente estabilizado, transição para monitorização' },
];

const meta: Meta<typeof TransitionHistory> = {
  title: 'Pathway/TransitionHistory',
  component: TransitionHistory,
  tags: ['autodocs'],
  argTypes: {
    history: { control: 'object', description: 'Lista de transições de estado (StateTransition[])' },
  },
};

export default meta;
type Story = StoryObj<typeof TransitionHistory>;

export const Default: Story = {
  args: { history: mockHistory },
};

export const SingleTransition: Story = {
  args: { history: [mockHistory[0]] },
};

export const Empty: Story = {
  args: { history: [] },
};
