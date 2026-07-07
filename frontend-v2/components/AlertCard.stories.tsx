import type { Meta, StoryObj } from '@storybook/react';
import AlertCard from './AlertCard';
import type { AlertInfo, TriggeringParameter } from '@/lib/api';

// ─── Mock Data Factories ──────────────────────────────────────────────────────

function makeAlert(overrides: Partial<AlertInfo> = {}): AlertInfo {
  return {
    id: 1042,
    mpi_id: 'PAT-0042',
    score_id: null,
    severity: 'urgent',
    status: 'active',
    title: 'MEWS Elevado Detectado',
    body:
      'O escore MEWS do paciente subiu para 5 nos últimos 30 minutos. ' +
      'Parâmetros de frequência cardíaca e respiratória ultrapassaram os limiares configurados.',
    created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    acknowledged_at: null,
    acknowledged_by: null,
    resolved_at: null,
    resolution: null,
    ...overrides,
  };
}

function makeTriggeringParams(): TriggeringParameter[] {
  return [
    { name: 'Frequência Cardíaca', value: 118, threshold: 100, unit: 'bpm', breached: true },
    { name: 'Frequência Respiratória', value: 26, threshold: 20, unit: 'rpm', breached: true },
    { name: 'SpO₂', value: 93, threshold: 92, unit: '%', breached: false },
    { name: 'Temperatura', value: 37.8, threshold: 38.0, unit: '°C', breached: false },
    { name: 'Pressão Sistólica', value: 105, threshold: 90, unit: 'mmHg', breached: false },
  ];
}

// ─── Meta ─────────────────────────────────────────────────────────────────────

const meta: Meta<typeof AlertCard> = {
  title: 'Components/AlertCard',
  component: AlertCard,
  tags: ['autodocs'],
  argTypes: {
    onUpdate: { action: 'updated' },
  },
};

export default meta;
type Story = StoryObj<typeof AlertCard>;

const noop = () => {};

// ─── Stories by Status ────────────────────────────────────────────────────────

export const Active: Story = {
  args: {
    alert: makeAlert({ status: 'active', severity: 'urgent' }),
    onUpdate: noop,
  },
};

export const ActiveCritical: Story = {
  args: {
    alert: makeAlert({
      status: 'active',
      severity: 'critical',
      title: 'PCR Iminente — MEWS Crítico',
      body: 'Paciente apresenta MEWS 7 com taquicardia ventricular. Risco elevado de parada cardiorrespiratória.',
    }),
    onUpdate: noop,
  },
};

export const ActiveWatch: Story = {
  args: {
    alert: makeAlert({
      status: 'active',
      severity: 'watch',
      title: 'Tendência de Piora — MEWS 3',
      body: 'MEWS subiu de 1 para 3. Monitorar evolução nas próximas 2 horas.',
    }),
    onUpdate: noop,
  },
};

export const Acknowledged: Story = {
  args: {
    alert: makeAlert({
      status: 'acknowledged',
      severity: 'urgent',
      acknowledged_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      acknowledged_by: 'Dr. Silva',
    }),
    onUpdate: noop,
  },
};

export const Escalated: Story = {
  args: {
    alert: makeAlert({
      status: 'escalated',
      severity: 'critical',
      title: 'Escalado para UTI — Insuficiência Respiratória Aguda',
      acknowledged_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      acknowledged_by: 'Dr. Santos',
    }),
    onUpdate: noop,
  },
};

export const Resolved: Story = {
  args: {
    alert: makeAlert({
      status: 'resolved',
      severity: 'watch',
      title: 'MEWS Normalizado',
      body: 'Parâmetros voltaram ao normal após intervenção.',
      acknowledged_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
      acknowledged_by: 'Dr. Silva',
      resolved_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      resolution: 'intervention_done',
    }),
    onUpdate: noop,
  },
};

// ─── Why-Panel Variants ───────────────────────────────────────────────────────

export const WithWhyPanelClosed: Story = {
  args: {
    alert: makeAlert({
      triggering_parameters: makeTriggeringParams(),
      rule_reference: 'MEWS ≥ 5 com dois parâmetros violados → Alerta Urgente (NEWS2/MEWS Protocol v2.1)',
      alert_definition_version: 'v2.1.0',
      data_coverage_note: 'Dados de FC cobrem 98% das últimas 6h. Janela de 5min sem leitura às 14:32.',
    }),
    onUpdate: noop,
  },
};

export const WithWhyPanelTriggeringOnly: Story = {
  args: {
    alert: makeAlert({
      triggering_parameters: [
        { name: 'Frequência Cardíaca', value: 135, threshold: 100, unit: 'bpm', breached: true },
      ],
    }),
    onUpdate: noop,
  },
};

// ─── Edge Cases ───────────────────────────────────────────────────────────────

export const NoBody: Story = {
  args: {
    alert: makeAlert({
      body: null,
      title: 'Alerta sem corpo descritivo',
    }),
    onUpdate: noop,
  },
};

export const NoPatientId: Story = {
  args: {
    alert: makeAlert({
      mpi_id: '',
    }),
    onUpdate: noop,
  },
};

export const FullDetail: Story = {
  args: {
    alert: makeAlert({
      status: 'active',
      severity: 'critical',
      title: 'Alerta Completo — Todos os Campos',
      body: 'Este alerta contém todos os campos de metadados disponíveis para inspeção visual.',
      triggering_parameters: makeTriggeringParams(),
      rule_reference: 'Protocolo de Sepse — qSOFA ≥ 2 com lactato > 2 mmol/L',
      alert_definition_version: 'v3.0.0-rc1',
      data_coverage_note:
        'Cobertura total de 99.7% nas últimas 24h. Dados de lactato disponíveis a cada 6h.',
    }),
    onUpdate: noop,
  },
};
