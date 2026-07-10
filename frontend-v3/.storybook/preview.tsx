import type { Preview } from '@storybook/react';
import { AuthProvider } from '../lib/auth';
import '../app/globals.css';

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: 'dark',
      values: [
        { name: 'dark', value: '#0a0e14' },
        { name: 'light', value: '#ffffff' },
      ],
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    nextjs: {
      appDirectory: true,
    },
  },
  decorators: [(Story) => <AuthProvider><Story /></AuthProvider>],
  tags: ['autodocs'],
};

export default preview;
