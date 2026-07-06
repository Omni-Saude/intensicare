'use client';

const TOKEN_KEY = 'access_token';
const USER_KEY = 'intensicare_user';

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  display_name: string | null;
  is_admin: boolean;
  is_active: boolean;
}

// --- Token management ---

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  sessionStorage.setItem(TOKEN_KEY, token);
  // Also set as cookie for middleware
  document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Lax`;
}

export function clearToken(): void {
  if (typeof window === 'undefined') return;
  sessionStorage.removeItem(TOKEN_KEY);
  document.cookie = 'access_token=; path=/; max-age=0; SameSite=Lax';
}

// --- User info ---

export function getUser(): UserInfo | null {
  if (typeof window === 'undefined') return null;
  const stored = sessionStorage.getItem(USER_KEY);
  if (!stored) return null;
  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}

export function setUser(user: UserInfo): void {
  if (typeof window === 'undefined') return;
  sessionStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearUser(): void {
  if (typeof window === 'undefined') return;
  sessionStorage.removeItem(USER_KEY);
}

// --- Auth helpers ---

export function isAuthenticated(): boolean {
  return getToken() !== null;
}

export function isAdmin(): boolean {
  const user = getUser();
  return user?.is_admin === true;
}

export function logout(): void {
  clearToken();
  clearUser();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

// --- JWT decode (for role checks) ---

export function decodeTokenPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const middle = parts[1];
    if (!middle) return null;
    const payload = JSON.parse(atob(middle));
    return payload;
  } catch {
    return null;
  }
}
