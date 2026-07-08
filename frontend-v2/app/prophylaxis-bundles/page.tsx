'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  CheckCircle,
  Clock,
  Circle,
  Ban,
  Loader2,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Shield,
} from 'lucide-react';
import Layout from '@/components/Layout';
import ErrorBoundary from '@/components/ErrorBoundary';
import BundleCard from '@/components/BundleCard';
import type { BundleInfo, BundleStatus } from '@/components/BundleCard';
import {
  PROPHYLAXIS_BUNDLES,
  computeBundleScore,
  BUNDLE_STATUS_LABELS,
} from '@/lib/prophylaxis-types';
import { useKeyboardShortcuts, type KeyboardShortcut } from '@/hooks/useKeyboardShortcuts';

// ─── Status → Icon mapping for the summary bar ──────────────────────────────

const STATUS_ICONS: Record<BundleStatus, React.ComponentType<{ className?: string }>> = {
  complete: CheckCircle,
  partial: Clock,
  pending: Circle,
  na: Ban,
};

const STATUS_TOKEN_ROOT: Record<BundleStatus, string> = {
  complete: 'complete',
  partial: 'partial',
  pending: 'pending',
  na: 'na',
};

// ─── Summary Bar ────────────────────────────────────────────────────────────

function SummaryBar({ bundles }: { bundles: BundleInfo[] }) {
  return (
    <div
      className="flex flex-wrap gap-3 mb-6 p-4 rounded-xl border"
      style={{
        borderColor: 'var(--semantic-border-default)',
        backgroundColor: 'var(--semantic-surface-raised)',
      }}
      role="region"
      aria-label="Resumo dos bundles de profilaxia"
    >
      {bundles.map((bundle) => {
        const root = STATUS_TOKEN_ROOT[bundle.status];
        const Icon = STATUS_ICONS[bundle.status];
        const score = computeBundleScore(bundle);

        return (
          <div
            key={bundle.id}
            className="flex items-center gap-2 px-3 py-2 rounded-lg min-w-0 flex-1 basis-40"
            style={{
              backgroundColor: `var(--clinical-prophylaxis-${root}-wash)`,
              opacity: 0.85,
            }}
            title={`${bundle.name}: ${BUNDLE_STATUS_LABELS[bundle.status]} — ${score}%`}
          >
            <span
              style={{ color: `var(--clinical-prophylaxis-${root}-signal)` }}
              aria-hidden="true"
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
            </span>
            <div className="min-w-0 flex-1">
              <p
                className="text-xs font-semibold truncate"
                style={{ color: `var(--clinical-prophylaxis-${root}-on-surface)` }}
              >
                {bundle.name.split(' — ')[0]}
              </p>
              <p
                className="text-[10px]"
                style={{ color: `var(--clinical-prophylaxis-${root}-on-surface)`, opacity: 0.7 }}
              >
                {BUNDLE_STATUS_LABELS[bundle.status]}
                {bundle.status !== 'na' && ` · ${score}%`}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── Tabs ───────────────────────────────────────────────────────────────────

function BundleTabs({
  bundles,
  activeIndex,
  onSelect,
}: {
  bundles: BundleInfo[];
  activeIndex: number;
  onSelect: (index: number) => void;
}) {
  return (
    <div
      className="flex overflow-x-auto border-b mb-6 gap-1"
      style={{ borderColor: 'var(--semantic-border-default)' }}
      role="tablist"
      aria-label="Bundles de profilaxia"
    >
      {bundles.map((bundle, idx) => {
        const isActive = idx === activeIndex;
        const root = STATUS_TOKEN_ROOT[bundle.status];

        return (
          <button
            key={bundle.id}
            role="tab"
            aria-selected={isActive}
            aria-controls={`panel-${bundle.id}`}
            id={`tab-${bundle.id}`}
            tabIndex={isActive ? 0 : -1}
            onClick={() => onSelect(idx)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap rounded-t-lg transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset ${
              isActive ? '-mb-[1px] border-b-2' : 'border-b-2 border-transparent'
            }`}
            style={{
              color: isActive
                ? `var(--clinical-prophylaxis-${root}-on-surface)`
                : 'var(--semantic-text-secondary)',
              backgroundColor: isActive
                ? 'var(--semantic-surface-canvas)'
                : 'transparent',
              borderBottomColor: isActive
                ? `var(--clinical-prophylaxis-${root}-signal)`
                : 'transparent',
            }}
          >
            {bundle.name.split(' — ')[0]}
          </button>
        );
      })}
    </div>
  );
}

// ─── Loading Skeleton ────────────────────────────────────────────────────────

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse" role="status" aria-label="Carregando bundles de profilaxia">
      {/* Summary skeleton */}
      <div
        className="flex gap-3 p-4 rounded-xl border"
        style={{
          borderColor: 'var(--semantic-border-default)',
          backgroundColor: 'var(--semantic-surface-raised)',
        }}
      >
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex-1 h-14 rounded-lg"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        ))}
      </div>
      {/* Tab skeleton */}
      <div className="flex gap-1 border-b pb-1" style={{ borderColor: 'var(--semantic-border-default)' }}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-9 w-24 rounded-t-lg"
            style={{ backgroundColor: 'var(--semantic-surface-overlay)' }}
          />
        ))}
      </div>
      {/* Card skeleton — reuse BundleCard's built-in skeleton */}
      <BundleCard
        bundle={{ id: 'skel', name: '', status: 'pending', criteria: [] }}
        isLoading
      />
    </div>
  );
}

// ─── Error State ─────────────────────────────────────────────────────────────

function ErrorDisplay({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="border rounded-xl p-6 m-4"
      style={{
        backgroundColor: 'var(--clinical-severity-critical-wash)',
        borderColor: 'var(--clinical-severity-critical-signal)',
        color: 'var(--clinical-severity-critical-on-surface)',
      }}
    >
      <div className="flex items-start gap-3">
        <AlertTriangle
          className="w-6 h-6 flex-shrink-0 mt-0.5"
          style={{ color: 'var(--clinical-severity-critical-signal)' }}
          aria-hidden="true"
        />
        <div className="min-w-0">
          <h2 className="font-semibold text-lg">Erro ao carregar bundles</h2>
          <p className="text-sm mt-1 opacity-90">{message}</p>
          <button
            onClick={onRetry}
            className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all"
            style={{
              backgroundColor: 'var(--semantic-surface-raised)',
              color: 'var(--semantic-text-primary)',
              border: '1px solid var(--semantic-border-default)',
            }}
          >
            <Loader2 className="w-4 h-4" aria-hidden="true" />
            Tentar novamente
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

function ProphylaxisBundlesPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [bundles, setBundles] = useState<BundleInfo[]>(PROPHYLAXIS_BUNDLES);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Keyboard navigation for tabs (← →) ─────────────────────────────────
  const shortcuts: KeyboardShortcut[] = useMemo(
    () => [
      {
        key: 'ArrowLeft',
        handler: () =>
          setActiveTab((prev) => (prev > 0 ? prev - 1 : bundles.length - 1)),
      },
      {
        key: 'ArrowRight',
        handler: () =>
          setActiveTab((prev) => (prev < bundles.length - 1 ? prev + 1 : 0)),
      },
    ],
    [bundles.length],
  );

  useKeyboardShortcuts(shortcuts);

  // ── Toggle criterion (mock callback) ───────────────────────────────────
  const handleToggle = useCallback(
    (bundleId: string, criterionId: string, met: boolean) => {
      setBundles((prev) =>
        prev.map((b) => {
          if (b.id !== bundleId) return b;
          const updatedCriteria = b.criteria.map((c) =>
            c.id === criterionId ? { ...c, met } : c,
          );
          // Recompute score and status
          const applicable = updatedCriteria.filter((c) => !c.na);
          const metCount = applicable.filter((c) => c.met).length;
          const newScore =
            applicable.length > 0
              ? Math.round((metCount / applicable.length) * 100)
              : 0;

          let newStatus: BundleStatus;
          if (applicable.length === 0) {
            newStatus = 'na';
          } else if (metCount === applicable.length) {
            newStatus = 'complete';
          } else if (metCount > 0) {
            newStatus = 'partial';
          } else {
            newStatus = 'pending';
          }

          return {
            ...b,
            criteria: updatedCriteria,
            score: newScore,
            status: newStatus,
          };
        }),
      );
    },
    [],
  );

  // ── Simulate loading state (demo toggle) ──────────────────────────────
  const simulateLoading = useCallback(() => {
    setIsLoading(true);
    setError(null);
    setTimeout(() => setIsLoading(false), 1500);
  }, []);

  const simulateError = useCallback(() => {
    setIsLoading(false);
    setError('Falha na conexão ao servidor de profilaxia. Verifique sua rede e tente novamente.');
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // ── Active bundle ─────────────────────────────────────────────────────
  const activeBundle = bundles[activeTab];
  if (!activeBundle) {
    return null; // Should never happen with valid state
  }
  const allComplete = bundles.every((b) => b.status === 'complete' || b.status === 'na');
  const allPending = bundles.every((b) => b.status === 'pending' || b.status === 'na');

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        {/* ── Header ───────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1
              className="text-2xl font-bold flex items-center gap-2"
              style={{ color: 'var(--semantic-text-primary)' }}
            >
              <Shield className="w-6 h-6" aria-hidden="true" />
              Bundles de Profilaxia
            </h1>
            <p className="text-sm mt-1" style={{ color: 'var(--semantic-text-secondary)' }}>
              {bundles.length} bundles &middot;{' '}
              {bundles.filter((b) => b.status === 'complete').length} completos
              {allComplete && (
                <span
                  className="ml-2 inline-flex items-center gap-1 text-xs font-semibold"
                  style={{ color: 'var(--clinical-prophylaxis-complete-on-surface)' }}
                >
                  <CheckCircle className="w-3.5 h-3.5" aria-hidden="true" />
                  Todos completos
                </span>
              )}
              {allPending && !allComplete && (
                <span
                  className="ml-2 inline-flex items-center gap-1 text-xs font-semibold"
                  style={{ color: 'var(--clinical-prophylaxis-pending-on-surface)' }}
                >
                  <Circle className="w-3.5 h-3.5" aria-hidden="true" />
                  Todos pendentes
                </span>
              )}
            </p>
          </div>

          {/* Demo state toggles */}
          <div className="flex gap-2">
            <button
              onClick={simulateLoading}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors disabled:opacity-50"
              style={{
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-secondary)',
                borderColor: 'var(--semantic-border-default)',
              }}
              aria-label="Simular carregamento"
            >
              <Loader2 className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} aria-hidden="true" />
              Loading
            </button>
            <button
              onClick={simulateError}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
              style={{
                backgroundColor: 'var(--clinical-severity-critical-wash)',
                color: 'var(--clinical-severity-critical-on-surface)',
                borderColor: 'var(--clinical-severity-critical-signal)',
              }}
              aria-label="Simular erro"
            >
              <AlertTriangle className="w-3.5 h-3.5" aria-hidden="true" />
              Error
            </button>
          </div>
        </div>

        {/* ── Error ────────────────────────────────────────────────────── */}
        {error && (
          <ErrorDisplay
            message={error}
            onRetry={() => {
              clearError();
              simulateLoading();
            }}
          />
        )}

        {/* ── Loading ──────────────────────────────────────────────────── */}
        {isLoading && <LoadingSkeleton />}

        {/* ── Main Content ─────────────────────────────────────────────── */}
        {!error && !isLoading && (
          <>
            {/* Summary bar */}
            <SummaryBar bundles={bundles} />

            {/* Tabs */}
            <BundleTabs
              bundles={bundles}
              activeIndex={activeTab}
              onSelect={setActiveTab}
            />

            {/* Keyboard shortcut hint */}
            <p
              className="text-xs mb-4"
              style={{ color: 'var(--semantic-text-secondary)' }}
            >
              Use as setas <kbd
                className="px-1 py-0.5 rounded text-[10px] font-mono"
                style={{
                  backgroundColor: 'var(--semantic-surface-overlay)',
                  color: 'var(--semantic-text-primary)',
                }}
              >←</kbd> <kbd
                className="px-1 py-0.5 rounded text-[10px] font-mono"
                style={{
                  backgroundColor: 'var(--semantic-surface-overlay)',
                  color: 'var(--semantic-text-primary)',
                }}
              >→</kbd> para navegar entre os bundles
            </p>

            {/* Active BundleCard */}
            <div
              id={`panel-${activeBundle.id}`}
              role="tabpanel"
              aria-labelledby={`tab-${activeBundle.id}`}
            >
              <BundleCard
                bundle={activeBundle}
                onToggle={(criterionId, met) =>
                  handleToggle(activeBundle.id, criterionId, met)
                }
              />
            </div>

            {/* Tab navigation footer */}
            <div className="flex items-center justify-between mt-6">
              <button
                onClick={() =>
                  setActiveTab((prev) => (prev > 0 ? prev - 1 : bundles.length - 1))
                }
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-30"
                style={{
                  color: 'var(--semantic-text-secondary)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                  border: '1px solid var(--semantic-border-default)',
                }}
                aria-label="Bundle anterior"
              >
                <ArrowLeft className="w-4 h-4" aria-hidden="true" />
                Anterior
              </button>

              <span
                className="text-sm tabular-nums"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {activeTab + 1} de {bundles.length}
              </span>

              <button
                onClick={() =>
                  setActiveTab((prev) => (prev < bundles.length - 1 ? prev + 1 : 0))
                }
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                style={{
                  color: 'var(--semantic-text-secondary)',
                  backgroundColor: 'var(--semantic-surface-raised)',
                  border: '1px solid var(--semantic-border-default)',
                }}
                aria-label="Próximo bundle"
              >
                Próximo
                <ArrowRight className="w-4 h-4" aria-hidden="true" />
              </button>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}

// ─── Exported Page (wrapped in ErrorBoundary) ────────────────────────────────

export default function ProphylaxisBundlesPageWithBoundary() {
  return (
    <ErrorBoundary>
      <ProphylaxisBundlesPage />
    </ErrorBoundary>
  );
}
