import type { Meta, StoryObj } from '@storybook/react';
import { StateFlow } from './state-flow';
import type { PathwayState, StateTransition } from '@/lib/api';

const mockStates: PathwayState[] = [
  { id: 'triage', name: 'Triagem Inicial', order: 1, description: 'Avaliação inicial' },
  { id: 'diagnosis', name: 'Diagnóstico', order: 2, description: 'Confirmação diagnóstica' },
  { id: 'treatment', name: 'Tratamento', order: 3, description: 'Intervenção terapêutica' },
  { id: 'monitoring', name: 'Monitorização', order: 4, description: 'Acompanhamento contínuo' },
  { id: 'discharge', name: 'Alta', order: 5, description: 'Critérios de saída', is_terminal: true },
];

const mockHistory: StateTransition[] = [
  { to_state: 'triage', changed_at: '2026-07-08T10:00:00Z' },
  { from_state: 'triage', to_state: 'diagnosis', changed_at: '2026-07-08T14:30:00Z', reason: 'Critérios de triagem atendidos' },
  { from_state: 'diagnosis', to_state: 'treatment', changed_at: '2026-07-09T08:00:00Z', reason: 'Diagnóstico confirmado' },
];

const meta: Meta<typeof StateFlow> = {
  title: 'Pathway/StateFlow',
  component: StateFlow,
  tags: ['autodocs'],
  argTypes: {
    states: { control: 'object', description: 'Lista de estados da trilha clínica' },
    currentStateId: { control: 'text', description: 'ID do estado atual' },
    history: { control: 'object', description: 'Histórico de transições de estado' },
  },
};

export default meta;
type Story = StoryObj<typeof StateFlow>;

export const Default: Story = {
  args: { states: mockStates, currentStateId: 'treatment', history: mockHistory },
};

export const Empty: Story = {
  args: { states: [], currentStateId: '', history: [] },
};

export const AtFirstState: Story = {
  args: { states: mockStates, currentStateId: 'triage', history: [] },
};

export const AtLastState: Story = {
  args: { states: mockStates, currentStateId: 'discharge', history: mockHistory },
};

export const SingleState: Story = {
  args: {
    states: [{ id: 'single', name: 'Estado Único', order: 1, is_terminal: true }],
    currentStateId: 'single',
    history: [],
  },
};
