import type { Meta, StoryObj } from '@storybook/react';
import { CriteriaValue } from './criteria-value';

const meta: Meta<typeof CriteriaValue> = {
  title: 'Pathway/CriteriaValue',
  component: CriteriaValue,
  tags: ['autodocs'],
  argTypes: {
    value: { control: 'text', description: 'Valor medido atual' },
    unit: { control: 'text', description: 'Unidade de medida' },
    threshold: { control: 'text', description: 'Limiar de alerta' },
    normalRange: { control: 'text', description: 'Faixa de referência normal' },
    className: { control: 'text', description: 'Classes CSS adicionais' },
  },
};

export default meta;
type Story = StoryObj<typeof CriteriaValue>;

export const WithValueAndUnit: Story = {
  args: { value: '3.2', unit: 'mmol/L' },
};

export const WithThreshold: Story = {
  args: { value: '85', unit: 'mmHg', threshold: '≥90 mmHg' },
};

export const WithNormalRange: Story = {
  args: { value: '72', unit: 'bpm', normalRange: '60–100' },
};

export const WithThresholdAndRange: Story = {
  args: { value: '3.2', unit: 'mmol/L', threshold: '≥2.0', normalRange: '0.5–1.6' },
};

export const NoValue: Story = {
  args: { value: null },
};

export const OnlyUnit: Story = {
  args: { value: null, unit: 'mmHg' },
};
