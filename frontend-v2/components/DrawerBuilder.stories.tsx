import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import DrawerBuilder from './DrawerBuilder';

const meta: Meta<typeof DrawerBuilder> = {
  title: 'Components/DrawerBuilder',
  component: DrawerBuilder,
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg', 'full'],
    },
  },
};

export default meta;
type Story = StoryObj<typeof DrawerBuilder>;

/** Helper wrapper so stories show the drawer already open */
function DrawerDemo({
  size = 'md',
  title,
  children,
}: {
  size?: 'sm' | 'md' | 'lg' | 'full';
  title?: string;
  children?: React.ReactNode;
}) {
  const [open, setOpen] = useState(true);
  return (
    <>
      <button
        onClick={() => setOpen(true)}
        style={{
          padding: '0.5rem 1rem',
          background: 'var(--action-primary-bg-dark, #2563eb)',
          color: '#fff',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
        }}
      >
        Open Drawer
      </button>
      <DrawerBuilder open={open} onClose={() => setOpen(false)} title={title} size={size}>
        {children || (
          <div style={{ color: 'var(--semantic-text-secondary, #A6ADBB)' }}>
            <p>This is the drawer content. You can put any components here.</p>
            <p style={{ marginTop: '0.5rem' }}>
              The drawer uses Radix Dialog under the hood with a backdrop overlay.
            </p>
          </div>
        )}
      </DrawerBuilder>
    </>
  );
}

export const Default: Story = {
  render: () => <DrawerDemo />,
};

export const Small: Story = {
  render: () => <DrawerDemo size="sm" title="Confirmation" />,
};

export const Medium: Story = {
  render: () => <DrawerDemo size="md" title="Alert Details" />,
};

export const Large: Story = {
  render: () => (
    <DrawerDemo size="lg" title="Patient Summary">
      <div style={{ color: 'var(--semantic-text-secondary, #A6ADBB)', lineHeight: 1.6 }}>
        <p>
          Large drawer — ideal for forms, detailed patient info, or multi-section content.
        </p>
        <p style={{ marginTop: '0.5rem' }}>
          This drawer has a <code>max-w-lg</code> width constraint and is centered on screen.
        </p>
      </div>
    </DrawerDemo>
  ),
};

export const FullScreen: Story = {
  render: () => (
    <DrawerDemo size="full">
      <div
        style={{
          color: 'var(--semantic-text-secondary, #A6ADBB)',
          minHeight: '60vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <h2
          style={{
            fontSize: '1.5rem',
            fontWeight: 700,
            color: 'var(--semantic-text-primary, #E9ECF1)',
            marginBottom: '0.5rem',
          }}
        >
          Full-Screen Drawer
        </h2>
        <p>Covers the entire viewport — useful for mobile navigation and immersive UIs.</p>
      </div>
    </DrawerDemo>
  ),
};

export const WithoutTitle: Story = {
  render: () => (
    <DrawerDemo size="sm">
      <p style={{ color: 'var(--semantic-text-secondary, #A6ADBB)' }}>
        This drawer has no title — just content and a close button.
      </p>
    </DrawerDemo>
  ),
};

function ClosedDemo() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        onClick={() => setOpen(true)}
        style={{
          padding: '0.5rem 1rem',
          background: 'var(--action-primary-bg-dark, #2563eb)',
          color: '#fff',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
        }}
      >
        Open Drawer
      </button>
      <DrawerBuilder open={open} onClose={() => setOpen(false)} title="Closed by default">
        <p style={{ color: 'var(--semantic-text-secondary, #A6ADBB)' }}>
          Open me with the button above.
        </p>
      </DrawerBuilder>
    </>
  );
}

export const Closed: Story = {
  render: () => <ClosedDemo />,
};
