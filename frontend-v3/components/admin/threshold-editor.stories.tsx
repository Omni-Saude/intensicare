import type { Meta, StoryObj } from '@storybook/react';
import { ThresholdEditor } from './threshold-editor';

const meta: Meta<typeof ThresholdEditor> = {
  title: 'Admin/ThresholdEditor',
  component: ThresholdEditor,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ThresholdEditor>;

export const Default: Story = {};
