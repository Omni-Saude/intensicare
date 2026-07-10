import type { Meta, StoryObj } from '@storybook/react';
import { StateLabel } from './state-label';

const meta: Meta<typeof StateLabel> = {
  title: 'Patient/StateLabel',
  component: StateLabel,
  tags: ['autodocs'],
  argTypes: {
    severity: {
      control: 'select',
      options: ['normal', 'watch', 'urgent', 'critical'],
      description: 'Nível de severidade',
    },
    label: {
      control: 'text',
      description: 'Texto do label',
    },
    className: {
      control: 'text',
      description: 'Classes CSS adicionais',
    },
  },
};

export default meta;
type Story = StoryObj<typeof StateLabel>;

export const Normal: Story = {
  args: {
    label: 'Estável',
    severity: 'normal',
  },
};

export const Watch: Story = {
  args: {
    label: 'Observação',
    severity: 'watch',
  },
};

export const Urgent: Story = {
  args: {
    label: 'Urgente',
    severity: 'urgent',
  },
};

export const Critical: Story = {
  args: {
    label: 'Crítico',
    severity: 'critical',
  },
};

export const LongLabel: Story = {
  args: {
    label: 'Aguardando Transferência',
    severity: 'watch',
  },
};
