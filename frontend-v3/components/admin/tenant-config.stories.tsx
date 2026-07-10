import type { Meta, StoryObj } from '@storybook/react';
import { TenantConfig } from './tenant-config';

const meta: Meta<typeof TenantConfig> = {
  title: 'Admin/TenantConfig',
  component: TenantConfig,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof TenantConfig>;

export const Default: Story = {};
