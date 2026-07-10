import type { Meta, StoryObj } from '@storybook/react';
import { SeverityDot } from '../components/dashboard/severity-dot';

const meta: Meta<typeof SeverityDot> = {
  title: 'Dashboard/SeverityDot',
  component: SeverityDot,
  tags: ['autodocs'],
  argTypes: {
    severity: {
      control: 'select',
      options: ['normal', 'watch', 'urgent', 'critical'],
      description: 'Nível de severidade clínica',
    },
  },
};

export default meta;
type Story = StoryObj<typeof SeverityDot>;

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
