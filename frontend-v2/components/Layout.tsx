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
} from 'lucide-react';
import { logout, getUser, isAdmin } from '@/lib/auth';
import { useState } from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUser();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isLoginPage = pathname === '/login' || pathname === '/register';

  if (isLoginPage) {
    return <>{children}</>;
  }

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/command-center', label: 'Command Center', icon: Activity },
    { href: '/alert-triage', label: 'Alert Triage', icon: Bell },
  ];

  const adminItems = [
    { href: '/admin', label: 'Admin', icon: Shield },
    { href: '/admin/users', label: 'Users', icon: UserCog },
    { href: '/admin/thresholds', label: 'Thresholds', icon: Sliders },
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
      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
        isActive(href)
          ? 'bg-sidebar-active text-white'
          : 'text-slate-300 hover:bg-sidebar-hover hover:text-white'
      }`}
    >
      <Icon className="w-5 h-5" />
      <span>{label}</span>
    </button>
  );

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="hidden md:flex md:w-64 md:flex-col bg-sidebar-bg">
        <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-700/50">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">Intensicare</h1>
            <p className="text-slate-400 text-xs">Clinical Command</p>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-4 mb-2">
            Clinical
          </div>
          {navItems.map((item) => (
            <NavLink key={item.href} {...item} />
          ))}

          {isAdmin() && (
            <>
              <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-4 mb-2 mt-6">
                Administration
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
                {user?.is_admin ? 'Administrator' : 'Clinician'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-sidebar-hover transition-colors"
              title="Logout"
              aria-label="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-30 bg-sidebar-bg px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 rounded-lg text-slate-300 hover:bg-sidebar-hover"
            aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <span className="text-white font-bold">Intensicare</span>
        </div>
        <button
          onClick={handleLogout}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-sidebar-hover"
          aria-label="Logout"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="md:hidden fixed inset-0 z-20" role="dialog" aria-modal="true" aria-label="Navigation menu">
          <div
            className="absolute inset-0 bg-black/50"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute left-0 top-0 bottom-0 w-64 bg-sidebar-bg pt-16 overflow-y-auto">
            <nav className="px-3 py-4 space-y-1">
              <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-4 mb-2">
                Clinical
              </div>
              {navItems.map((item) => (
                <NavLink key={item.href} {...item} />
              ))}
              {isAdmin() && (
                <>
                  <div className="text-slate-500 text-xs font-semibold uppercase tracking-wider px-4 mb-2 mt-6">
                    Administration
                  </div>
                  {adminItems.map((item) => (
                    <NavLink key={item.href} {...item} />
                  ))}
                </>
              )}
            </nav>
          </div>
        </div>
      )}

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
            aria-label="Go to dashboard"
          >
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-sm">Intensicare</span>
          </button>
          <nav className="hidden sm:flex items-center gap-1 ml-4">
            <button
              onClick={() => router.push('/dashboard')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                pathname === '/dashboard'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-500 hover:bg-slate-100'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => router.push('/command-center')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                pathname.startsWith('/command-center')
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-500 hover:bg-slate-100'
              }`}
            >
              Command Center
            </button>
            <button
              onClick={() => router.push('/alert-triage')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                pathname.startsWith('/alert-triage')
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-500 hover:bg-slate-100'
              }`}
            >
              Alert Triage
            </button>
          </nav>
        </div>
        <button
          onClick={() => {
            logout();
            router.push('/login');
          }}
          className="text-xs text-slate-500 hover:text-slate-700 transition-colors"
          aria-label="Logout"
        >
          Logout
        </button>
      </header>

      {/* Main content — full width, no sidebar */}
      <main className="flex-1">
        <div className="p-4 md:p-6 lg:p-8 max-w-[1920px] mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
