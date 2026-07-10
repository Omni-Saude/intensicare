import type { Meta, StoryObj } from '@storybook/react';
import { SWRConfig } from 'swr';
import { UserManager } from './user-manager';
import type { UserInfo } from '@/lib/api';

const mockUsers: UserInfo[] = [
  {
    id: 'user-001',
    name: 'Dr. Carlos Mendes',
    email: 'carlos.mendes@hospital.com',
    role: 'Médico Intensivista',
    is_admin: true,
  },
  {
    id: 'user-002',
    name: 'Enf. Ana Oliveira',
    email: 'ana.oliveira@hospital.com',
    role: 'Enfermeira',
    is_admin: false,
  },
  {
    id: 'user-003',
    name: 'Dra. Paula Ribeiro',
    email: 'paula.ribeiro@hospital.com',
    role: 'Médica Plantonista',
    is_admin: true,
  },
];

const meta: Meta<typeof UserManager> = {
  title: 'Admin/UserManager',
  component: UserManager,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof UserManager>;

export const Default: Story = {
  decorators: [
    (Story) => (
      <SWRConfig
        value={{
          fallback: {
            'admin-users': { items: mockUsers, total: mockUsers.length },
          },
        }}
      >
        <Story />
      </SWRConfig>
    ),
  ],
};

export const Empty: Story = {
  decorators: [
    (Story) => (
      <SWRConfig
        value={{
          fallback: {
            'admin-users': { items: [], total: 0 },
          },
        }}
      >
        <Story />
      </SWRConfig>
    ),
  ],
};
