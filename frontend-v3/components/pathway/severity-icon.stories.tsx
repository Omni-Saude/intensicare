import type { Meta, StoryObj } from '@storybook/react';
import { SeverityIcon } from './severity-icon';

const meta: Meta<typeof SeverityIcon> = {
  title: 'Pathway/SeverityIcon',
  component: SeverityIcon,
  tags: ['autodocs'],
  argTypes: {
    met: { control: 'radio', options: [true, false, null], description: 'Critério atendido (true/false/null)' },
    severity: { control: 'select', options: ['normal', 'watch', 'urgent', 'critical', null], description: 'Nível de severidade' },
    className: { control: 'text', description: 'Classes CSS adicionais' },
  },
};

export default meta;
type Story = StoryObj<typeof SeverityIcon>;

export const MetTrue: Story = { args: { met: true } };
export const MetFalse: Story = { args: { met: false } };
export const Pending: Story = { args: { met: null } };

export const SeverityNormal: Story = { args: { met: undefined, severity: 'normal' } };
export const SeverityWatch: Story = { args: { met: undefined, severity: 'watch' } };
export const SeverityUrgent: Story = { args: { met: undefined, severity: 'urgent' } };
export const SeverityCritical: Story = { args: { met: undefined, severity: 'critical' } };

export const MetOverridesSeverity: Story = { args: { met: true, severity: 'critical' } };
export const NotMetOverridesSeverity: Story = { args: { met: false, severity: 'normal' } };
