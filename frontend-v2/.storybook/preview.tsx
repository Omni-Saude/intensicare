import type { Preview } from '@storybook/react';
import '../app/globals.css'; // Import Tailwind + design tokens

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#0E1014' },
        { name: 'light', value: '#F5F6F8' },
      ],
    },
  },
  decorators: [
    (Story) => (
      <div data-theme="dark" style={{ padding: '2rem', minHeight: '100vh' }}>
        <Story />
      </div>
    ),
  ],
};

export default preview;
