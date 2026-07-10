import type { Meta, StoryObj } from '@storybook/react';
import { SeverityBadge } from '../components/alerts/severity-badge';

const meta: Meta<typeof SeverityBadge> = {
  title: 'Alerts/SeverityBadge',
  component: SeverityBadge,
  tags: ['autodocs'],
  argTypes: {
    severity: {
      control: 'select',
      options: ['normal', 'watch', 'urgent', 'critical'],
      description: 'Nível de severidade clínica',
    },
    className: {
      control: 'text',
      description: 'Classes CSS adicionais',
    },
  },
};

export default meta;
type Story = StoryObj<typeof SeverityBadge>;

export const Normal: Story = {
  args: { severity: 'normal' },
};

export const Watch: Story = {
  args: { severity: 'watch' },
};

export const Urgent: Story = {
  args: { severity: 'urgent' },
};

export const Critical: Story = {
  args: { severity: 'critical' },
};

export const WithCustomClass: Story = {
  args: {
    severity: 'watch',
    className: 'text-sm px-4 py-1',
  },
};
