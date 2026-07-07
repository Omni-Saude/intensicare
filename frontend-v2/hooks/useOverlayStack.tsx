'use client';

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from 'react';

// ─── Types ───────────────────────────────────────────────────────────────────

export interface OverlayStack {
  /** Push an overlay onto the stack */
  open: (id: string) => void;
  /** Close the topmost overlay (no-op if stack is empty) */
  close: () => void;
  /** Close all overlays at once */
  closeAll: () => void;
  /** Whether the given overlay is the topmost (receives input) */
  isTopmost: (id: string) => boolean;
  /** Number of overlays currently open */
  depth: number;
  /** ID of the topmost overlay, or null if stack is empty */
  activeId: string | null;
}

// ─── Context ─────────────────────────────────────────────────────────────────

const OverlayStackContext = createContext<OverlayStack | null>(null);

// ─── Provider ────────────────────────────────────────────────────────────────

export function OverlayStackProvider({ children }: { children: ReactNode }) {
  const [stack, setStack] = useState<string[]>([]);

  const open = useCallback((id: string) => {
    setStack((prev) => {
      // Don't push duplicate consecutive entries
      if (prev.length > 0 && prev[prev.length - 1] === id) return prev;
      return [...prev, id];
    });
  }, []);

  const close = useCallback(() => {
    setStack((prev) => {
      if (prev.length === 0) return prev;
      return prev.slice(0, -1);
    });
  }, []);

  const closeAll = useCallback(() => {
    setStack([]);
  }, []);

  const isTopmost = useCallback(
    (id: string) => {
      if (stack.length === 0) return false;
      return stack[stack.length - 1] === id;
    },
    [stack],
  );

  const depth = stack.length;
  const activeId: string | null = depth > 0 ? stack[depth - 1]! : null;

  // Global Escape key: close only the topmost overlay
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && stack.length > 0) {
        e.preventDefault();
        close();
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [stack, close]);

  const value: OverlayStack = { open, close, closeAll, isTopmost, depth, activeId };

  return (
    <OverlayStackContext.Provider value={value}>
      {children}
    </OverlayStackContext.Provider>
  );
}

// ─── Hook ────────────────────────────────────────────────────────────────────

export function useOverlayStack(): OverlayStack {
  const ctx = useContext(OverlayStackContext);
  if (!ctx) {
    throw new Error('useOverlayStack must be used within an <OverlayStackProvider>');
  }
  return ctx;
}
