'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import {
  LayoutDashboard,
  Bell,
  GitBranch,
  Shield,
  Menu,
  X,
  ChevronRight,
  Home,
  Wifi,
  WifiOff,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useConnectionStatus } from '@/lib/websocket';
import { cn } from '@/lib/utils';
import { Logo } from '@/components/brand/logo';
import { BreadcrumbProvider, useBreadcrumbLabels } from '@/lib/breadcrumb-context';
import { KeyboardShortcutsProvider, useKeyboardShortcuts } from '@/lib/keyboard-shortcuts';

const NAV_ITEMS = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/alerts', label: 'Alertas', icon: Bell },
  { href: '/pathways', label: 'Trilhas', icon: GitBranch },
  { href: '/admin', label: 'Admin', icon: Shield },
];

// Fixed PT-BR labels for static (non-dynamic) URL segments. Segments not
// listed here (e.g. IDs) fall back to the title-cased slug, or to a
// registered label from BreadcrumbContext when available.
const STATIC_SEGMENT_LABELS: Record<string, string> = {
  patient: 'Paciente',
  pathway: 'Trilha',
  pathways: 'Trilhas',
  alerts: 'Alertas',
  admin: 'Admin',
};

function Breadcrumb() {
  const pathname = usePathname();
  const { labels } = useBreadcrumbLabels();
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length === 0) {
    return (
      <div className="flex items-center gap-1 text-sm text-[var(--text-secondary)]">
        <Home className="h-3.5 w-3.5" />
        <span className="text-[var(--text-primary)]">Dashboard</span>
      </div>
    );
  }

  const crumbs = segments.map((seg, i) => {
    const href = '/' + segments.slice(0, i + 1).join('/');
    const fallback =
      STATIC_SEGMENT_LABELS[seg] ?? seg.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    const label = labels[seg] ?? fallback;
    return { href, label, isLast: i === segments.length - 1 };
  });

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm text-[var(--text-secondary)]">
      <Link href="/" className="hover:text-[var(--text-primary)] transition-colors" aria-label="Início">
        <Home className="h-3.5 w-3.5" aria-hidden="true" />
      </Link>
      {crumbs.map((crumb) => (
        <span key={crumb.href} className="flex items-center gap-1">
          <ChevronRight className="h-3 w-3" />
          {crumb.isLast ? (
            <span className="text-[var(--text-primary)] font-medium">{crumb.label}</span>
          ) : (
            <Link
              href={crumb.href}
              className="hover:text-[var(--text-primary)] transition-colors"
            >
              {crumb.label}
            </Link>
          )}
        </span>
      ))}
    </nav>
  );
}

// Discreet sidebar-footer hint that opens the keyboard shortcuts help
// overlay. Rendered as a descendant of KeyboardShortcutsProvider so it can
// consume the shared open/close state.
function ShortcutsHint() {
  const { openHelp } = useKeyboardShortcuts();

  return (
    <button
      type="button"
      onClick={openHelp}
      className="flex w-full items-center gap-1.5 px-3 py-2 text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      aria-label="Ver atalhos de teclado"
    >
      <kbd className="px-1.5 py-0.5 rounded border border-[var(--border-default)] bg-[var(--surface-overlay)] font-mono text-2xs">
        ?
      </kbd>
      atalhos
    </button>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [confirmLogout, setConfirmLogout] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated, user, logout } = useAuth();
  const { status: connStatus } = useConnectionStatus();

  // Mobile drawer focus trap — pattern copied from KeyboardShortcutsHelp
  // (lib/keyboard-shortcuts.tsx) / CreateUserDialog (admin/user-manager.tsx):
  // Esc closes, Tab cycles within the drawer while open, and focus returns
  // to the trigger (hamburger) button on close. On large screens the same
  // <aside> renders as a persistent, non-modal sidebar (lg:relative
  // lg:translate-x-0) — the trap and aria-modal/role="dialog" only kick in
  // while `sidebarOpen` is true, which only happens via the hamburger
  // button that is itself hidden at lg (`lg:hidden`), so desktop navigation
  // is never affected.
  const sidebarRef = useRef<HTMLElement>(null);
  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const wasSidebarOpenRef = useRef(false);

  useEffect(() => {
    if (!sidebarOpen) {
      // Drawer just closed — return focus to whatever opened it.
      if (wasSidebarOpenRef.current) {
        menuButtonRef.current?.focus();
      }
      wasSidebarOpenRef.current = false;
      return;
    }
    wasSidebarOpenRef.current = true;

    closeButtonRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        event.preventDefault();
        setSidebarOpen(false);
        return;
      }
      if (event.key !== 'Tab') return;
      const container = sidebarRef.current;
      if (!container) return;

      const focusable = container.querySelectorAll<HTMLElement>(
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

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [sidebarOpen]);

  // Don't render sidebar on login page, but keep shortcuts active (e.g. so
  // typing "g" while focused on the login form correctly does nothing).
  if (pathname === '/login') {
    return (
      <KeyboardShortcutsProvider>
        {children}
      </KeyboardShortcutsProvider>
    );
  }

  return (
    <KeyboardShortcutsProvider>
    <BreadcrumbProvider>
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside
        ref={sidebarRef}
        id="app-sidebar"
        role={sidebarOpen ? 'dialog' : undefined}
        aria-modal={sidebarOpen ? 'true' : undefined}
        aria-label={sidebarOpen ? 'Menu de navegação' : undefined}
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-[var(--surface-raised)] border-r border-[var(--border-default)]',
          'transform transition-transform duration-200 ease-in-out',
          'lg:relative lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-[var(--border-default)]">
          <Link href="/" className="flex items-center gap-2" aria-label="IntensiCare — Dashboard">
            <Logo variant="full" theme="dark" className="h-8 w-auto" />
          </Link>
          <button
            ref={closeButtonRef}
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2.5 rounded hover:bg-[var(--surface-overlay)]"
            aria-label="Fechar menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1 p-3">
          {NAV_ITEMS.map((item) => {
            const isActive = item.href === '/'
              ? pathname === '/'
              : pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-[var(--surface-overlay)] text-[var(--text-primary)]'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-overlay)]',
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Footer: keyboard-shortcuts hint + user section */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-[var(--border-default)]">
          <ShortcutsHint />

          {isAuthenticated && user && (
            <div className="p-3 border-t border-[var(--border-default)]">
              <div className="flex items-center justify-between">
                <div className="text-sm">
                  <p className="font-medium text-[var(--text-primary)] truncate max-w-[150px]">
                    {user.name}
                  </p>
                  <p className="text-xs text-[var(--text-secondary)]">{user.role}</p>
                </div>
                {confirmLogout ? (
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => { logout(); setConfirmLogout(false); }}
                      className="text-xs px-2 py-1 rounded bg-[var(--severity-critical)] text-[var(--surface-canvas)] font-medium hover:opacity-90 transition-opacity"
                      aria-label="Confirmar saída"
                    >
                      Sair
                    </button>
                    <button
                      onClick={() => setConfirmLogout(false)}
                      className="text-xs px-2 py-1 rounded border border-[var(--border-default)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
                      aria-label="Cancelar saída"
                    >
                      Cancelar
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setConfirmLogout(true)}
                    className="text-xs text-[var(--text-secondary)] hover:text-[var(--severity-critical)] transition-colors"
                    aria-label="Sair do sistema"
                  >
                    Sair
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          role="button"
          tabIndex={0}
          aria-label="Fechar menu lateral"
          onClick={() => setSidebarOpen(false)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
              e.preventDefault();
              setSidebarOpen(false);
            }
          }}
        />
      )}

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center h-16 px-4 border-b border-[var(--border-default)] bg-[var(--surface-canvas)]">
          <button
            ref={menuButtonRef}
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden mr-3 p-2.5 rounded hover:bg-[var(--surface-overlay)]"
            aria-label="Abrir menu"
            aria-expanded={sidebarOpen}
            aria-controls="app-sidebar"
          >
            <Menu className="h-5 w-5" />
          </button>
          <Breadcrumb />
          {/* Connection status indicator (ADR-0034) */}
          <div className="ml-auto flex items-center" title={
            connStatus === 'connected' ? 'WebSocket conectado' :
            connStatus === 'fallback' ? 'Modo polling (WebSocket indisponível)' :
            'Desconectado'
          }>
            {connStatus === 'connected' && <Wifi className="h-4 w-4 text-[var(--severity-normal)]" aria-label="Conectado" />}
            {connStatus === 'fallback' && <WifiOff className="h-4 w-4 text-[var(--severity-watch)]" aria-label="Modo polling" />}
            {connStatus === 'disconnected' && <WifiOff className="h-4 w-4 text-[var(--severity-critical)]" aria-label="Desconectado" />}
          </div>
        </header>

        {/* Page content */}
        <main id="main-content" tabIndex={-1} className="flex-1 overflow-auto p-4 sm:p-6">
          {children}
        </main>
      </div>
    </div>
    </BreadcrumbProvider>
    </KeyboardShortcutsProvider>
  );
}
