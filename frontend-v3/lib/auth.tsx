'use client';

import type { ReactNode } from 'react';
import { createContext, useContext, useState, useCallback } from 'react';
import {
  getToken,
  setToken,
  login as apiLogin,
  logout as apiLogout,
  type UserInfo,
} from './api';

// Decodes the (in-memory only, non-persisted) token synchronously to build
// the initial auth state. Safe to call during render/SSR: getToken() reads a
// plain in-module variable (never localStorage), so it is always `null` on a
// fresh module instance and only becomes non-null after an explicit login()
// call later in the same client session.
function initialAuthState(): AuthState {
  const token = getToken();
  if (!token) {
    return { user: null, isLoading: false, isAuthenticated: false };
  }

  // Decode JWT payload to get user info without an extra network call
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const user: UserInfo = {
      id: payload.sub || '',
      name: payload.name || '',
      email: payload.email || '',
      role: payload.role || 'viewer',
      is_admin: payload.is_admin === true,
    };
    return { user, isLoading: false, isAuthenticated: true };
  } catch {
    // Invalid token format — keep default (unauthenticated) state
    return { user: null, isLoading: false, isAuthenticated: false };
  }
}

// ---------- types ----------

interface AuthState {
  user: UserInfo | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

// ---------- context ----------

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ---------- provider ----------

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>(initialAuthState);

  const login = useCallback(async (username: string, password: string) => {
    const response = await apiLogin(username, password);
    setToken(response.access_token);
    setState({
      user: response.user,
      isLoading: false,
      isAuthenticated: true,
    });
  }, []);

  const logout = useCallback(() => {
    apiLogout();
    setState({ user: null, isLoading: false, isAuthenticated: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// ---------- hook ----------

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
