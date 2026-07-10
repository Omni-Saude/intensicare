import type { Meta, StoryObj } from '@storybook/react';
import type { ScoreRecord } from '@/lib/api';
import { ScoreTimeline } from './score-timeline';

const mockScores: ScoreRecord[] = [
  { name: 'MEWS', value: 7, measured_at: '2026-07-09T12:00:00Z', trend: 'up' },
  { name: 'MEWS', value: 5, measured_at: '2026-07-09T10:00:00Z', trend: 'up' },
  { name: 'MEWS', value: 3, measured_at: '2026-07-09T08:00:00Z', trend: 'stable' },
  { name: 'MEWS', value: 3, measured_at: '2026-07-09T06:00:00Z', trend: 'stable' },
  { name: 'MEWS', value: 2, measured_at: '2026-07-09T04:00:00Z', trend: 'stable' },
  { name: 'MEWS', value: 1, measured_at: '2026-07-09T02:00:00Z', trend: 'down' },
  { name: 'MEWS', value: 1, measured_at: '2026-07-09T00:00:00Z', trend: 'stable' },
  { name: 'NEWS2', value: 8, measured_at: '2026-07-09T12:00:00Z', trend: 'up' },
  { name: 'NEWS2', value: 6, measured_at: '2026-07-09T10:00:00Z', trend: 'up' },
  { name: 'NEWS2', value: 4, measured_at: '2026-07-09T08:00:00Z', trend: 'stable' },
  { name: 'NEWS2', value: 3, measured_at: '2026-07-09T06:00:00Z', trend: 'stable' },
  { name: 'NEWS2', value: 2, measured_at: '2026-07-09T04:00:00Z', trend: 'stable' },
  { name: 'NEWS2', value: 1, measured_at: '2026-07-09T02:00:00Z', trend: 'down' },
  { name: 'NEWS2', value: 1, measured_at: '2026-07-09T00:00:00Z', trend: 'stable' },
];

const meta: Meta<typeof ScoreTimeline> = {
  title: 'Patient/ScoreTimeline',
  component: ScoreTimeline,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ScoreTimeline>;

export const Default: Story = {
  args: {
    scores: mockScores,
    alertTimes: ['2026-07-09T12:00:00Z'],
  },
};

export const Loading: Story = {
  args: {
    scores: [],
    isLoading: true,
  },
};

export const ErrorState: Story = {
  args: {
    scores: [],
    error: 'Falha ao carregar scores',
  },
};

export const Empty: Story = {
  args: {
    scores: [],
  },
};

export const MultipleAlerts: Story = {
  args: {
    scores: mockScores,
    alertTimes: [
      '2026-07-09T12:00:00Z',
      '2026-07-09T10:00:00Z',
      '2026-07-09T06:00:00Z',
    ],
  },
};
