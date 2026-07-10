'use client';

import type { ReactNode } from 'react';
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  getToken,
  setToken,
  login as apiLogin,
  logout as apiLogout,
  type UserInfo,
} from './api';

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
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });

  // On mount, check if we have a token and try to validate it
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setState({ user: null, isLoading: false, isAuthenticated: false });
      return;
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
      setState({ user, isLoading: false, isAuthenticated: true });
    } catch {
      // Invalid token format
      setState({ user: null, isLoading: false, isAuthenticated: false });
    }
  }, []);

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
