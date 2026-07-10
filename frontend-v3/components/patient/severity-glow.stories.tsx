import type { Meta, StoryObj } from '@storybook/react';
import { severityGlow, severityBorder, severityColor } from './severity-glow';

// severity-glow exports utility functions, not a React component
// We provide a demo component to visualize the outputs
function SeverityGlowDemo() {
  const levels = ['normal', 'watch', 'urgent', 'critical'] as const;

  return (
    <div className="flex flex-wrap gap-6 p-8" style={{ backgroundColor: 'var(--surface-base, #0a0e14)' }}>
      {levels.map((sev) => (
        <div
          key={sev}
          className="flex flex-col items-center gap-3 p-5 rounded-lg"
          style={{
            backgroundColor: 'var(--surface-raised)',
            borderColor: `${severityColor(sev)}66`,
            borderWidth: '1px',
            borderLeftWidth: '4px',
            borderLeftColor: severityColor(sev),
            boxShadow: severityGlow(sev) || undefined,
          }}
        >
          <div
            className="size-4 rounded-full"
            style={{ backgroundColor: severityColor(sev) }}
          />
          <span
            className="text-xs font-semibold uppercase"
            style={{ color: severityColor(sev) }}
          >
            {sev}
          </span>
          <div className="flex flex-col gap-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
            <code className="text-[10px]" style={{ color: severityColor(sev) }}>
              Color: {severityColor(sev)}
            </code>
            <code className="text-[10px]" style={{ opacity: 0.6 }}>
              Glow: {severityGlow(sev) || '(none)'}
            </code>
            <code className="text-[10px]" style={{ opacity: 0.6 }}>
              Border: {severityBorder(sev)}
            </code>
          </div>
        </div>
      ))}
    </div>
  );
}

const meta: Meta<typeof SeverityGlowDemo> = {
  title: 'Patient/SeverityGlow',
  component: SeverityGlowDemo,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof SeverityGlowDemo>;

export const Demo: Story = {};
