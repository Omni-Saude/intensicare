import type { Meta, StoryObj } from '@storybook/react';
import { UnitFilter } from './unit-filter';

const meta: Meta<typeof UnitFilter> = {
  title: 'Dashboard/UnitFilter',
  component: UnitFilter,
  tags: ['autodocs'],
  argTypes: {
    onChange: { action: 'changed', description: 'Callback quando uma unidade é selecionada' },
  },
};

export default meta;
type Story = StoryObj<typeof UnitFilter>;

export const Default: Story = {
  args: {
    units: ['UTI Adulto', 'UTI Pediátrica', 'Enfermaria', 'Pronto-Socorro'],
    selected: null,
    onChange: (unit: string | null) => console.log('Filter:', unit),
  },
};

export const WithSelection: Story = {
  args: {
    units: ['UTI Adulto', 'UTI Pediátrica', 'Enfermaria', 'Pronto-Socorro'],
    selected: 'UTI Adulto',
    onChange: (unit: string | null) => console.log('Filter:', unit),
  },
};

export const SingleUnit: Story = {
  args: {
    units: ['UTI Adulto'],
    selected: null,
    onChange: (unit: string | null) => console.log('Filter:', unit),
  },
};

export const EmptyUnits: Story = {
  args: {
    units: [],
    selected: null,
    onChange: (unit: string | null) => console.log('Filter:', unit),
  },
};
