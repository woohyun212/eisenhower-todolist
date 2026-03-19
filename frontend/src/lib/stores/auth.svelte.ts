import { api } from '$lib/api/client';
import type { User } from '$lib/types';

let token = $state<string | null>(
  typeof window !== 'undefined' ? localStorage.getItem('token') : null
);
let user = $state<User | null>(null);
let isAuthenticated = $derived(!!token);
let error = $state<string | null>(null);

// Initialize auth on app load
if (typeof window !== 'undefined' && token) {
  api.auth.me()
    .then(userData => {
      user = userData;
    })
    .catch(() => {
      token = null;
      localStorage.removeItem('token');
    });
}

export async function login(email: string, password: string): Promise<boolean> {
  error = null;
  try {
    const data = await api.auth.login(email, password);
    token = data.access_token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
    user = await api.auth.me();
    return true;
  } catch (err) {
    error = err instanceof Error ? err.message : '로그인에 실패했습니다';
    return false;
  }
}

export async function register(email: string, password: string): Promise<boolean> {
  error = null;
  try {
    const data = await api.auth.register(email, password);
    token = data.access_token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
    user = await api.auth.me();
    return true;
  } catch (err) {
    error = err instanceof Error ? err.message : '회원가입에 실패했습니다';
    return false;
  }
}

export async function logout(): Promise<void> {
  token = null;
  user = null;
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
  }
}

export function getToken(): string | null {
  return token;
}

export function getUser() {
  return user;
}

export function getError(): string | null {
  return error;
}

export function isAuth(): boolean {
  return isAuthenticated;
}
