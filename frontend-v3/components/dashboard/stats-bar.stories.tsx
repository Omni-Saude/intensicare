import type { Meta, StoryObj } from '@storybook/react';
import { StatsBar } from './stats-bar';

const meta: Meta<typeof StatsBar> = {
  title: 'Dashboard/StatsBar',
  component: StatsBar,
  tags: ['autodocs'],
  argTypes: {
    total: {
      control: 'number',
      description: 'Total de pacientes',
    },
    criticalCount: {
      control: 'number',
      description: 'Número de pacientes críticos',
    },
    unit: {
      control: 'text',
      description: 'Nome da unidade filtrada',
    },
  },
};

export default meta;
type Story = StoryObj<typeof StatsBar>;

export const WithCriticals: Story = {
  args: {
    total: 12,
    criticalCount: 3,
  },
};

export const NoCriticals: Story = {
  args: {
    total: 8,
    criticalCount: 0,
  },
};

export const WithUnitFilter: Story = {
  args: {
    total: 5,
    criticalCount: 2,
    unit: 'UTI Adulto',
  },
};

export const LargeWard: Story = {
  args: {
    total: 24,
    criticalCount: 0,
    unit: 'Enfermaria',
  },
};
