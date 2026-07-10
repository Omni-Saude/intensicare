import type { Meta, StoryObj } from '@storybook/react';
import { PathwayBadges } from './pathway-badges';

const meta: Meta<typeof PathwayBadges> = {
  title: 'Dashboard/PathwayBadges',
  component: PathwayBadges,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof PathwayBadges>;

export const SinglePathway: Story = {
  args: {
    pathways: [
      { slug: 'sepsis', severity: 'urgent' },
    ],
  },
};

export const MultiplePathways: Story = {
  args: {
    pathways: [
      { slug: 'sepsis', severity: 'critical' },
      { slug: 'aki', severity: 'urgent' },
      { slug: 'delirium', severity: 'watch' },
    ],
  },
};

export const MaxVisibleWithOverflow: Story = {
  args: {
    pathways: [
      { slug: 'sepsis', severity: 'critical' },
      { slug: 'aki', severity: 'urgent' },
      { slug: 'vap', severity: 'urgent' },
      { slug: 'delirium', severity: 'watch' },
      { slug: 'post-op', severity: 'normal' },
      { slug: 'nutrition', severity: 'normal' },
    ],
  },
};

export const AllNormal: Story = {
  args: {
    pathways: [
      { slug: 'post-op', severity: 'normal' },
      { slug: 'nutrition', severity: 'normal' },
    ],
  },
};

export const Empty: Story = {
  args: {
    pathways: [],
  },
};
