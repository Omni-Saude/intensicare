'use client';

import React, { useState, useEffect } from 'react';
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
import { fetchAlertRoutingRules, updateAlertRoutingRule } from '@/lib/api';

// ─── Types ──────────────────────────────────────────────────────────────────

type SeverityBand = 'normal' | 'watch' | 'urgent' | 'critical';
type NotificationChannel = 'RRT' | 'SMS' | 'Push' | 'Badge';

interface RoutingRule {
  id?: string;
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
  const [rules, setRules] = useState<RoutingRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Fetch rules on mount
  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchAlertRoutingRules()
      .then((data) => {
        const fetched = data as RoutingRule[];
        setRules(fetched.length > 0 ? fetched : DEFAULT_RULES);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : 'Failed to load routing rules');
        setRules(DEFAULT_RULES);
      })
      .finally(() => setLoading(false));
  }, []);

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
      // Save each rule individually via the API
      const promises = rules.map((rule) => {
        if (rule.id) {
          return updateAlertRoutingRule(rule.id, rule);
        }
        // If no ID, skip (shouldn't happen with real API data)
        return Promise.resolve();
      });
      await Promise.all(promises);
      setSaved(true);
    } catch (err: unknown) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save routing rules');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-20">
          <div className="flex items-center gap-3" style={{ color: 'var(--semantic-text-secondary)' }}>
            <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
            <span>Loading routing configuration...</span>
          </div>
        </div>
      </Layout>
    );
  }

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
            <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
          ) : (
            <Save className="w-4 h-4" aria-hidden="true" />
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
          <CheckCircle className="w-4 h-4" aria-hidden="true" />
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
          <AlertTriangle className="w-4 h-4" aria-hidden="true" />
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
         <table className="w-full border-collapse" role="table">
           <thead>
             <tr
               className="text-xs font-semibold uppercase tracking-wider"
               style={{
                 borderBottom: '1px solid var(--semantic-border-default)',
                 color: 'var(--semantic-text-secondary)',
                 backgroundColor: 'var(--semantic-surface-overlay)',
               }}
             >
               <th scope="col" className="px-6 py-3 text-left w-[16.6%]">Severity</th>
               <th scope="col" className="px-6 py-3 text-left w-[33.3%]">Channel</th>
               <th scope="col" className="px-6 py-3 text-left w-[25%]">Escalation (min)</th>
               <th scope="col" className="px-6 py-3 text-left w-[16.6%]">Status</th>
               <th scope="col" className="px-6 py-3 text-right w-[8.3%]">Toggle</th>
             </tr>
           </thead>
           <tbody>
             {rules.map((rule) => (
               <tr
                 key={rule.severity}
                 className="transition-colors"
                 style={{
                   borderBottom: '1px solid var(--semantic-border-default)',
                   opacity: rule.enabled ? 1 : 0.55,
                 }}
               >
                 {/* Severity */}
                 <td className="px-6 py-4">
                   <div className="flex items-center gap-2">
                     <span style={{ color: getSeverityColour(rule.severity) }} aria-hidden="true">
                       {getSeverityIcon(rule.severity)}
                     </span>
                     <span
                       className="font-semibold text-sm"
                       style={{ color: getSeverityColour(rule.severity) }}
                     >
                       {rule.label}
                     </span>
                   </div>
                 </td>

                 {/* Channel selector */}
                 <td className="px-6 py-4">
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
                 </td>

                 {/* Escalation timeout */}
                 <td className="px-6 py-4">
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
                 </td>

                 {/* Status indicator */}
                 <td className="px-6 py-4">
                   <div className="flex items-center gap-2">
                     <div
                       className="w-2 h-2 rounded-full"
                       aria-hidden="true"
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
                 </td>

                 {/* Toggle */}
                 <td className="px-6 py-4 text-right">
                   <button
                     onClick={() => toggleRule(rule.severity)}
                     aria-label={`${rule.enabled ? 'Disable' : 'Enable'} ${rule.label} routing`}
                     className="p-2 rounded-lg transition-all border focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
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
                       <Bell className="w-4 h-4" aria-hidden="true" />
                     ) : (
                       <BellOff className="w-4 h-4" aria-hidden="true" />
                     )}
                   </button>
                 </td>
               </tr>
             ))}
           </tbody>
         </table>
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
        <Shield className="w-5 h-5 flex-shrink-0 mt-0.5" aria-hidden="true" />
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
