'use client';

import React, { useState } from 'react';
import {
  Bell,
  BellOff,
  Clock,
  Save,
  Shield,
  AlertTriangle,
  CheckCircle,
  Loader2,
  ArrowUpCircle,
} from 'lucide-react';
import Layout from '@/components/Layout';

// ─── Types ──────────────────────────────────────────────────────────────────

type SeverityBand = 'normal' | 'watch' | 'urgent' | 'critical';
type NotificationChannel = 'RRT' | 'SMS' | 'Push' | 'Badge';

interface RoutingRule {
  severity: SeverityBand;
  label: string;
  channel: NotificationChannel;
  escalationTimeoutMinutes: number;
  enabled: boolean;
}

const DEFAULT_RULES: RoutingRule[] = [
  {
    severity: 'normal',
    label: 'Normal',
    channel: 'Badge',
    escalationTimeoutMinutes: 60,
    enabled: true,
  },
  {
    severity: 'watch',
    label: 'Watch',
    channel: 'Push',
    escalationTimeoutMinutes: 30,
    enabled: true,
  },
  {
    severity: 'urgent',
    label: 'Urgent',
    channel: 'SMS',
    escalationTimeoutMinutes: 10,
    enabled: true,
  },
  {
    severity: 'critical',
    label: 'Critical',
    channel: 'RRT',
    escalationTimeoutMinutes: 3,
    enabled: true,
  },
];

const CHANNELS: NotificationChannel[] = ['RRT', 'SMS', 'Push', 'Badge'];
const TIMEOUTS = [1, 3, 5, 10, 15, 30, 60];

// ─── Severity helpers ───────────────────────────────────────────────────────

function getSeverityIcon(severity: SeverityBand) {
  switch (severity) {
    case 'critical':
      return <AlertTriangle className="w-4 h-4" />;
    case 'urgent':
      return <ArrowUpCircle className="w-4 h-4" />;
    case 'watch':
      return <Bell className="w-4 h-4" />;
    default:
      return <CheckCircle className="w-4 h-4" />;
  }
}

function getSeverityColour(severity: SeverityBand): string {
  switch (severity) {
    case 'critical':
      return 'var(--clinical-severity-critical-signal)';
    case 'urgent':
      return 'var(--clinical-severity-urgent-signal)';
    case 'watch':
      return 'var(--clinical-severity-watch-signal)';
    default:
      return 'var(--clinical-severity-normal-signal)';
  }
}

function getSeverityWash(severity: SeverityBand): string {
  switch (severity) {
    case 'critical':
      return 'var(--clinical-severity-critical-wash)';
    case 'urgent':
      return 'var(--clinical-severity-urgent-wash)';
    case 'watch':
      return 'var(--clinical-severity-watch-wash)';
    default:
      return 'var(--clinical-severity-normal-wash)';
  }
}

// ─── Page ───────────────────────────────────────────────────────────────────

export default function AlertRoutingPage() {
  const [rules, setRules] = useState<RoutingRule[]>(() =>
    DEFAULT_RULES.map((r) => ({ ...r })),
  );
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const toggleRule = (severity: SeverityBand) => {
    setRules((prev) =>
      prev.map((r) =>
        r.severity === severity ? { ...r, enabled: !r.enabled } : r,
      ),
    );
    setSaved(false);
    setSaveError(null);
  };

  const updateChannel = (severity: SeverityBand, channel: NotificationChannel) => {
    setRules((prev) =>
      prev.map((r) => (r.severity === severity ? { ...r, channel } : r)),
    );
    setSaved(false);
    setSaveError(null);
  };

  const updateTimeout = (severity: SeverityBand, minutes: number) => {
    setRules((prev) =>
      prev.map((r) =>
        r.severity === severity ? { ...r, escalationTimeoutMinutes: minutes } : r,
      ),
    );
    setSaved(false);
    setSaveError(null);
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveError(null);
    try {
      // Simulated API call — replace with real endpoint when available
      await new Promise((resolve) => setTimeout(resolve, 800));
      setSaved(true);
    } catch (err: unknown) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save routing rules');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1
            className="text-2xl font-bold"
            style={{ color: 'var(--semantic-text-primary)' }}
          >
            Alert Routing
          </h1>
          <p
            className="text-sm mt-1"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            Configure severity-driven notification routing rules
          </p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          aria-label="Save routing rules"
          className="flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all disabled:opacity-50"
          style={{
            backgroundColor: 'var(--clinical-severity-normal-fill)',
            color: 'var(--clinical-severity-normal-on-fill)',
            border: 'none',
          }}
        >
          {saving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          {saving ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>

      {/* Save feedback */}
      {saved && !saving && (
        <div
          className="flex items-center gap-2 px-4 py-3 rounded-lg mb-4"
          style={{
            backgroundColor: 'var(--clinical-severity-normal-wash)',
            borderColor: 'var(--clinical-severity-normal-signal)',
            border: '1px solid var(--clinical-severity-normal-signal)',
            color: 'var(--clinical-severity-normal-on-surface)',
          }}
          role="status"
          aria-live="polite"
        >
          <CheckCircle className="w-4 h-4" />
          Routing configuration saved successfully.
        </div>
      )}

      {saveError && (
        <div
          className="flex items-center gap-2 px-4 py-3 rounded-lg mb-4"
          style={{
            backgroundColor: 'var(--clinical-severity-critical-wash)',
            borderColor: 'var(--clinical-severity-critical-signal)',
            border: '1px solid var(--clinical-severity-critical-signal)',
            color: 'var(--clinical-severity-critical-on-surface)',
          }}
          role="alert"
          aria-live="assertive"
        >
          <AlertTriangle className="w-4 h-4" />
          {saveError}
        </div>
      )}

      {/* Rules Table */}
      <div
        className="rounded-xl border overflow-hidden"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        {/* Table header */}
        <div
          className="grid grid-cols-12 gap-4 px-6 py-3 text-xs font-semibold uppercase tracking-wider"
          style={{
            borderBottom: '1px solid var(--semantic-border-default)',
            color: 'var(--semantic-text-secondary)',
            backgroundColor: 'var(--semantic-surface-overlay)',
          }}
        >
          <div className="col-span-2" aria-label="Severity column">Severity</div>
          <div className="col-span-4" aria-label="Notification channel column">Channel</div>
          <div className="col-span-3" aria-label="Escalation timeout column">Escalation (min)</div>
          <div className="col-span-2" aria-label="Status column">Status</div>
          <div className="col-span-1" aria-label="Toggle column">Toggle</div>
        </div>

        {/* Table body */}
        {rules.map((rule) => (
          <div
            key={rule.severity}
            className="grid grid-cols-12 gap-4 px-6 py-4 items-center transition-colors"
            style={{
              borderBottom: '1px solid var(--semantic-border-default)',
              opacity: rule.enabled ? 1 : 0.55,
            }}
            aria-label={`Routing rule for ${rule.label} severity`}
          >
            {/* Severity */}
            <div className="col-span-2 flex items-center gap-2">
              <span style={{ color: getSeverityColour(rule.severity) }}>
                {getSeverityIcon(rule.severity)}
              </span>
              <span
                className="font-semibold text-sm"
                style={{
                  color: getSeverityColour(rule.severity),
                }}
              >
                {rule.label}
              </span>
            </div>

            {/* Channel selector */}
            <div className="col-span-4">
              <select
                value={rule.channel}
                onChange={(e) =>
                  updateChannel(rule.severity, e.target.value as NotificationChannel)
                }
                disabled={!rule.enabled}
                aria-label={`Notification channel for ${rule.label}`}
                className="w-full px-3 py-2 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                  backgroundColor: 'var(--semantic-surface-canvas)',
                }}
              >
                {CHANNELS.map((ch) => (
                  <option key={ch} value={ch}>
                    {ch === 'RRT'
                      ? '🚨 Rapid Response Team'
                      : ch === 'SMS'
                        ? '📱 SMS'
                        : ch === 'Push'
                          ? '🔔 Push Notification'
                          : '🏷️ Badge'}
                  </option>
                ))}
              </select>
            </div>

            {/* Escalation timeout */}
            <div className="col-span-3">
              <select
                value={rule.escalationTimeoutMinutes}
                onChange={(e) =>
                  updateTimeout(rule.severity, Number(e.target.value))
                }
                disabled={!rule.enabled}
                aria-label={`Escalation timeout for ${rule.label}`}
                className="w-full px-3 py-2 rounded-lg text-sm border outline-none transition-all focus:ring-2 focus:ring-blue-500"
                style={{
                  borderColor: 'var(--semantic-border-default)',
                  color: 'var(--semantic-text-primary)',
                  backgroundColor: 'var(--semantic-surface-canvas)',
                }}
              >
                {TIMEOUTS.map((t) => (
                  <option key={t} value={t}>
                    {t} {t === 1 ? 'minute' : 'minutes'}
                  </option>
                ))}
              </select>
            </div>

            {/* Status indicator */}
            <div className="col-span-2 flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor: rule.enabled
                    ? getSeverityColour(rule.severity)
                    : 'var(--semantic-text-secondary)',
                }}
              />
              <span
                className="text-xs font-medium"
                style={{
                  color: rule.enabled
                    ? getSeverityColour(rule.severity)
                    : 'var(--semantic-text-secondary)',
                }}
              >
                {rule.enabled ? 'Active' : 'Disabled'}
              </span>
            </div>

            {/* Toggle */}
            <div className="col-span-1 flex justify-end">
              <button
                onClick={() => toggleRule(rule.severity)}
                aria-label={`${rule.enabled ? 'Disable' : 'Enable'} ${rule.label} routing`}
                className="p-2 rounded-lg transition-all border"
                style={{
                  borderColor: rule.enabled
                    ? getSeverityColour(rule.severity)
                    : 'var(--semantic-border-default)',
                  backgroundColor: rule.enabled
                    ? getSeverityWash(rule.severity)
                    : 'transparent',
                  color: rule.enabled
                    ? getSeverityColour(rule.severity)
                    : 'var(--semantic-text-secondary)',
                }}
              >
                {rule.enabled ? (
                  <Bell className="w-4 h-4" />
                ) : (
                  <BellOff className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Info card */}
      <div
        className="mt-6 p-4 rounded-xl border flex items-start gap-3"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-overlay)',
          color: 'var(--semantic-text-secondary)',
        }}
      >
        <Shield className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="text-sm">
          <p className="font-medium" style={{ color: 'var(--semantic-text-primary)' }}>
            Routing Logic
          </p>
          <p className="mt-1">
            Alerts are routed to the configured channel when the severity threshold is
            met. If not acknowledged within the escalation timeout, the alert is
            automatically escalated to the next severity level. Critical alerts always
            trigger the Rapid Response Team regardless of configuration.
          </p>
        </div>
      </div>
    </Layout>
  );
}
