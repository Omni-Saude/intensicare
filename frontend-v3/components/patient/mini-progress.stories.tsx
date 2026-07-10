import type { Meta, StoryObj } from '@storybook/react';
import { MiniProgress } from './mini-progress';

const meta: Meta<typeof MiniProgress> = {
  title: 'Patient/MiniProgress',
  component: MiniProgress,
  tags: ['autodocs'],
  argTypes: {
    met: {
      control: 'number',
      description: 'Número de critérios atendidos',
    },
    total: {
      control: 'number',
      description: 'Número total de critérios',
    },
    label: {
      control: 'text',
      description: 'Label de acessibilidade',
    },
  },
};

export default meta;
type Story = StoryObj<typeof MiniProgress>;

export const HalfComplete: Story = {
  args: {
    met: 3,
    total: 6,
    label: 'Progresso da trilha',
  },
};

export const AlmostComplete: Story = {
  args: {
    met: 7,
    total: 8,
  },
};

export const Empty: Story = {
  args: {
    met: 0,
    total: 5,
  },
};

export const Full: Story = {
  args: {
    met: 5,
    total: 5,
  },
};

export const LowProgress: Story = {
  args: {
    met: 1,
    total: 4,
  },
};

export const LargeCount: Story = {
  args: {
    met: 4,
    total: 12,
    label: 'Critérios da trilha Sepse',
  },
};
