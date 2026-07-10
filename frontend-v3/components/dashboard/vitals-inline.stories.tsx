import type { Meta, StoryObj } from '@storybook/react';
import { VitalsInline } from './vitals-inline';

const meta: Meta<typeof VitalsInline> = {
  title: 'Dashboard/VitalsInline',
  component: VitalsInline,
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof VitalsInline>;

export const FullVitals: Story = {
  args: {
    vitals: {
      hr: 112,
      spo2: 91,
      bp_sys: 88,
      bp_dia: 56,
    },
  },
};

export const OnlyHeartRate: Story = {
  args: {
    vitals: {
      hr: 82,
    },
  },
};

export const OnlySpo2: Story = {
  args: {
    vitals: {
      spo2: 98,
    },
  },
};

export const OnlyBloodPressure: Story = {
  args: {
    vitals: {
      bp_sys: 120,
      bp_dia: 80,
    },
  },
};

export const SystolicOnly: Story = {
  args: {
    vitals: {
      bp_sys: 135,
    },
  },
};

export const Undefined: Story = {
  args: {
    vitals: undefined,
  },
};
