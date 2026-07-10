import type { Meta, StoryObj } from '@storybook/react';
import { PathwayGrid } from './pathway-grid';

const meta: Meta<typeof PathwayGrid> = {
  title: 'Pathways/PathwayGrid',
  component: PathwayGrid,
  tags: ['autodocs'],
  parameters: {
    nextjs: {
      appDirectory: true,
    },
  },
};

export default meta;
type Story = StoryObj<typeof PathwayGrid>;

/** Renderiza o grid com dados do backend. Mostra loading state enquanto carrega. */
export const Default: Story = {
  render: () => <PathwayGrid />,
};
