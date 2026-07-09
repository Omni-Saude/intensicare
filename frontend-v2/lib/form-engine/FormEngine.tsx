'use client';

import React, { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { ChevronDown, ChevronRight } from 'lucide-react';
import type { FormConfig, FormField } from './types';

// ─── Renderer imports ────────────────────────────────────────────────────────

import StringField from './renderers/StringField';
import SelectField from './renderers/SelectField';
import NumberField from './renderers/NumberField';
import BooleanField from './renderers/BooleanField';
import CheckboxField from './renderers/CheckboxField';
import DateField from './renderers/DateField';
import MaskedField from './renderers/MaskedField';

// ─── Renderer map (maps field type → component) ─────────────────────────────

const rendererMap: Record<string, React.ComponentType<any>> = {
  string: StringField,
  select: SelectField,
  number: NumberField,
  boolean: BooleanField,
  checkbox: CheckboxField,
  date: DateField,
  masked: MaskedField,
};

// ─── Offline queue (M8 / ADR-0029) ───────────────────────────────────────────

const OFFLINE_QUEUE_KEY = 'intensicare:offline-queue';
const OFFLINE_FLUSH_BATCH_SIZE = 5;

interface OfflineEntry {
  /** ISO timestamp when the submission was queued */
  queuedAt: string;
  /** The form data payload */
  data: Record<string, any>;
  /** Whether this entry has been marked for retry */
  retryCount: number;
  /** Unique ID for deduplication */
  id: string;
}

function loadOfflineQueue(): OfflineEntry[] {
  try {
    const raw = localStorage.getItem(OFFLINE_QUEUE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as OfflineEntry[];
  } catch {
    return [];
  }
}

function saveOfflineQueue(queue: OfflineEntry[]): void {
  try {
    localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
  } catch {
    // Storage full — silently drop; the queue is best-effort.
  }
}

/**
 * Attempt to flush the offline queue to the server.
 * Called on connectivity restoration and after successful online submissions.
 */
async function flushOfflineQueue(
  submitFn: (data: Record<string, any>) => void | Promise<void>,
): Promise<void> {
  const queue = loadOfflineQueue();
  if (queue.length === 0) return;

  // Process in small batches to avoid overwhelming the server.
  const batch = queue.slice(0, OFFLINE_FLUSH_BATCH_SIZE);
  const remaining = queue.slice(OFFLINE_FLUSH_BATCH_SIZE);

  const failed: OfflineEntry[] = [];

  for (const entry of batch) {
    try {
      await submitFn({ ...entry.data, submitted_offline: true });
    } catch {
      // If flush fails, keep the entry (with incremented retry count).
      failed.push({ ...entry, retryCount: (entry.retryCount || 0) + 1 });
    }
  }

  // Retain failed entries and unprocessed remaining entries.
  const newQueue = [...failed, ...remaining];
  saveOfflineQueue(newQueue);
}

/**
 * Hook that listens for online/offline events and flushes the queue
 * when connectivity is restored.
 */
function useOfflineQueue(
  submitFn: (data: Record<string, any>) => void | Promise<void>,
): { isOnline: boolean; queueSize: number; enqueue: (data: Record<string, any>) => void } {
  const [isOnline, setIsOnline] = useState<boolean>(
    typeof navigator !== 'undefined' ? navigator.onLine : true,
  );
  const [queueSize, setQueueSize] = useState<number>(() => {
    if (typeof localStorage === 'undefined') return 0;
    return loadOfflineQueue().length;
  });

  const submitRef = useRef(submitFn);
  submitRef.current = submitFn;

  // Listen for online/offline events.
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // Flush the queue when we come back online.
      flushOfflineQueue(submitRef.current).then(() => {
        setQueueSize(loadOfflineQueue().length);
      });
    };
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Also check for service worker registration as a connectivity signal.
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      // Service worker is active — good signal for offline readiness.
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const enqueue = useCallback(
    (data: Record<string, any>) => {
      const entry: OfflineEntry = {
        queuedAt: new Date().toISOString(),
        data,
        retryCount: 0,
        id: crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      };
      const queue = loadOfflineQueue();
      queue.push(entry);
      saveOfflineQueue(queue);
      setQueueSize(queue.length);
    },
    [],
  );

  return { isOnline, queueSize, enqueue };
}

// ─── Dynamic schema builder ──────────────────────────────────────────────────

function buildZodSchema(config: FormConfig): z.ZodObject<any> {
  const shape: Record<string, any> = {};

  for (const group of config.groups) {
    for (const field of group.fields) {
      let zodField: any;

      switch (field.type) {
        case 'number':
          zodField = z.number({ error: `${field.label} é obrigatório` });
          if (field.min !== undefined) {
            zodField = zodField.min(field.min, `${field.label} deve ser ≥ ${field.min}`);
          }
          if (field.max !== undefined) {
            zodField = zodField.max(field.max, `${field.label} deve ser ≤ ${field.max}`);
          }
          break;

        case 'boolean':
        case 'checkbox':
          zodField = z.boolean({ error: `${field.label} é obrigatório` });
          break;

        case 'multicheck':
          zodField = z.array(z.string());
          break;

        case 'string':
        case 'select':
        case 'date':
        case 'masked':
        default:
          zodField = z.string({ error: `${field.label} é obrigatório` });
          break;
      }

      if (!field.required) {
        zodField = zodField.optional();
      } else {
        // For string types, add a minimum length constraint to prevent empty strings
        if (
          field.type === 'string' ||
          field.type === 'select' ||
          field.type === 'masked'
        ) {
          zodField = zodField.min(1, `${field.label} é obrigatório`);
        }
      }

      shape[field.name] = zodField;
    }
  }

  let schema = z.object(shape);

  // ─── Cross-field validation: atLeastOne ─────────────────────────────────
  if (config.validation?.atLeastOne?.length) {
    schema = schema.superRefine((data: Record<string, any>, ctx) => {
      const atLeastOneFields = config.validation!.atLeastOne!;
      const anyFilled = atLeastOneFields.some((name) => {
        const val = data[name];
        return val !== undefined && val !== null && val !== '';
      });

      if (!anyFilled) {
        for (const name of atLeastOneFields) {
          ctx.addIssue({
            code: 'custom' as const,
            path: [name],
            message: 'Pelo menos um dos campos deve ser preenchido',
          });
        }
      }
    });
  }

  return schema as z.ZodObject<any>;
}

// ─── Component ───────────────────────────────────────────────────────────────

interface FormEngineProps {
  config: FormConfig;
  onSubmit: (data: Record<string, any>) => void | Promise<void>;
  defaultValues?: Record<string, any>;
}

export default function FormEngine({ config, onSubmit, defaultValues }: FormEngineProps) {
  const schema = useMemo(() => buildZodSchema(config), [config]);

  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: defaultValues as any,
  });

  const {
    handleSubmit,
    formState: { errors, isSubmitting },
  } = form;

  // ─── Offline queue (M8 / ADR-0029) ────────────────────────────────────────
  const { isOnline, queueSize, enqueue } = useOfflineQueue(onSubmit);

  const onValid = async (data: Record<string, any>) => {
    if (!isOnline && typeof navigator !== 'undefined' && !navigator.onLine) {
      // Offline: queue the submission locally. The server expects a
      // ``submitted_offline`` flag on queued submissions so it can apply
      // the correct timestamp logic (ADR-0029).
      enqueue(data);
      return;
    }

    try {
      await onSubmit(data);
      // After a successful online submission, try flushing any backlog.
      flushOfflineQueue(onSubmit).catch(() => {
        // Silently ignore flush failures — entries stay queued for next attempt.
      });
    } catch (err: unknown) {
      // Network error or server unavailable — save to localStorage queue.
      // Check if it's likely a network issue (fetch failed, timeout, etc.)
      const isNetworkError =
        err instanceof TypeError ||
        (err instanceof Error &&
          (err.message.includes('fetch') ||
           err.message.includes('network') ||
           err.message.includes('Failed to fetch') ||
           err.message.includes('NetworkError') ||
           err.message.includes('AbortError')));

      if (isNetworkError || !navigator.onLine) {
        enqueue(data);
        // Prevent react-hook-form from showing an error state.
        return;
      }

      // Non-network errors re-throw so the form can display validation/server errors.
      throw err;
    }
  };

  // ─── Collapsible group state ──────────────────────────────────────────────
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>(() => {
    const state: Record<string, boolean> = {};
    for (const group of config.groups) {
      if (group.collapsible) {
        state[group.title] = !group.defaultOpen;
      }
    }
    return state;
  });

  const toggleGroup = (title: string) => {
    setCollapsed((prev) => ({ ...prev, [title]: !prev[title] }));
  };

  // ─── Render ────────────────────────────────────────────────────────────────

  return (
    <form onSubmit={handleSubmit(onValid)} noValidate>
      <h2
        className="text-lg font-semibold mb-4"
        style={{ color: 'var(--semantic-text-primary)' }}
      >
        {config.title}
      </h2>

      {config.description && (
        <p
          className="text-sm mb-5"
          style={{ color: 'var(--semantic-text-secondary)' }}
        >
          {config.description}
        </p>
      )}

      {/* ─── Offline queue indicator (M8) ───────────────────────────────── */}
      {queueSize > 0 && (
        <div
          className="mb-4 px-3 py-2 rounded-md text-sm flex items-center gap-2"
          style={{
            backgroundColor: 'var(--clinical-severity-warning-fill, #fef3c7)',
            color: 'var(--clinical-severity-warning-on-fill, #92400e)',
          }}
          role="status"
          aria-live="polite"
        >
          <span aria-hidden="true">⚠</span>
          <span>
            {queueSize} formulário{queueSize > 1 ? 's' : ''} pendente{queueSize > 1 ? 's' : ''} de envio.
            {isOnline
              ? ' Serão enviados automaticamente.'
              : ' Sincronização automática ao reconectar.'}
          </span>
        </div>
      )}

      {config.groups.map((group) => {
        const isCollapsible = group.collapsible === true;
        const isCollapsed = collapsed[group.title] === true;

        return (
          <div key={group.title} className="mb-5">
            {/* Group header */}
            {isCollapsible ? (
              <button
                type="button"
                onClick={() => toggleGroup(group.title)}
                aria-expanded={!isCollapsed}
                className="w-full flex items-center gap-2 text-left mb-3"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {isCollapsed ? (
                  <ChevronRight className="w-4 h-4 flex-shrink-0" />
                ) : (
                  <ChevronDown className="w-4 h-4 flex-shrink-0" />
                )}
                <span className="text-sm font-semibold uppercase tracking-wider">
                  {group.title}
                </span>
              </button>
            ) : (
              <h3
                className="text-sm font-semibold uppercase tracking-wider mb-3"
                style={{ color: 'var(--semantic-text-secondary)' }}
              >
                {group.title}
              </h3>
            )}

            {/* Group body */}
            {(!isCollapsible || !isCollapsed) && (
              <div>
                {group.fields.map((field) => {
                  const errorMsg = errors[field.name]?.message as string | undefined;
                  const Renderer = rendererMap[field.type] || StringField;

                  return (
                    <Renderer
                      key={field.name}
                      field={field}
                      form={form}
                      error={errorMsg}
                    />
                  );
                })}
              </div>
            )}
          </div>
        );
      })}

      {/* Submit area */}
      <div className="mt-6 flex items-center gap-4">
        <button
          type="submit"
          disabled={isSubmitting}
          aria-label="Enviar formulário"
          className="flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium text-sm transition-all disabled:opacity-50 cursor-pointer"
          style={{
            backgroundColor: 'var(--clinical-severity-normal-fill)',
            color: 'var(--clinical-severity-normal-on-fill)',
          }}
        >
          {isSubmitting ? 'Enviando...' : 'Enviar Avaliação'}
        </button>
      </div>
    </form>
  );
}
