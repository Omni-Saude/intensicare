'use client';

import React, { useState } from 'react';
import { CheckCircle, XCircle, ArrowUpCircle, Clock, AlertTriangle, ChevronDown, ChevronUp, Info } from 'lucide-react';
import SeverityBadge from './SeverityBadge';
import type { AlertInfo, TriggeringParameter } from '@/lib/api';
import { acknowledgeAlert, resolveAlert, escalateAlert } from '@/lib/api';

interface AlertCardProps {
  alert: AlertInfo;
  onUpdate: () => void;
}

// Status badge colors — using CSS custom properties (design-tokens.md §6)
const statusBadge: Record<
  string,
  { bgVar: string; textVar: string; label: string }
> = {
  active: {
    bgVar: 'var(--clinical-severity-critical-wash)',
    textVar: 'var(--clinical-severity-critical-on-surface)',
    label: 'Active',
  },
  acknowledged: {
    bgVar: 'var(--clinical-status-attended-color)',
    textVar: 'var(--clinical-status-attended-on-color)',
    label: 'Acknowledged',
  },
  escalated: {
    bgVar: 'var(--clinical-severity-urgent-wash)',
    textVar: 'var(--clinical-severity-urgent-on-surface)',
    label: 'Escalated',
  },
  resolved: {
    bgVar: 'var(--clinical-severity-normal-wash)',
    textVar: 'var(--clinical-severity-normal-on-surface)',
    label: 'Resolved',
  },
};

export default function AlertCard({ alert, onUpdate }: AlertCardProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [whyPanelOpen, setWhyPanelOpen] = useState(false);

  const handleAcknowledge = async () => {
    setLoading('ack');
    setError(null);
    try {
      await acknowledgeAlert(alert.id);
      onUpdate();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to acknowledge');
    } finally {
      setLoading(null);
    }
  };

  const handleResolve = async (
    resolution: 'true_positive' | 'false_positive' | 'intervention_done',
  ) => {
    setLoading(`resolve-${resolution}`);
    setError(null);
    try {
      await resolveAlert(alert.id, resolution);
      onUpdate();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to resolve');
    } finally {
      setLoading(null);
    }
  };

  const handleEscalate = async () => {
    setLoading('escalate');
    setError(null);
    try {
      await escalateAlert(alert.id);
      onUpdate();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to escalate');
    } finally {
      setLoading(null);
    }
  };

  const statusKey = (alert.status && alert.status in statusBadge) ? alert.status : 'active';
  const status = statusBadge[statusKey]!;
  const isActionable = alert.status === 'active' || alert.status === 'escalated';
  const isAcknowledgeable =
    alert.status === 'active' || alert.status === 'escalated';
  const isResolvable =
    alert.status === 'acknowledged' || alert.status === 'acting';
  const isEscalatable =
    alert.status === 'active' || alert.status === 'acknowledged';
  const isCritical = alert.severity === 'critical';

  const hasWhyPanel =
    alert.triggering_parameters ||
    alert.rule_reference ||
    alert.alert_definition_version ||
    alert.data_coverage_note;

  const formatDate = (iso: string | null) => {
    if (!iso) return null;
    return new Date(iso).toLocaleString();
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 min-w-0">
            <SeverityBadge
              severity={
                alert.severity as 'normal' | 'watch' | 'urgent' | 'critical'
              }
            />
            <span
              className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
              style={{
                backgroundColor: status.bgVar,
                color: status.textVar,
              }}
            >
              {status.label}
            </span>
          </div>
          <div
            className="text-xs whitespace-nowrap"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            #{alert.id} · {formatDate(alert.created_at)}
          </div>
        </div>

        {/* Title & Body */}
        <h4
          className="font-semibold mb-1"
          style={{ color: 'var(--semantic-text-primary)' }}
        >
          {alert.title}
        </h4>
        {alert.body && (
          <p
            className="text-sm mb-3 line-clamp-2"
            style={{ color: 'var(--semantic-text-secondary)' }}
          >
            {alert.body}
          </p>
        )}

        {/* Meta */}
        <div
          className="flex flex-wrap gap-3 text-xs mb-3"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {alert.mpi_id && <span>Patient: {alert.mpi_id}</span>}
          {alert.acknowledged_at && (
            <span className="flex items-center gap-1">
              <CheckCircle className="w-3 h-3" />
              Ack: {formatDate(alert.acknowledged_at)}
              {alert.acknowledged_by && ` by ${alert.acknowledged_by}`}
            </span>
          )}
          {alert.resolved_at && (
            <span className="flex items-center gap-1">
              <CheckCircle
                className="w-3 h-3"
                style={{ color: 'var(--clinical-severity-normal-signal)' }}
              />
              Resolved: {formatDate(alert.resolved_at)}
              {alert.resolution &&
                ` (${alert.resolution.replace(/_/g, ' ')})`}
            </span>
          )}
        </div>

        {/* Error — uses critical severity tokens, role="alert" */}
        {error && (
          <div
            className="flex items-center gap-1 text-xs px-2 py-1 rounded mb-3"
            style={{
              color: 'var(--clinical-severity-critical-on-surface)',
              backgroundColor: 'var(--clinical-severity-critical-wash)',
            }}
            role="alert"
            aria-live="assertive"
          >
            <AlertTriangle className="w-3 h-3" />
            {error}
          </div>
        )}

        {/* Actions — all buttons get proper aria-labels */}
        <div className="flex flex-wrap gap-2">
          {isAcknowledgeable && (
            <button
              onClick={handleAcknowledge}
              disabled={loading !== null}
              aria-label={`Acknowledge alert: ${alert.title}`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-white text-xs font-medium rounded-lg disabled:opacity-50 transition-colors"
              style={{
                backgroundColor: 'var(--clinical-status-attended-color)',
              }}
            >
              <Clock className="w-3.5 h-3.5" />
              {loading === 'ack' ? '...' : 'Acknowledge'}
            </button>
          )}

          {isEscalatable && (
            <button
              onClick={handleEscalate}
              disabled={loading !== null}
              aria-label={`Escalate alert: ${alert.title}`}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-white text-xs font-medium rounded-lg disabled:opacity-50 transition-colors"
              style={{
                backgroundColor: 'var(--clinical-severity-urgent-fill)',
              }}
            >
              <ArrowUpCircle className="w-3.5 h-3.5" />
              {loading === 'escalate' ? '...' : 'Escalate'}
            </button>
          )}

          {isResolvable && (
            <>
              <button
                onClick={() => handleResolve('true_positive')}
                disabled={loading !== null}
                aria-label="Resolve as true positive"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-white text-xs font-medium rounded-lg disabled:opacity-50 transition-colors"
                style={{
                  backgroundColor: 'var(--clinical-severity-normal-fill)',
                }}
              >
                <CheckCircle className="w-3.5 h-3.5" />
                {loading === 'resolve-true_positive' ? '...' : 'True Positive'}
              </button>
              <button
                onClick={() => handleResolve('false_positive')}
                disabled={loading !== null}
                aria-label="Resolve as false positive"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-white text-xs font-medium rounded-lg disabled:opacity-50 transition-colors"
                style={{ backgroundColor: 'var(--semantic-text-secondary)' }}
              >
                <XCircle className="w-3.5 h-3.5" />
                {loading === 'resolve-false_positive'
                  ? '...'
                  : 'False Positive'}
              </button>
              <button
                onClick={() => handleResolve('intervention_done')}
                disabled={loading !== null}
                aria-label="Resolve as intervention done"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-white text-xs font-medium rounded-lg disabled:opacity-50 transition-colors"
                style={{
                  backgroundColor: 'var(--clinical-severity-watch-fill)',
                }}
              >
                <CheckCircle className="w-3.5 h-3.5" />
                {loading === 'resolve-intervention_done'
                  ? '...'
                  : 'Intervention Done'}
              </button>
            </>
          )}

          {/* Why-panel toggle button */}
          {hasWhyPanel && (
            <button
              onClick={() => setWhyPanelOpen(!whyPanelOpen)}
              aria-label={whyPanelOpen ? 'Hide alert details' : 'Show alert details'}
              aria-expanded={whyPanelOpen}
              className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 transition-colors"
            >
              <Info className="w-3.5 h-3.5" />
              Why?
              {whyPanelOpen ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Expandable Why-Panel */}
      {whyPanelOpen && hasWhyPanel && (
        <div
          className="border-t border-slate-100 px-4 py-3"
          style={{ backgroundColor: 'var(--semantic-surface-raised)' }}
          role="region"
          aria-label="Alert clinical rationale"
        >
          <h5 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: 'var(--semantic-text-secondary)' }}>
            Clinical Rationale
          </h5>

          {/* Triggering Parameters */}
          {alert.triggering_parameters && alert.triggering_parameters.length > 0 && (
            <div className="mb-3">
              <h6 className="text-[11px] font-semibold mb-2" style={{ color: 'var(--semantic-text-primary)' }}>
                Triggering Parameters
              </h6>
              <div className="space-y-1.5">
                {alert.triggering_parameters.map((param: TriggeringParameter, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between text-xs py-1.5 px-2 rounded"
                    style={{
                      backgroundColor: param.breached
                        ? 'var(--clinical-severity-critical-wash)'
                        : 'var(--semantic-surface-canvas)',
                    }}
                  >
                    <span className="font-medium" style={{ color: 'var(--semantic-text-primary)' }}>
                      {param.name}{param.unit ? ` (${param.unit})` : ''}
                    </span>
                    <div className="flex items-center gap-2">
                      <span
                        className="tabular-nums"
                        style={{
                          color: param.breached
                            ? 'var(--clinical-severity-critical-on-surface)'
                            : 'var(--semantic-text-primary)',
                          fontWeight: param.breached ? 700 : 500,
                        }}
                      >
                        {param.value}
                      </span>
                      <span style={{ color: 'var(--semantic-text-secondary)' }}>/</span>
                      <span
                        className="tabular-nums"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                      >
                        {param.threshold}
                      </span>
                      {param.breached && (
                        <span
                          className="text-[10px] font-bold px-1 rounded"
                          style={{
                            color: 'var(--clinical-severity-critical-on-surface)',
                            backgroundColor: 'var(--clinical-severity-critical-fill)',
                          }}
                        >
                          BREACHED
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Rule Reference */}
          {alert.rule_reference && (
            <div className="mb-2">
              <h6 className="text-[11px] font-semibold mb-1" style={{ color: 'var(--semantic-text-primary)' }}>
                Clinical Evidence
              </h6>
              <div
                className="text-xs font-mono px-2 py-1 rounded"
                style={{
                  backgroundColor: 'var(--semantic-surface-canvas)',
                  color: 'var(--semantic-text-primary)',
                }}
              >
                {alert.rule_reference}
              </div>
            </div>
          )}

          {/* Alert Definition Version */}
          {alert.alert_definition_version && (
            <div className="mb-2">
              <h6 className="text-[11px] font-semibold mb-1" style={{ color: 'var(--semantic-text-primary)' }}>
                Definition Version
              </h6>
              <span
                className="text-xs font-mono px-2 py-0.5 rounded"
                style={{
                  backgroundColor: 'var(--semantic-surface-canvas)',
                  color: 'var(--semantic-text-secondary)',
                }}
              >
                {alert.alert_definition_version}
              </span>
            </div>
          )}

          {/* Data Coverage Note */}
          {alert.data_coverage_note && (
            <div>
              <h6 className="text-[11px] font-semibold mb-1" style={{ color: 'var(--semantic-text-primary)' }}>
                Data Coverage
              </h6>
              <p className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
                {alert.data_coverage_note}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
