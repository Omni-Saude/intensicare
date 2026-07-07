import type { Meta, StoryObj } from '@storybook/react';
import SeverityBadge, { TrendBadge, ScoreDisplay } from './SeverityBadge';

const meta: Meta<typeof SeverityBadge> = {
  title: 'Components/SeverityBadge',
  component: SeverityBadge,
  tags: ['autodocs'],
  argTypes: {
    severity: {
      control: 'select',
      options: ['normal', 'watch', 'urgent', 'critical', 'info'],
    },
    showLabel: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof SeverityBadge>;

// ─── Severity Badge Variants ──────────────────────────────────────────────────

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

export const Info: Story = {
  args: { severity: 'info' },
};

export const WithoutLabel: Story = {
  args: { severity: 'critical', showLabel: false },
};

export const CriticalWithPulse: Story = {
  args: { severity: 'critical' },
};

export const AllSeverities: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
      <SeverityBadge severity="normal" />
      <SeverityBadge severity="watch" />
      <SeverityBadge severity="urgent" />
      <SeverityBadge severity="critical" />
      <SeverityBadge severity="info" />
    </div>
  ),
};

export const AllSeveritiesNoLabel: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
      <SeverityBadge severity="normal" showLabel={false} />
      <SeverityBadge severity="watch" showLabel={false} />
      <SeverityBadge severity="urgent" showLabel={false} />
      <SeverityBadge severity="critical" showLabel={false} />
      <SeverityBadge severity="info" showLabel={false} />
    </div>
  ),
};

// ─── TrendBadge Variants ──────────────────────────────────────────────────────

const TrendBadgeMeta: Meta<typeof TrendBadge> = {
  title: 'Components/SeverityBadge/TrendBadge',
  component: TrendBadge,
  tags: ['autodocs'],
};

export const TrendIncreasing: StoryObj<typeof TrendBadge> = {
  render: () => <TrendBadge trend="increasing" />,
};

export const TrendDecreasing: StoryObj<typeof TrendBadge> = {
  render: () => <TrendBadge trend="decreasing" />,
};

export const TrendStable: StoryObj<typeof TrendBadge> = {
  render: () => <TrendBadge trend={null} />,
};

export const TrendUnknown: StoryObj<typeof TrendBadge> = {
  render: () => <TrendBadge trend="unknown" />,
};

export const AllTrends: StoryObj<typeof TrendBadge> = {
  render: () => (
    <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem' }}>
        <TrendBadge trend="increasing" />
        <span style={{ fontSize: '0.6875rem', color: 'var(--semantic-text-secondary, #A6ADBB)' }}>Increasing</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem' }}>
        <TrendBadge trend="decreasing" />
        <span style={{ fontSize: '0.6875rem', color: 'var(--semantic-text-secondary, #A6ADBB)' }}>Decreasing</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem' }}>
        <TrendBadge trend={null} />
        <span style={{ fontSize: '0.6875rem', color: 'var(--semantic-text-secondary, #A6ADBB)' }}>Stable</span>
      </div>
    </div>
  ),
};

// ─── ScoreDisplay Variants ────────────────────────────────────────────────────

const ScoreDisplayMeta: Meta<typeof ScoreDisplay> = {
  title: 'Components/SeverityBadge/ScoreDisplay',
  component: ScoreDisplay,
  tags: ['autodocs'],
};

export const MEWSLow: StoryObj<typeof ScoreDisplay> = {
  render: () => <ScoreDisplay label="MEWS" score={1} />,
};

export const MEWSMedium: StoryObj<typeof ScoreDisplay> = {
  render: () => <ScoreDisplay label="MEWS" score={3} trend="increasing" />,
};

export const MEWSHigh: StoryObj<typeof ScoreDisplay> = {
  render: () => <ScoreDisplay label="MEWS" score={6} risk="high" trend="increasing" />,
};

export const NEWS2Low: StoryObj<typeof ScoreDisplay> = {
  render: () => <ScoreDisplay label="NEWS2" score={2} risk="low" trend="stable" />,
};

export const NEWS2Medium: StoryObj<typeof ScoreDisplay> = {
  render: () => <ScoreDisplay label="NEWS2" score={5} risk="medium" trend="increasing" />,
};

export const NEWS2High: StoryObj<typeof ScoreDisplay> = {
  render: () => <ScoreDisplay label="NEWS2" score={8} risk="high" trend="increasing" />,
};

export const ScoreNull: StoryObj<typeof ScoreDisplay> = {
  render: () => <ScoreDisplay label="MEWS" score={null} />,
};

export const ScoreDisplayGrid: StoryObj<typeof ScoreDisplay> = {
  render: () => (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
        gap: '1.5rem',
        maxWidth: '500px',
      }}
    >
      <ScoreDisplay label="MEWS" score={1} trend="stable" />
      <ScoreDisplay label="MEWS" score={3} trend="increasing" />
      <ScoreDisplay label="MEWS" score={6} risk="high" trend="increasing" />
      <ScoreDisplay label="NEWS2" score={2} risk="low" trend="decreasing" />
      <ScoreDisplay label="NEWS2" score={5} risk="medium" trend="increasing" />
      <ScoreDisplay label="NEWS2" score={8} risk="high" trend="increasing" />
    </div>
  ),
};

// Re-export the sub-component metas so they're registered
export { TrendBadgeMeta, ScoreDisplayMeta };
