import type { Meta, StoryObj } from '@storybook/react';
import { FilterBar } from './filter-bar';
import type { AlertFilterValues } from './filter-bar';

const defaultFilters: AlertFilterValues = {
  severity: '',
  status: 'all',
  unit: '',
  pathway: '',
  period: 'all',
};

const activeFilters: AlertFilterValues = {
  severity: 'critical',
  status: 'pending',
  unit: 'UTI 1',
  pathway: 'Sepse',
  period: '24h',
};

const meta: Meta<typeof FilterBar> = {
  title: 'Alerts/FilterBar',
  component: FilterBar,
  tags: ['autodocs'],
  argTypes: {
    filters: { control: 'object', description: 'Valores atuais dos filtros (AlertFilterValues)' },
    onChange: { action: 'changed', description: 'Callback de mudança de filtro' },
  },
};

export default meta;
type Story = StoryObj<typeof FilterBar>;

export const Default: Story = {
  args: { filters: defaultFilters },
};

export const WithActiveFilters: Story = {
  args: { filters: activeFilters },
};

export const SeverityOnly: Story = {
  args: { filters: { ...defaultFilters, severity: 'urgent' } },
};

export const StatusOnly: Story = {
  args: { filters: { ...defaultFilters, status: 'acknowledged' } },
};

export const PeriodOnly: Story = {
  args: { filters: { ...defaultFilters, period: '1h' } },
};
