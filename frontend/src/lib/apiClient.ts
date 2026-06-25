import { useCallback } from 'react';
import { useMember } from '@/integrations/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/v1';

export class ApiError extends Error {
  status: number;
  data: any;
  
  constructor(message: string, status: number, data: any) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

export function useApiClient() {
  const { actions, isAuthenticated } = useMember();

  const fetchApi = useCallback(async <T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    // MemberProvider controls the single source of truth for the token.
    // It saves it to localStorage, so we read it from there here for the actual network request.
    const token = localStorage.getItem('access_token');
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // Check for 401 Unauthorized - might need token refresh
    if (response.status === 401 && token) {
      // The AuthProvider handles refresh logic. If we get a 401 here on a random request,
      // we could try to call loadCurrentMember() to trigger a refresh and state update.
      actions.loadCurrentMember();
    }

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = await response.text();
      }
      throw new ApiError(
        errorData?.detail || errorData?.message || 'API request failed',
        response.status,
        errorData
      );
    }

    // Some endpoints (like export) might not return JSON. Handle if necessary,
    // but default to JSON for standard API calls.
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }
    
    return response.text() as unknown as T;
  }, [actions]);

  return { fetchApi, API_URL };
}

// Global helper for outside-React contexts if strictly needed.
// Uses the localStorage token managed by MemberProvider.
export async function fetchApi<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = await response.text();
    }
    throw new ApiError(
      errorData?.detail || errorData?.message || 'API request failed',
      response.status,
      errorData
    );
  }

  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return response.json();
  }
  return response.text() as unknown as T;
}
