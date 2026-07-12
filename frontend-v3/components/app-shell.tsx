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
import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useConnectionStatus } from '@/lib/websocket';
import { cn } from '@/lib/utils';
import { Logo } from '@/components/brand/logo';

const NAV_ITEMS = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/alerts', label: 'Alertas', icon: Bell },
  { href: '/pathways', label: 'Trilhas', icon: GitBranch },
  { href: '/admin', label: 'Admin', icon: Shield },
];

function Breadcrumb() {
  const pathname = usePathname();
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
    const label = seg.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    return { href, label, isLast: i === segments.length - 1 };
  });

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-sm text-[var(--text-secondary)]">
      <Link href="/" className="hover:text-[var(--text-primary)] transition-colors">
        <Home className="h-3.5 w-3.5" />
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

export function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [confirmLogout, setConfirmLogout] = useState(false);
  const pathname = usePathname();
  const { isAuthenticated, user, logout } = useAuth();
  const { status: connStatus } = useConnectionStatus();

  // Don't render sidebar on login page
  if (pathname === '/login') {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside
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
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded hover:bg-[var(--surface-overlay)]"
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

        {/* User section */}
        {isAuthenticated && user && (
          <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-[var(--border-default)]">
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
                    className="text-xs px-2 py-1 rounded bg-[var(--severity-critical)] text-white font-medium hover:opacity-90 transition-opacity"
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
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden mr-3 p-1 rounded hover:bg-[var(--surface-overlay)]"
            aria-label="Abrir menu"
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
        <main id="main-content" tabIndex={-1} className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
