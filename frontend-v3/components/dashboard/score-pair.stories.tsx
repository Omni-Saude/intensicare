import type { Meta, StoryObj } from '@storybook/react';
import { ScorePair } from './score-pair';

const meta: Meta<typeof ScorePair> = {
  title: 'Dashboard/ScorePair',
  component: ScorePair,
  tags: ['autodocs'],
  argTypes: {
    mews: {
      control: 'number',
      description: 'Valor do MEWS (Modified Early Warning Score)',
    },
    news2: {
      control: 'number',
      description: 'Valor do NEWS2 (National Early Warning Score 2)',
    },
  },
};

export default meta;
type Story = StoryObj<typeof ScorePair>;

export const BothScores: Story = {
  args: {
    mews: 6,
    news2: 7,
  },
};

export const OnlyMews: Story = {
  args: {
    mews: 3,
    news2: null,
  },
};

export const OnlyNews2: Story = {
  args: {
    mews: null,
    news2: 8,
  },
};

export const Normal: Story = {
  args: {
    mews: 1,
    news2: 2,
  },
};

export const Critical: Story = {
  args: {
    mews: 8,
    news2: 9,
  },
};

export const BothNull: Story = {
  args: {
    mews: null,
    news2: null,
  },
};
