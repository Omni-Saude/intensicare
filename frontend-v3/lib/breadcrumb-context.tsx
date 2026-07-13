'use client';

import type { ReactNode } from 'react';
import { createContext, useContext, useState, useCallback, useEffect } from 'react';

// ---------- types ----------

interface BreadcrumbContextType {
  /** Map of URL segment/ID -> human-readable label. */
  labels: Record<string, string>;
  /** Register (or overwrite) a label for a given URL segment/ID. Stable reference. */
  setLabel: (segment: string, label: string) => void;
  /** Remove a single segment's label. Stable reference. */
  clearLabel: (segment: string) => void;
  /** Remove all registered labels. Stable reference. */
  clearLabels: () => void;
}

// ---------- context ----------

const BreadcrumbContext = createContext<BreadcrumbContextType | undefined>(undefined);

// ---------- provider ----------

export function BreadcrumbProvider({ children }: { children: ReactNode }) {
  const [labels, setLabels] = useState<Record<string, string>>({});

  const setLabel = useCallback((segment: string, label: string) => {
    setLabels((prev) => {
      if (prev[segment] === label) return prev;
      return { ...prev, [segment]: label };
    });
  }, []);

  const clearLabel = useCallback((segment: string) => {
    setLabels((prev) => {
      if (!(segment in prev)) return prev;
      const next = { ...prev };
      delete next[segment];
      return next;
    });
  }, []);

  const clearLabels = useCallback(() => {
    setLabels({});
  }, []);

  return (
    <BreadcrumbContext.Provider value={{ labels, setLabel, clearLabel, clearLabels }}>
      {children}
    </BreadcrumbContext.Provider>
  );
}

// ---------- hooks ----------

/**
 * Low-level accessor for the breadcrumb label map. Prefer
 * `useSetBreadcrumbLabel` from pages that just need to register a label.
 */
export function useBreadcrumbLabels(): BreadcrumbContextType {
  const ctx = useContext(BreadcrumbContext);
  if (!ctx) {
    throw new Error('useBreadcrumbLabels must be used within a BreadcrumbProvider');
  }
  return ctx;
}

/**
 * Registers a human-readable label for a URL segment (e.g. an MPI ID or
 * pathway ID) so the breadcrumb in AppShell can display it instead of the
 * raw slug. Call from a page once the label value (e.g. `patient_name` from
 * an SWR response) is available:
 *
 *   useSetBreadcrumbLabel(mpiId, patient?.patient_name);
 *
 * No-ops while `label` is falsy/undefined (e.g. before data loads), and
 * automatically removes the label on unmount or when `segment`/`label`
 * change, so stale names never linger across navigations.
 */
export function useSetBreadcrumbLabel(segment: string | undefined, label: string | undefined | null) {
  const { setLabel, clearLabel } = useBreadcrumbLabels();

  useEffect(() => {
    if (!segment || !label) return;
    setLabel(segment, label);
    return () => {
      clearLabel(segment);
    };
  }, [segment, label, setLabel, clearLabel]);
}
