'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Sliders, Save, AlertTriangle, CheckCircle, RefreshCw, Clock, User } from 'lucide-react';
import Layout from '@/components/Layout';
import {
  fetchThresholds,
  updateThreshold,
  createThreshold,
  type ThresholdConfigResponse,
  type ThresholdConfigUpdate,
} from '@/lib/api';

const SCORE_TYPE_LABELS: Record<string, string> = {
  MEWS: 'MEWS Score',
  NEWS2: 'NEWS2 Score',
  SOFA: 'SOFA Score',
  qSOFA: 'qSOFA Score',
};

const SCOPE_LABELS: Record<string, string> = {
  tenant: 'Tenant-wide',
  unit: 'Unit',
  bed: 'Bed',
};

export default function AdminThresholdsPage() {
  const router = useRouter();
  const [thresholds, setThresholds] = useState<ThresholdConfigResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<number | null>(null);
  const [savedId, setSavedId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<number, string>>({});

  const loadThresholds = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchThresholds();
      setThresholds(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load thresholds');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadThresholds();
  }, [loadThresholds]);

  // Clear saved indicator after 3s
  useEffect(() => {
    if (savedId !== null) {
      const timer = setTimeout(() => setSavedId(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [savedId]);

  // --- Monotonic band validation ---
  function validateThreshold(t: ThresholdConfigResponse): string | null {
    const w = t.watch_threshold;
    const u = t.urgent_threshold;
    const c = t.critical_threshold;

    if (w >= u) {
      return `Watch threshold (${w}) must be less than urgent threshold (${u})`;
    }
    if (u >= c) {
      return `Urgent threshold (${u}) must be less than critical threshold (${c})`;
    }
    return null;
  }

  function updateField(id: number, field: keyof ThresholdConfigUpdate, value: number | string | null) {
    setThresholds((prev) =>
      prev.map((t) => {
        if (t.id !== id) return t;
        const updated = { ...t, [field]: value };
        // Re-validate
        const err = validateThreshold(updated as ThresholdConfigResponse);
        setValidationErrors((prev) => {
          const next = { ...prev };
          if (err) next[id] = err;
          else delete next[id];
          return next;
        });
        return updated;
      })
    );
  }

  async function handleSave(threshold: ThresholdConfigResponse) {
    const err = validateThreshold(threshold);
    if (err) {
      setValidationErrors((prev) => ({ ...prev, [threshold.id]: err }));
      return;
    }

    setSaving(threshold.id);
    setError(null);
    try {
      const updated = await updateThreshold(threshold.id, {
        watch_threshold: threshold.watch_threshold,
        urgent_threshold: threshold.urgent_threshold,
        critical_threshold: threshold.critical_threshold,
        rate_limit_per_hour: threshold.rate_limit_per_hour,
        cooldown_minutes: threshold.cooldown_minutes,
      });
      setThresholds((prev) =>
        prev.map((t) => (t.id === threshold.id ? updated : t))
      );
      setSavedId(threshold.id);
      setValidationErrors((prev) => {
        const next = { ...prev };
        delete next[threshold.id];
        return next;
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save threshold');
    } finally {
      setSaving(null);
    }
  }

  function getScopeLabel(t: ThresholdConfigResponse): string {
    if (t.unit) return `Unit: ${t.unit}`;
    return 'Tenant-wide';
  }

  function formatDate(iso: string | null): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleString();
  }

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/admin')}
          className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-3 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Admin
        </button>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center">
              <Sliders className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">Threshold Configuration</h1>
              <p className="text-slate-500 text-sm mt-0.5">
                Clinical score thresholds — per score type and scope
              </p>
            </div>
          </div>
          <button
            onClick={loadThresholds}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm text-slate-600 hover:bg-slate-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Info banner */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-medium text-blue-800">Clinical Threshold Management</p>
          <p className="text-sm text-blue-600 mt-0.5">
            Thresholds determine when score bands (watch / urgent / critical) trigger alerts.
            Validation enforces <strong>watch &lt; urgent &lt; critical</strong> monotonic ordering.
            Every change is audited.
          </p>
        </div>
      </div>

      {/* Global error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-red-700 text-sm mb-4">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="w-6 h-6 text-slate-400 animate-spin" />
        </div>
      )}

      {/* Empty state */}
      {!loading && thresholds.length === 0 && (
        <div className="text-center py-20 bg-white rounded-xl border border-slate-200">
          <Sliders className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500 font-medium">No thresholds configured</p>
        </div>
      )}

      {/* Thresholds grid */}
      {!loading && thresholds.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {thresholds.map((threshold) => {
            const valError = validationErrors[threshold.id];
            const isSaving = saving === threshold.id;
            const isSaved = savedId === threshold.id;

            return (
              <div
                key={threshold.id}
                className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm"
              >
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-slate-400 to-slate-600 flex items-center justify-center">
                    <Sliders className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">
                      {SCORE_TYPE_LABELS[threshold.score_type] || threshold.score_type}
                    </h3>
                    <p className="text-xs text-slate-400">
                      {getScopeLabel(threshold)} · ID {threshold.id}
                    </p>
                  </div>
                </div>

                {/* Score band inputs */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <ThresholdBandInput
                    label="Watch ≥"
                    value={threshold.watch_threshold}
                    onChange={(v) => updateField(threshold.id, 'watch_threshold', v)}
                    band="watch"
                  />
                  <ThresholdBandInput
                    label="Urgent ≥"
                    value={threshold.urgent_threshold}
                    onChange={(v) => updateField(threshold.id, 'urgent_threshold', v)}
                    band="urgent"
                  />
                  <ThresholdBandInput
                    label="Critical ≥"
                    value={threshold.critical_threshold}
                    onChange={(v) => updateField(threshold.id, 'critical_threshold', v)}
                    band="critical"
                  />
                </div>

                {/* Advanced settings */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div>
                    <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                      Rate Limit (alerts/hr)
                    </label>
                    <input
                      type="number"
                      value={threshold.rate_limit_per_hour ?? ''}
                      onChange={(e) =>
                        updateField(
                          threshold.id,
                          'rate_limit_per_hour',
                          e.target.value === '' ? null : parseInt(e.target.value)
                        )
                      }
                      min={0}
                      className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                      Cooldown (min)
                    </label>
                    <input
                      type="number"
                      value={threshold.cooldown_minutes ?? ''}
                      onChange={(e) =>
                        updateField(
                          threshold.id,
                          'cooldown_minutes',
                          e.target.value === '' ? null : parseInt(e.target.value)
                        )
                      }
                      min={0}
                      className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 outline-none"
                    />
                  </div>
                </div>

                {/* Validation error */}
                {valError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-2.5 text-xs text-red-700 mb-3 flex items-start gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                    {valError}
                  </div>
                )}

                {/* Monotonic band bar */}
                <div className="mb-4">
                  <div className="h-3 rounded-full bg-gradient-to-r from-green-400 via-yellow-400 via-orange-400 to-red-500 relative overflow-hidden">
                    {/* Band markers */}
                    <div className="absolute inset-0 flex">
                      <div
                        className="h-full bg-gradient-to-r from-green-400 to-yellow-400"
                        style={{
                          width: `${(threshold.watch_threshold / threshold.critical_threshold) * 100}%`,
                        }}
                      />
                      <div
                        className="h-full bg-gradient-to-r from-yellow-400 to-orange-400"
                        style={{
                          width: `${
                            ((threshold.urgent_threshold - threshold.watch_threshold) /
                              threshold.critical_threshold) *
                            100
                          }%`,
                        }}
                      />
                      <div className="h-full bg-gradient-to-r from-orange-400 to-red-500" style={{ flex: 1 }} />
                    </div>
                    {/* Tick markers */}
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-white/60"
                      style={{ left: `${(threshold.watch_threshold / threshold.critical_threshold) * 100}%` }}
                    />
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-white/60"
                      style={{ left: `${(threshold.urgent_threshold / threshold.critical_threshold) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                    <span>0 — Normal</span>
                    <span>Watch ≥{threshold.watch_threshold}</span>
                    <span>Urgent ≥{threshold.urgent_threshold}</span>
                    <span>Crit ≥{threshold.critical_threshold}</span>
                  </div>
                </div>

                {/* Audit info & save */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(threshold.updated_at)}
                    </span>
                    {threshold.updated_by && (
                      <span className="flex items-center gap-1">
                        <User className="w-3 h-3" />
                        {threshold.updated_by}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleSave(threshold)}
                    disabled={isSaving || !!valError}
                    className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                      isSaved
                        ? 'bg-green-100 text-green-700 border border-green-200'
                        : 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-sm hover:from-cyan-600 hover:to-blue-700 disabled:opacity-50'
                    }`}
                  >
                    {isSaving ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : isSaved ? (
                      <CheckCircle className="w-3.5 h-3.5" />
                    ) : (
                      <Save className="w-3.5 h-3.5" />
                    )}
                    {isSaved ? 'Saved!' : isSaving ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Layout>
  );
}

// --- Band input sub-component ---

function ThresholdBandInput({
  label,
  value,
  onChange,
  band,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  band: 'watch' | 'urgent' | 'critical';
}) {
  const bandStyles: Record<string, React.CSSProperties> = {
    watch: {
      backgroundColor: 'var(--clinical-severity-watch-wash)',
      borderColor: 'var(--clinical-severity-watch-signal)',
      color: 'var(--clinical-severity-watch-on-fill)',
    },
    urgent: {
      backgroundColor: 'var(--clinical-severity-urgent-wash)',
      borderColor: 'var(--clinical-severity-urgent-signal)',
      color: 'var(--clinical-severity-urgent-on-fill)',
    },
    critical: {
      backgroundColor: 'var(--clinical-severity-critical-wash)',
      borderColor: 'var(--clinical-severity-critical-signal)',
      color: 'var(--clinical-severity-critical-on-fill)',
    },
  };

  return (
    <div style={bandStyles[band]} className="rounded-lg p-2.5 border">
      <label className="text-[10px] font-semibold uppercase tracking-wider mb-1 block opacity-70">
        {label}
      </label>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value) || 0)}
        min={0}
        className="w-full bg-transparent border-none outline-none text-sm font-bold [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
      />
    </div>
  );
}
