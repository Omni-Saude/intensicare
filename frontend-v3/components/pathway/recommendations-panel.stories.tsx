import type { Meta, StoryObj } from '@storybook/react';
import { RecommendationsPanel } from './recommendations-panel';

const mockRecommendations = [
  'Iniciar antibioticoterapia empírica de amplo espectro em até 1 hora.',
  'Coletar hemoculturas (2 pares) antes do início do antibiótico.',
  'Iniciar ressuscitação volêmica com cristaloide 30 mL/kg nas primeiras 3 horas.',
  'Monitorar lactato sérico a cada 2–4 horas até normalização.',
  'Avaliar necessidade de vasopressor se PAM < 65 mmHg após volume.',
];

const meta: Meta<typeof RecommendationsPanel> = {
  title: 'Pathway/RecommendationsPanel',
  component: RecommendationsPanel,
  tags: ['autodocs'],
  argTypes: {
    recommendations: { control: 'object', description: 'Lista de recomendações clínicas' },
    isLoading: { control: 'boolean', description: 'Estado de carregamento' },
  },
};

export default meta;
type Story = StoryObj<typeof RecommendationsPanel>;

export const Default: Story = {
  args: { recommendations: mockRecommendations },
};

export const SingleRecommendation: Story = {
  args: { recommendations: [mockRecommendations[0]] },
};

export const Loading: Story = {
  args: { recommendations: undefined, isLoading: true },
};

export const Empty: Story = {
  args: { recommendations: [] },
};
