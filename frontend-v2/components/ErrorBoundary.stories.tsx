import type { Meta, StoryObj } from '@storybook/react';
import ErrorBoundary from './ErrorBoundary';

const meta: Meta<typeof ErrorBoundary> = {
  title: 'Components/ErrorBoundary',
  component: ErrorBoundary,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ErrorBoundary>;

/** A component that deliberately throws an error for demonstration */
function BrokenComponent({ message }: { message?: string }): React.ReactNode {
  throw new Error(message || 'Simulated render error in child component');
}

function HealthyComponent() {
  return (
    <div
      style={{
        padding: '1rem',
        background: 'var(--clinical-severity-normal-wash, #1D8844)',
        color: 'var(--clinical-severity-normal-on-surface, #2DD269)',
        borderRadius: '8px',
        border: '1px solid var(--clinical-severity-normal-signal, #2DD269)',
      }}
    >
      ✅ Everything rendered successfully.
    </div>
  );
}

function CustomFallback() {
  return (
    <div
      style={{
        padding: '1rem',
        background: 'var(--feedback-warning-bg-dark, #3b2f00)',
        color: 'var(--feedback-warning-text-dark, #facc15)',
        borderRadius: '8px',
        border: '1px solid var(--feedback-warning-border-dark, #5c4a00)',
      }}
    >
      ⚠️ Custom fallback: The child component could not be rendered.
    </div>
  );
}

export const Normal: Story = {
  render: () => (
    <ErrorBoundary>
      <HealthyComponent />
    </ErrorBoundary>
  ),
};

export const WithError: Story = {
  render: () => (
    <ErrorBoundary>
      <BrokenComponent message="Failed to load patient vitals — data integrity check failed" />
    </ErrorBoundary>
  ),
};

export const WithErrorShortMessage: Story = {
  render: () => (
    <ErrorBoundary>
      <BrokenComponent message="Network error" />
    </ErrorBoundary>
  ),
};

export const WithCustomFallback: Story = {
  render: () => (
    <ErrorBoundary fallback={<CustomFallback />}>
      <BrokenComponent message="This error is caught by the custom fallback" />
    </ErrorBoundary>
  ),
};
