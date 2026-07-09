'use client';

import { useRole, type ClinicalRole } from '@/hooks/useRole';

interface RequireRoleProps {
  role: ClinicalRole;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

/**
 * Componente wrapper que renderiza children apenas se o usuário
 * tem a role clínica mínima necessária.
 *
 * Usa a hierarquia de roles: admin > medico > enfermeiro > ...
 *
 * @example
 * <RequireRole role="medico" fallback={<p>Acesso restrito</p>}>
 *   <PrescriptionForm />
 * </RequireRole>
 */
export default function RequireRole({ role, fallback = null, children }: RequireRoleProps) {
  const { can } = useRole();
  if (!can(role)) return <>{fallback}</>;
  return <>{children}</>;
}
