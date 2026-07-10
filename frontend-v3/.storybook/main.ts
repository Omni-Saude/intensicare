import type { StorybookConfig } from '@storybook/nextjs';

const config: StorybookConfig = {
  framework: {
    name: '@storybook/nextjs',
    options: {
      // Next.js 16 + app directory
      nextConfigPath: '../next.config.ts',
    },
  },
  stories: [
    '../stories/**/*.stories.@(ts|tsx)',
    '../components/**/*.stories.@(ts|tsx)',
  ],
  addons: [
    '@storybook/addon-a11y',
  ],
  staticDirs: ['../public'],
  typescript: {
    reactDocgen: 'react-docgen',
  },
};

export default config;
