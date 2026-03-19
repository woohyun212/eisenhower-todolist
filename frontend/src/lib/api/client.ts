import type { Task, User } from '$lib/types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api/v1';

function getErrorMessage(status: number, defaultMessage: string): string {
  const messages: Record<number, string> = {
    401: '로그인이 필요합니다',
    404: '항목을 찾을 수 없습니다',
    500: '서버 오류가 발생했습니다',
  };

  return messages[status] || defaultMessage;
}

function getServerErrorMessage(errorData: unknown): string | null {
  if (!errorData || typeof errorData !== 'object') {
    return null;
  }

  const data = errorData as Record<string, unknown>;
  if (typeof data.message === 'string' && data.message.trim()) {
    return data.message;
  }
  if (typeof data.detail === 'string' && data.detail.trim()) {
    return data.detail;
  }

  return null;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' 
    ? localStorage.getItem('token') 
    : null;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch {
    throw new Error('서버에 연결할 수 없습니다');
  }
  
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    throw new Error(getErrorMessage(401, '로그인이 필요합니다'));
  }
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const serverMessage = getServerErrorMessage(errorData);
    throw new Error(
      getErrorMessage(response.status, serverMessage || `HTTP ${response.status}`)
    );
  }
  
  return response.json();
}

export const api = {
  auth: {
    register: (email: string, password: string) =>
      request<{ access_token: string; token_type: string }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    login: (email: string, password: string) =>
      request<{ access_token: string; token_type: string }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    me: () =>
      request<User>('/auth/me'),
  },
  tasks: {
    list: () =>
      request<Task[]>('/tasks'),
    create: (title: string) =>
      request<Task>('/tasks', {
        method: 'POST',
        body: JSON.stringify({ title }),
      }),
    update: (id: string, data: Partial<Task>) =>
      request<Task>(`/tasks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request<void>(`/tasks/${id}`, { method: 'DELETE' }),
  },
};
