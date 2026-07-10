import type { Meta, StoryObj } from '@storybook/react';
import type { VitalRecord } from '@/lib/api';
import { VitalsPanel } from './vitals-panel';

const mockVitals: VitalRecord[] = [
  { name: 'HR', value: 112, unit: 'bpm', measured_at: '2026-07-09T12:00:00Z', severity: 'urgent' },
  { name: 'BP_SYS', value: 88, unit: 'mmHg', measured_at: '2026-07-09T12:00:00Z', severity: 'critical' },
  { name: 'BP_DIA', value: 56, unit: 'mmHg', measured_at: '2026-07-09T12:00:00Z', severity: 'critical' },
  { name: 'SpO2', value: 91, unit: '%', measured_at: '2026-07-09T12:00:00Z', severity: 'urgent' },
  { name: 'TEMP', value: 38.7, unit: '°C', measured_at: '2026-07-09T12:00:00Z', severity: 'watch' },
];

const meta: Meta<typeof VitalsPanel> = {
  title: 'Patient/VitalsPanel',
  component: VitalsPanel,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof VitalsPanel>;

export const Default: Story = {
  args: {
    vitals: mockVitals,
  },
};

export const Loading: Story = {
  args: {
    vitals: [],
    isLoading: true,
  },
};

export const ErrorState: Story = {
  args: {
    vitals: [],
    error: 'Falha ao conectar com o servidor',
  },
};

export const Empty: Story = {
  args: {
    vitals: [],
  },
};

export const NormalOnly: Story = {
  args: {
    vitals: [
      { name: 'HR', value: 72, unit: 'bpm', measured_at: '2026-07-09T12:00:00Z', severity: 'normal' },
      { name: 'SpO2', value: 98, unit: '%', measured_at: '2026-07-09T12:00:00Z', severity: 'normal' },
      { name: 'TEMP', value: 36.5, unit: '°C', measured_at: '2026-07-09T12:00:00Z', severity: 'normal' },
    ],
  },
};
