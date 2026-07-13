'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Users, SlidersHorizontal, Building2, FileClock } from 'lucide-react';
import { UserManager } from '@/components/admin/user-manager';
import { ThresholdEditor } from '@/components/admin/threshold-editor';
import { TenantConfig } from '@/components/admin/tenant-config';
import { AuditLog } from '@/components/admin/audit-log';
import { useAuth } from '@/lib/auth';
import { cn } from '@/lib/utils';

type TabId = 'users' | 'thresholds' | 'tenant' | 'audit';

interface Tab {
  id: TabId;
  label: string;
  icon: typeof Users;
}

const TABS: Tab[] = [
  { id: 'users', label: 'Usuários', icon: Users },
  { id: 'thresholds', label: 'Thresholds', icon: SlidersHorizontal },
  { id: 'tenant', label: 'Tenant', icon: Building2 },
  { id: 'audit', label: 'Auditoria', icon: FileClock },
];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<TabId>('users');
  const { user, isLoading } = useAuth();
  const router = useRouter();

  // Admin guard (AUTH-3): redirect non-admins away without flashing content.
  useEffect(() => {
    if (!isLoading && !user?.is_admin) {
      router.replace('/');
    }
  }, [isLoading, user, router]);

  if (isLoading || !user?.is_admin) {
    return null;
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Page header */}
      <div>
        <h1
          className="text-2xl font-bold mb-1"
          style={{ color: 'var(--text-primary)' }}
        >
          Administração
        </h1>
        <p
          className="text-sm"
          style={{ color: 'var(--text-secondary)' }}
        >
          Gerencie usuários, thresholds, configurações do tenant e registros de auditoria.
        </p>
      </div>

      {/* Tabs */}
      <div
        className="flex gap-1 p-1 rounded-[var(--radius-md)] self-start"
        style={{
          backgroundColor: 'var(--surface-raised)',
          borderColor: 'var(--border-default)',
          borderWidth: '1px',
          borderStyle: 'solid',
        }}
        role="tablist"
        aria-label="Seções de administração"
      >
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          const Icon = tab.icon;

          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`panel-${tab.id}`}
              id={`tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-[var(--radius-sm)] transition-all',
                'hover:opacity-80',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--severity-watch)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--surface-canvas)]',
                isActive && 'shadow-sm',
              )}
              style={{
                backgroundColor: isActive ? 'var(--surface-overlay)' : 'transparent',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
              }}
            >
              <Icon className="size-4" aria-hidden="true" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab panels */}
      <div>
        <div
          role="tabpanel"
          id="panel-users"
          aria-labelledby="tab-users"
          hidden={activeTab !== 'users'}
        >
          {activeTab === 'users' && <UserManager />}
        </div>
        <div
          role="tabpanel"
          id="panel-thresholds"
          aria-labelledby="tab-thresholds"
          hidden={activeTab !== 'thresholds'}
        >
          {activeTab === 'thresholds' && <ThresholdEditor />}
        </div>
        <div
          role="tabpanel"
          id="panel-tenant"
          aria-labelledby="tab-tenant"
          hidden={activeTab !== 'tenant'}
        >
          {activeTab === 'tenant' && <TenantConfig />}
        </div>
        <div
          role="tabpanel"
          id="panel-audit"
          aria-labelledby="tab-audit"
          hidden={activeTab !== 'audit'}
        >
          {activeTab === 'audit' && <AuditLog />}
        </div>
      </div>
    </div>
  );
}
