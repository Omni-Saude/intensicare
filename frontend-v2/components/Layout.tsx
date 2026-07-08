'use client';

import React from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  Activity,
  Bell,
  UserCog,
  Shield,
  Sliders,
  LogOut,
  Menu,
  X,
  HelpCircle,
  Heart,
  Pill,
  ClipboardCheck,
  Scale,
  Droplets,
  MessageSquare,
  Building2,
} from 'lucide-react';
import { logout, getUser, isAdmin } from '@/lib/auth';
import { useState } from 'react';
import DrawerBuilder from '@/components/DrawerBuilder';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUser();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  // Global keyboard shortcut: ? → open help
  useKeyboardShortcuts([
    {
      key: '?',
      handler: () => setHelpOpen((prev) => !prev),
    },
  ]);

  const isLoginPage = pathname === '/login' || pathname === '/register';

  if (isLoginPage) {
    return <>{children}</>;
  }

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const navItems = [
    { href: '/dashboard', label: 'Painel', icon: LayoutDashboard },
    { href: '/command-center', label: 'Central de Comando', icon: Activity },
    { href: '/alert-triage', label: 'Triagem de Alertas', icon: Bell },
    { href: '/sepse-dashboard', label: 'Sepse', icon: Heart },
    { href: '/antimicrobial-stewardship', label: 'Antimicrobiano', icon: Pill },
    { href: '/prophylaxis-bundles', label: 'Profilaxia', icon: ClipboardCheck },
    { href: '/nutrition', label: 'Nutrição', icon: Scale },
    { href: '/fluid-balance', label: 'Balanço Hídrico', icon: Droplets },
    { href: '/communication', label: 'Comunicação', icon: MessageSquare },
  ];

  const adminItems = [
    { href: '/admin', label: 'Administração', icon: Shield },
    { href: '/admin/users', label: 'Usuários', icon: UserCog },
    { href: '/admin/thresholds', label: 'Limiares', icon: Sliders },
    { href: '/admin/tenancy', label: 'Organizações', icon: Building2 },
    { href: '/admin/audit-log', label: 'Auditoria', icon: Shield },
  ];

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  const NavLink = ({
    href,
    label,
    icon: Icon,
  }: {
    href: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
  }) => (
    <button
      onClick={() => {
        router.push(href);
        setSidebarOpen(false);
      }}
      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none border-l-4 border-transparent ${
        isActive(href)
          ? 'bg-sidebar-active text-white border-l-[var(--clinical-severity-normal-signal)]'
          : 'text-slate-300 hover:bg-sidebar-hover hover:text-white hover:border-l-[var(--clinical-severity-normal-signal)]'
      }`}
    >
      <Icon className="w-5 h-5" aria-hidden="true" />
      <span>{label}</span>
    </button>
  );

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="hidden md:flex md:w-64 md:flex-col bg-sidebar-bg">
        <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-700/50">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center">
            <Activity className="w-5 h-5 text-white" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">Intensicare</h1>
            <p className="text-slate-400 text-xs">Comando Clínico</p>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-4 mb-2">
            Clínico
          </div>
          {navItems.map((item) => (
            <NavLink key={item.href} {...item} />
          ))}

          {isAdmin() && (
            <>
              <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-4 mb-2 mt-6">
                Administração
              </div>
              {adminItems.map((item) => (
                <NavLink key={item.href} {...item} />
              ))}
            </>
          )}
        </nav>

        {/* User footer */}
        <div className="border-t border-slate-700/50 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user?.display_name || user?.username || 'User'}
              </p>
              <p className="text-xs text-slate-400 truncate">
                {user?.is_admin ? 'Administrador' : 'Clínico'}
              </p>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setHelpOpen(true)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-sidebar-hover transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                title="Ajuda (?)"
                aria-label="Ajuda"
              >
                <HelpCircle className="w-4 h-4" aria-hidden="true" />
              </button>
              <button
                onClick={handleLogout}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-sidebar-hover transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
                title="Sair"
                aria-label="Sair"
              >
                <LogOut className="w-4 h-4" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-30 bg-sidebar-bg px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 rounded-lg text-slate-300 hover:bg-sidebar-hover min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
          >
            {sidebarOpen ? <X className="w-5 h-5" aria-hidden="true" /> : <Menu className="w-5 h-5" aria-hidden="true" />}
          </button>
          <span className="text-white font-bold">Intensicare</span>
        </div>
        <button
          onClick={handleLogout}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-sidebar-hover min-h-[44px] min-w-[44px] flex items-center justify-center"
          aria-label="Sair"
        >
          <LogOut className="w-4 h-4" aria-hidden="true" />
        </button>
      </div>

      {/* Mobile sidebar overlay */}
      <DrawerBuilder open={sidebarOpen} onClose={() => setSidebarOpen(false)} size="full">
        <div className="absolute left-0 top-0 bottom-0 w-64 bg-sidebar-bg pt-16 overflow-y-auto">
          <nav className="px-3 py-4 space-y-1">
            <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-4 mb-2">
              Clínico
            </div>
            {navItems.map((item) => (
              <NavLink key={item.href} {...item} />
            ))}
            {isAdmin() && (
              <>
                <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-4 mb-2 mt-6">
                  Administração
                </div>
                {adminItems.map((item) => (
                  <NavLink key={item.href} {...item} />
                ))}
              </>
            )}
          </nav>
        </div>
      </DrawerBuilder>

      {/* Help Drawer */}
      <DrawerBuilder open={helpOpen} onClose={() => setHelpOpen(false)} title="Ajuda" size="md">
        <div className="space-y-4 text-sm" style={{ color: 'var(--semantic-text-primary)' }}>
          <div>
            <h3 className="font-semibold mb-2">Atalhos de Teclado</h3>
            <ul className="space-y-1 text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">?</kbd> — Abrir/fechar ajuda</li>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">/</kbd> — Focar busca</li>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">1-4</kbd> — Filtrar por gravidade (Central de Comando)</li>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">Esc</kbd> — Limpar filtros</li>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">j/k</kbd> ou <kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">↓/↑</kbd> — Navegar lista</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Sobre o Intensicare</h3>
            <p className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
              Intensicare v0.1.0 — Sistema de Suporte à Decisão Clínica para UTI.
              Monitoramento contínuo, alertas inteligentes e passagem de plantão estruturada.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Documentação</h3>
            <p className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
              Consulte a documentação completa em{' '}
              <a href="#" className="underline text-blue-600 hover:text-blue-800">
                docs.intensicare.local
              </a>
            </p>
          </div>
        </div>
      </DrawerBuilder>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto pt-16 md:pt-0">
        <div className="p-4 md:p-6 lg:p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}

// FullScreenLayout: no sidebar, no persistent side nav — per command-center spec
export function FullScreenLayout({ children }: LayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const isLoginPage = pathname === '/login' || pathname === '/register';
  const [helpOpen, setHelpOpen] = useState(false);

  // Global keyboard shortcut: ? → open help
  useKeyboardShortcuts([
    {
      key: '?',
      handler: () => setHelpOpen((prev) => !prev),
    },
  ]);

  if (isLoginPage) {
    return <>{children}</>;
  }

  return (
    <div className="flex flex-col min-h-screen">
      {/* Minimal top bar — no persistent side nav */}
      <header
        style={{ borderColor: 'var(--semantic-border-default)' }}
        className="sticky top-0 z-20 bg-white border-b px-4 py-3 flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push('/dashboard')}
            className="flex items-center gap-2 text-slate-800 hover:text-blue-600 transition-colors"
            aria-label="Ir para o painel"
          >
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" aria-hidden="true" />
            </div>
            <span className="font-bold text-sm">Intensicare</span>
          </button>
          <nav className="hidden sm:flex items-center gap-1 ml-4">
            <button
              onClick={() => router.push('/dashboard')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                pathname === '/dashboard'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-500 hover:bg-slate-100'
              }`}
            >
              Painel
            </button>
            <button
              onClick={() => router.push('/command-center')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                pathname.startsWith('/command-center')
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-500 hover:bg-slate-100'
              }`}
            >
              Central de Comando
            </button>
            <button
              onClick={() => router.push('/alert-triage')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none ${
                pathname.startsWith('/alert-triage')
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-500 hover:bg-slate-100'
              }`}
            >
              Triagem de Alertas
            </button>
          </nav>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setHelpOpen(true)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
            aria-label="Ajuda"
            title="Ajuda (?)"
          >
            <HelpCircle className="w-4 h-4" aria-hidden="true" />
          </button>
          <button
            onClick={() => {
              logout();
              router.push('/login');
            }}
            className="text-xs text-slate-500 hover:text-slate-700 transition-colors"
            aria-label="Sair"
          >
            Sair
          </button>
        </div>
      </header>

      {/* Main content — full width, no sidebar */}
      <main className="flex-1">
        <div className="p-4 md:p-6 lg:p-8 max-w-[1920px] mx-auto">
          {children}
        </div>
      </main>

      {/* Help Drawer */}
      <DrawerBuilder open={helpOpen} onClose={() => setHelpOpen(false)} title="Ajuda" size="md">
        <div className="space-y-4 text-sm" style={{ color: 'var(--semantic-text-primary)' }}>
          <div>
            <h3 className="font-semibold mb-2">Atalhos de Teclado</h3>
            <ul className="space-y-1 text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">?</kbd> — Abrir/fechar ajuda</li>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">/</kbd> — Focar busca</li>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">1-4</kbd> — Filtrar por gravidade (Central de Comando)</li>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">Esc</kbd> — Limpar filtros</li>
              <li><kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">j/k</kbd> ou <kbd className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-xs">↓/↑</kbd> — Navegar lista</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Sobre o Intensicare</h3>
            <p className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
              Intensicare v0.1.0 — Sistema de Suporte à Decisão Clínica para UTI.
              Monitoramento contínuo, alertas inteligentes e passagem de plantão estruturada.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Documentação</h3>
            <p className="text-xs" style={{ color: 'var(--semantic-text-secondary)' }}>
              Consulte a documentação completa em{' '}
              <a href="#" className="underline text-blue-600 hover:text-blue-800">
                docs.intensicare.local
              </a>
            </p>
          </div>
        </div>
      </DrawerBuilder>
    </div>
  );
}
