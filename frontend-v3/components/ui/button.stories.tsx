import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './button';

const meta: Meta<typeof Button> = {
  title: 'UI/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'secondary', 'outline', 'ghost', 'destructive', 'link'],
      description: 'Estilo visual do botão',
    },
    size: {
      control: 'select',
      options: ['default', 'xs', 'sm', 'lg', 'icon', 'icon-xs', 'icon-sm', 'icon-lg'],
      description: 'Tamanho do botão',
    },
    disabled: {
      control: 'boolean',
      description: 'Desabilita o botão',
    },
    children: {
      control: 'text',
      description: 'Conteúdo do botão',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    variant: 'default',
    children: 'Primary',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Secondary',
  },
};

export const Outline: Story = {
  args: {
    variant: 'outline',
    children: 'Outline',
  },
};

export const Disabled: Story = {
  args: {
    variant: 'default',
    children: 'Disabled',
    disabled: true,
  },
};

export const Loading: Story = {
  args: {
    variant: 'default',
    children: 'Carregando...',
    disabled: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Estado de loading: botão desabilitado com texto indicando carregamento. Em produção, combine com um ícone de spinner.',
      },
    },
  },
};
