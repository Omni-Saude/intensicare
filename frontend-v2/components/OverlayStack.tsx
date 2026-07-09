'use client';

import React, {
  createContext,
  useContext,
  useEffect,
  useCallback,
  useRef,
  useState,
} from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

type OverlayId = string;

interface OverlayEntry {
  id: OverlayId;
  title?: string;
  content: React.ReactNode;
  /** The z-index for this overlay (auto-assigned) */
  zIndex: number;
}

interface OverlayStackContextValue {
  /** Push a new overlay onto the stack. Returns the overlay id. */
  push: (title: string | undefined, content: React.ReactNode) => OverlayId;
  /** Remove an overlay by id. If no id is given, pops the topmost overlay. */
  pop: (id?: OverlayId) => void;
  /** Remove all overlays */
  popAll: () => void;
  /** Current stack size */
  size: number;
}

/* ------------------------------------------------------------------ */
/*  Context                                                            */
/* ------------------------------------------------------------------ */

const OverlayStackContext = createContext<OverlayStackContextValue | null>(null);

/** Hook to access the overlay stack from any descendant component. */
export function useOverlayStack(): OverlayStackContextValue {
  const ctx = useContext(OverlayStackContext);
  if (!ctx) {
    throw new Error('useOverlayStack must be used within <OverlayStackProvider>');
  }
  return ctx;
}

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const BASE_Z_INDEX = 50;
const Z_INDEX_STEP = 10;

/* ------------------------------------------------------------------ */
/*  Provider + Renderer                                                */
/* ------------------------------------------------------------------ */

interface OverlayStackProviderProps {
  children: React.ReactNode;
}

/**
 * OverlayStackProvider
 *
 * Wraps the application (or a section) with an overlay-stack manager.
 * Provides `useOverlayStack()` to descendants and renders the current
 * stack of drawers/modals using @radix-ui/react-dialog primitives.
 *
 * Features:
 * - Nested overlays with automatic z-index stacking
 * - Esc closes the topmost overlay
 * - Focus trapping via Radix Dialog
 * - Back-button (browser) support: pops the topmost overlay
 */
export function OverlayStackProvider({ children }: OverlayStackProviderProps) {
  const [stack, setStack] = useState<OverlayEntry[]>([]);
  const idCounterRef = useRef(0);
  const historyRef = useRef<OverlayId[]>([]); // tracks push order for back-button

  /* -- push -- */
  const push = useCallback((title: string | undefined, content: React.ReactNode): OverlayId => {
    const id = `overlay-${++idCounterRef.current}`;

    setStack((prev) => {
      // Calculate next z-index: base + (current length * step)
      const zIndex = BASE_Z_INDEX + prev.length * Z_INDEX_STEP;
      return [...prev, { id, title, content, zIndex }];
    });

    // Track in history for back-button support
    historyRef.current.push(id);
    window.history.pushState({ overlayId: id }, '');

    return id;
  }, []);

  /* -- pop -- */
  const pop = useCallback((id?: OverlayId) => {
    setStack((prev) => {
      if (prev.length === 0) return prev;

      if (id) {
        // Pop a specific overlay (and all overlays above it)
        const index = prev.findIndex((entry) => entry.id === id);
        if (index === -1) return prev;
        const newStack = prev.slice(0, index);
        // Remove from history
        historyRef.current = historyRef.current.filter(
          (hid) => newStack.some((entry) => entry.id === hid)
        );
        return newStack;
      }

      // Pop the topmost
      const popped = prev[prev.length - 1];
      historyRef.current = historyRef.current.filter((hid) => hid !== popped.id);
      return prev.slice(0, -1);
    });
  }, []);

  /* -- popAll -- */
  const popAll = useCallback(() => {
    setStack([]);
    historyRef.current = [];
  }, []);

  /* -- Back-button handler -- */
  useEffect(() => {
    const handlePopState = () => {
      // User pressed back — pop the topmost overlay
      setStack((prev) => {
        if (prev.length === 0) return prev;
        const popped = prev[prev.length - 1];
        historyRef.current = historyRef.current.filter((hid) => hid !== popped.id);
        return prev.slice(0, -1);
      });
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  /* -- Context value -- */
  const contextValue: OverlayStackContextValue = {
    push,
    pop,
    popAll,
    size: stack.length,
  };

  return (
    <OverlayStackContext.Provider value={contextValue}>
      {children}

      {/* Render the overlay stack */}
      {stack.map((entry) => (
        <Dialog.Root
          key={entry.id}
          open={true}
          onOpenChange={(open) => {
            if (!open) pop(entry.id);
          }}
        >
          <Dialog.Portal>
            {/* Overlay backdrop */}
            <Dialog.Overlay
              className="fixed inset-0 bg-black/40"
              style={{
                zIndex: entry.zIndex,
                animation: 'fadeIn 150ms ease-out',
              }}
            />

            {/* Content */}
            <Dialog.Content
              className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md rounded-2xl shadow-xl overflow-auto max-h-[90vh]"
              style={{
                zIndex: entry.zIndex + 1,
                backgroundColor: 'var(--semantic-surface-raised)',
                color: 'var(--semantic-text-primary)',
              }}
              onEscapeKeyDown={(e) => {
                // Only close topmost
                if (entry.id === stack[stack.length - 1]?.id) {
                  pop(entry.id);
                }
                e.preventDefault();
              }}
              onPointerDownOutside={(e) => {
                // Only close topmost when clicking outside
                if (entry.id === stack[stack.length - 1]?.id) {
                  pop(entry.id);
                }
                e.preventDefault();
              }}
            >
              {/* Header */}
              {(entry.title || true) && (
                <div className="px-6 pt-6 pb-0 flex items-center justify-between">
                  {entry.title && (
                    <Dialog.Title
                      className="text-lg font-semibold"
                      style={{ color: 'var(--semantic-text-primary)' }}
                    >
                      {entry.title}
                    </Dialog.Title>
                  )}
                  <Dialog.Close asChild>
                    <button
                      onClick={() => pop(entry.id)}
                      className="p-1 rounded-lg hover:bg-black/10 dark:hover:bg-white/10 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
                      style={{ marginLeft: entry.title ? undefined : 'auto' }}
                      aria-label="Fechar"
                    >
                      <X
                        className="w-5 h-5"
                        style={{ color: 'var(--semantic-text-secondary)' }}
                        aria-hidden="true"
                      />
                    </button>
                  </Dialog.Close>
                </div>
              )}

              {/* Body */}
              <div className="px-6 pb-6 pt-4">
                {typeof entry.content === 'function'
                  ? (entry.content as (props: { close: () => void }) => React.ReactNode)({
                      close: () => pop(entry.id),
                    })
                  : entry.content}
              </div>
            </Dialog.Content>
          </Dialog.Portal>
        </Dialog.Root>
      ))}
    </OverlayStackContext.Provider>
  );
}

/**
 * Convenience component that wraps the entire app with OverlayStackProvider.
 * Also re-exports useOverlayStack for easy importing.
 */
export default function OverlayStack({ children }: { children: React.ReactNode }) {
  return <OverlayStackProvider>{children}</OverlayStackProvider>;
}
