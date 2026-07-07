'use client';

import { useEffect, useRef } from 'react';

export interface KeyboardShortcut {
  key: string;           // e.g., '1', '/', 'Escape', 'j', 'k'
  ctrlKey?: boolean;
  handler: () => void;
  enabled?: boolean;     // default true
}

/**
 * Register global keyboard shortcuts.
 * Shortcuts do NOT fire when the user is typing in an input, textarea, or select.
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]): void {
  // Use a ref so the listener always sees the latest shortcuts without re-registering
  const shortcutsRef = useRef(shortcuts);
  shortcutsRef.current = shortcuts;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Don't fire when user is typing in an input, textarea, select, or contenteditable
      const target = e.target as HTMLElement;
      const tag = target.tagName?.toLowerCase();
      if (
        tag === 'input' ||
        tag === 'textarea' ||
        tag === 'select' ||
        target.isContentEditable
      ) {
        return;
      }

      const active = shortcutsRef.current.filter((s) => s.enabled !== false);
      for (const shortcut of active) {
        const keyMatch = shortcut.key === e.key;
        const ctrlMatch = shortcut.ctrlKey
          ? e.ctrlKey || e.metaKey
          : !e.ctrlKey && !e.metaKey;

        if (keyMatch && ctrlMatch) {
          e.preventDefault();
          e.stopPropagation();
          shortcut.handler();
          return; // Only fire first matching shortcut
        }
      }
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);
}
