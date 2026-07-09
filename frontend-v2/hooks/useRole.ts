'use client';

import { useState, useMemo, useEffect } from 'react';
import { getUser } from '@/lib/auth';

export type ClinicalRole = 'medico' | 'enfermeiro' | 'fisioterapeuta' | 'farmacia' | 'nutricao' | 'admin' | 'readonly';

const ROLE_HIERARCHY: Record<ClinicalRole, number> = {
  admin: 100,
  medico: 80,
  enfermeiro: 70,
  fisioterapeuta: 60,
  farmacia: 50,
  nutricao: 40,
  readonly: 10,
};

export const ROLE_LABELS: Record<ClinicalRole, string> = {
  admin: 'Administrador',
  medico: 'Médico',
  enfermeiro: 'Enfermeiro',
  fisioterapeuta: 'Fisioterapeuta',
  farmacia: 'Farmácia',
  nutricao: 'Nutrição',
  readonly: 'Somente Leitura',
};

export const ALL_ROLES: ClinicalRole[] = ['admin', 'medico', 'enfermeiro', 'fisioterapeuta', 'farmacia', 'nutricao', 'readonly'];

/**
 * Hook que retorna a role clínica do usuário atual e funções de verificação.
 *
 * Lê o campo `role` do `UserInfo` armazenado em memória após login.
 */
export function useRole(): {
  role: ClinicalRole | null;
  isAdmin: boolean;
  can: (requiredRole: ClinicalRole) => boolean;
} {
  const [user, setUser] = useState(() => getUser());

  // Re-read on mount (catches login/logout across SPA navigations)
  useEffect(() => {
    const id = setInterval(() => {
      const current = getUser();
      setUser((prev) => (prev?.id !== current?.id || prev?.role !== current?.role ? current : prev));
    }, 500);
    return () => clearInterval(id);
  }, []);

  return useMemo(() => ({
    role: user?.role ?? null,
    isAdmin: user?.role === 'admin' || user?.is_admin === true,
    can: (required: ClinicalRole) => {
      const currentRole = user?.role ?? null;
      if (!currentRole) return false;
      return (ROLE_HIERARCHY[currentRole] || 0) >= (ROLE_HIERARCHY[required] || 0);
    },
  }), [user]);
}
