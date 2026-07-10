import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';
import { AppShell } from './app-shell';
import { setToken } from '@/lib/api';

// ── Fake JWT builder ──
// AuthProvider decodes the token payload on mount to extract user info.
// We inject a mock token before render so AuthProvider treats the session as authenticated.

function createFakeJwt(payload: object): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const body = btoa(JSON.stringify(payload));
  return `${header}.${body}.fake-signature`;
}

const mockJwt = createFakeJwt({
  sub: 'mock-id',
  name: 'Dr. Carlos Mendes',
  email: 'carlos.mendes@hospital.com',
  role: 'Médico Intensivista',
  is_admin: true,
});

const meta: Meta<typeof AppShell> = {
  title: 'Layout/AppShell',
  component: AppShell,
  tags: ['autodocs'],
  argTypes: {
    children: {
      control: 'text',
      description: 'Conteúdo da página renderizado dentro do shell',
    },
  },
};

export default meta;
type Story = StoryObj<typeof AppShell>;

export const Authenticated: Story = {
  decorators: [
    (Story) => {
      // Inject mock token so AuthProvider (from global preview decorator)
      // finds it on mount and sets isAuthenticated=true with the mock user.
      setToken(mockJwt);
      return <Story />;
    },
  ],
  args: {
    children: (
      <div style={{ padding: '2rem' }}>
        <h2
          style={{
            fontSize: '1.25rem',
            fontWeight: 600,
            marginBottom: '0.5rem',
            color: 'var(--text-primary)',
          }}
        >
          Conteúdo da Página
        </h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Esta é a área de conteúdo principal do AppShell. O sidebar à esquerda
          contém a navegação e as informações do usuário autenticado.
        </p>
      </div>
    ),
  },
};

export const Unauthenticated: Story = {
  args: {
    children: (
      <div style={{ padding: '2rem' }}>
        <h2
          style={{
            fontSize: '1.25rem',
            fontWeight: 600,
            marginBottom: '0.5rem',
            color: 'var(--text-primary)',
          }}
        >
          Dashboard
        </h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Modo sem usuário autenticado — a seção de usuário no rodapé do
          sidebar não é exibida. O indicador de conexão mostra desconectado.
        </p>
      </div>
    ),
  },
  parameters: {
    docs: {
      description: {
        story:
          'AppShell sem usuário autenticado. A seção de usuário no rodapé do sidebar fica oculta. ' +
          'Este é o estado inicial quando o AuthProvider não encontra um token JWT válido.',
      },
    },
  },
};
