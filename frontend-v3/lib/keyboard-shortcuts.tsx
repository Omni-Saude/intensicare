'use client';

import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
  type ReactNode,
} from 'react';
import { useRouter } from 'next/navigation';
import { X } from 'lucide-react';

// ---------------------------------------------------------------------------
// Global keyboard shortcuts (GitHub/Linear-style "g then key" chords)
//
//   g d  → Dashboard (/)
//   g a  → Alertas (/alerts)
//   g t  → Trilhas (/pathways)
//   ?    → Toggle keyboard shortcuts help overlay
//
// Rules:
//   - Ignored while focus is on an input/textarea/select/contentEditable
//     element, so shortcuts never hijack typing (e.g. searching, forms).
//   - No modifier keys (Ctrl/Cmd/Alt) — those are left to the browser.
//   - The `g` prefix expires after CHORD_TIMEOUT_MS if no follow-up key
//     arrives, so a lone `g` never lingers as a pending chord.
// ---------------------------------------------------------------------------

export interface ShortcutEntry {
  /** Human-readable key combo, e.g. "g d". */
  keys: string;
  /** PT-BR description of what the shortcut does. */
  description: string;
}

const CHORD_TIMEOUT_MS = 1500;

const CHORD_ROUTES: Record<string, string> = {
  d: '/',
  a: '/alerts',
  t: '/pathways',
};

export const SHORTCUTS: ShortcutEntry[] = [
  { keys: 'g d', description: 'Ir para o Dashboard' },
  { keys: 'g a', description: 'Ir para Alertas' },
  { keys: 'g t', description: 'Ir para Trilhas' },
  { keys: '?', description: 'Abrir/fechar esta ajuda' },
];

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true;
  if (target.isContentEditable) return true;
  return false;
}

interface KeyboardShortcutsContextType {
  isHelpOpen: boolean;
  openHelp: () => void;
  closeHelp: () => void;
  toggleHelp: () => void;
}

const KeyboardShortcutsContext = createContext<KeyboardShortcutsContextType | undefined>(undefined);

export function KeyboardShortcutsProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  // Timestamp of the last unconsumed "g" press, or null when no chord is pending.
  const pendingGAtRef = useRef<number | null>(null);

  const openHelp = useCallback(() => setIsHelpOpen(true), []);
  const closeHelp = useCallback(() => setIsHelpOpen(false), []);
  const toggleHelp = useCallback(() => setIsHelpOpen((v) => !v), []);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (isEditableTarget(event.target)) return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;

      const key = event.key;

      // '?' always toggles help, even while a "g" chord is pending.
      if (key === '?') {
        event.preventDefault();
        pendingGAtRef.current = null;
        setIsHelpOpen((v) => !v);
        return;
      }

      if (key === 'Escape') {
        pendingGAtRef.current = null;
        setIsHelpOpen((v) => (v ? false : v));
        return;
      }

      // While the help overlay is open, don't let other keys trigger navigation.
      if (isHelpOpen) return;

      if (key.toLowerCase() === 'g') {
        pendingGAtRef.current = Date.now();
        return;
      }

      const pendingAt = pendingGAtRef.current;
      if (pendingAt != null) {
        pendingGAtRef.current = null;
        const elapsed = Date.now() - pendingAt;
        if (elapsed <= CHORD_TIMEOUT_MS) {
          const route = CHORD_ROUTES[key.toLowerCase()];
          if (route) {
            event.preventDefault();
            router.push(route);
          }
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [router, isHelpOpen]);

  return (
    <KeyboardShortcutsContext.Provider value={{ isHelpOpen, openHelp, closeHelp, toggleHelp }}>
      {children}
      {isHelpOpen && <KeyboardShortcutsHelp onClose={closeHelp} />}
    </KeyboardShortcutsContext.Provider>
  );
}

export function useKeyboardShortcuts(): KeyboardShortcutsContextType {
  const ctx = useContext(KeyboardShortcutsContext);
  if (!ctx) {
    throw new Error('useKeyboardShortcuts must be used within a KeyboardShortcutsProvider');
  }
  return ctx;
}

// ---------------------------------------------------------------------------
// Help overlay — role=dialog, Esc closes (handled above), basic focus trap.
// ---------------------------------------------------------------------------

function KeyboardShortcutsHelp({ onClose }: { onClose: () => void }) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  // Focus the dialog on open, and trap Tab within it (basic: only wraps
  // between the first and last focusable elements).
  useEffect(() => {
    closeButtonRef.current?.focus();

    function handleTabTrap(event: KeyboardEvent) {
      if (event.key !== 'Tab') return;
      const dialog = dialogRef.current;
      if (!dialog) return;

      const focusable = dialog.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      );
      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener('keydown', handleTabTrap);
    return () => document.removeEventListener('keydown', handleTabTrap);
  }, []);

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="keyboard-shortcuts-help-title"
        className="w-full max-w-sm rounded-lg bg-[var(--surface-raised)] border border-[var(--border-default)] p-5 shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h2 id="keyboard-shortcuts-help-title" className="text-sm font-semibold text-[var(--text-primary)]">
            Atalhos de teclado
          </h2>
          <button
            ref={closeButtonRef}
            type="button"
            onClick={onClose}
            aria-label="Fechar ajuda de atalhos"
            className="p-1 rounded hover:bg-[var(--surface-overlay)] text-[var(--text-secondary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)]"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>

        <ul className="space-y-2">
          {SHORTCUTS.map((shortcut) => (
            <li key={shortcut.keys} className="flex items-center justify-between gap-4 text-sm">
              <span className="text-[var(--text-secondary)]">{shortcut.description}</span>
              <kbd className="px-2 py-0.5 rounded bg-[var(--surface-overlay)] border border-[var(--border-default)] font-mono text-xs text-[var(--text-primary)] whitespace-nowrap">
                {shortcut.keys}
              </kbd>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
