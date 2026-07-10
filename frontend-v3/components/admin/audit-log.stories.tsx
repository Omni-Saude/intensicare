import type { Meta, StoryObj } from '@storybook/react';
import { AuditLog } from './audit-log';

const meta: Meta<typeof AuditLog> = {
  title: 'Admin/AuditLog',
  component: AuditLog,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof AuditLog>;

export const Default: Story = {};
