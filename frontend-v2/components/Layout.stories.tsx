import type { Meta, StoryObj } from '@storybook/react';
import Layout, { FullScreenLayout } from './Layout';
import { setUser } from '@/lib/auth';

// Set up a mock user in the in-memory store so getUser() works
function setupMockUser(isAdmin = false) {
  const user = {
    id: 1,
    username: 'dr.silva',
    email: 'dr.silva@hospital.com',
    display_name: 'Dr. Silva',
    is_admin: isAdmin,
    is_active: true,
    role: null,
  };
  setUser(user);
}

const meta: Meta<typeof Layout> = {
  title: 'Components/Layout',
  component: Layout,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
  decorators: [
    (Story) => {
      setupMockUser();
      return <Story />;
    },
  ],
};

export default meta;
type Story = StoryObj<typeof Layout>;

const SampleContent = () => (
  <div style={{ color: 'var(--semantic-text-primary, #E9ECF1)' }}>
    <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.75rem' }}>
      Painel
    </h2>
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1rem',
      }}
    >
      {[
        { label: 'Pacientes Ativos', value: '12' },
        { label: 'Alertas Ativos', value: '3' },
        { label: 'Leitos Disponíveis', value: '4' },
        { label: 'Equipe de Plantão', value: '8' },
      ].map((stat) => (
        <div
          key={stat.label}
          style={{
            padding: '1rem',
            background: 'var(--semantic-surface-raised, #171A21)',
            borderRadius: '12px',
            border: '1px solid var(--semantic-border-default, rgba(255,255,255,0.08))',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: 'var(--semantic-text-secondary, #A6ADBB)',
              marginBottom: '0.25rem',
            }}
          >
            {stat.label}
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{stat.value}</div>
        </div>
      ))}
    </div>
  </div>
);

export const Default: Story = {
  render: () => (
    <Layout>
      <SampleContent />
    </Layout>
  ),
};

export const AdminUser: Story = {
  decorators: [
    (Story) => {
      setupMockUser(true);
      return <Story />;
    },
  ],
  render: () => (
    <Layout>
      <SampleContent />
    </Layout>
  ),
};

export const Mobile: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
  },
  render: () => (
    <Layout>
      <SampleContent />
    </Layout>
  ),
};

export const FullScreenLayoutDefault: Story = {
  render: () => (
    <FullScreenLayout>
      <SampleContent />
    </FullScreenLayout>
  ),
};

export const FullScreenLayoutMobile: Story = {
  parameters: {
    viewport: {
      defaultViewport: 'mobile1',
    },
  },
  render: () => (
    <FullScreenLayout>
      <SampleContent />
    </FullScreenLayout>
  ),
};

export const LoginPageBypass: Story = {
  parameters: {
    nextjs: {
      navigation: {
        pathname: '/login',
      },
    },
  },
  render: () => (
    <Layout>
      <div style={{ color: 'var(--semantic-text-primary, #E9ECF1)' }}>
        This content should render without sidebar (login page bypass).
      </div>
    </Layout>
  ),
};
