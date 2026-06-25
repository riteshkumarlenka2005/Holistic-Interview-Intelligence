import React, { useState, useEffect, useCallback, ReactNode } from 'react';
import { MemberContext } from './AuthContext';
import {
  Member,
  MemberState,
  MemberActions,
  LoginCredentials,
  RegisterCredentials,
  OTPVerification,
  AuthResponse,
  TokenResponse
} from './types';

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const MEMBER_STORAGE_KEY = 'member-store';

// API Base URL  
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/v1';

interface MemberProviderProps {
  children: ReactNode;
}

// API Helper
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data?: T; error?: string }> {
  try {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
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

    const data = await response.json();

    if (!response.ok) {
      return { error: data.detail || 'An error occurred' };
    }

    return { data };
  } catch (error) {
    console.error('API Error:', error);
    return { error: 'Network error. Please check your connection.' };
  }
}

export const MemberProvider: React.FC<MemberProviderProps> = ({ children }) => {
  const [state, setState] = useState<MemberState>(() => {
    let storedMemberData: Member | null = null;
    let hasToken = false;

    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem(MEMBER_STORAGE_KEY);
        const token = localStorage.getItem(ACCESS_TOKEN_KEY);
        if (stored) {
          storedMemberData = JSON.parse(stored);
        }
        hasToken = !!token;
      } catch (error) {
        console.error('Error loading member state from localStorage:', error);
      }
    }

    return {
      member: storedMemberData,
      isAuthenticated: !!storedMemberData && hasToken,
      isLoading: false,
      error: null,
      pendingVerification: false,
      pendingEmail: null,
    };
  });

  // Persist member to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined' && state.member) {
      try {
        localStorage.setItem(MEMBER_STORAGE_KEY, JSON.stringify(state.member));
      } catch (error) {
        console.error('Error saving member state to localStorage:', error);
      }
    }
  }, [state.member]);

  const updateState = useCallback((updates: Partial<MemberState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const saveTokens = useCallback((tokens: TokenResponse) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  }, []);

  const clearTokens = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(MEMBER_STORAGE_KEY);
  }, []);

  const transformUser = useCallback((user: any): Member => {
    return {
      id: user.id,
      email: user.email,
      firstName: user.first_name,
      lastName: user.last_name,
      avatar: user.avatar_url,
      isVerified: user.is_verified,
      oauthProvider: user.oauth_provider,
      createdAt: new Date(user.created_at),
      updatedAt: new Date(),
      profile: {
        nickname: user.first_name || user.email?.split('@')[0] || 'User',
      },
    };
  }, []);

  const actions: MemberActions = {
    loadCurrentMember: useCallback(async () => {
      const token = localStorage.getItem(ACCESS_TOKEN_KEY);
      if (!token) {
        updateState({
          member: null,
          isAuthenticated: false,
          isLoading: false,
        });
        return;
      }

      try {
        updateState({ isLoading: true, error: null });

        const { data, error } = await apiRequest<any>('/auth/me');

        if (error || !data) {
          // Token might be expired, try refresh
          const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
          if (refreshToken) {
            const refreshResult = await apiRequest<TokenResponse>('/auth/refresh', {
              method: 'POST',
              body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (refreshResult.data) {
              saveTokens(refreshResult.data);
              // Retry getting user
              const retryResult = await apiRequest<any>('/auth/me');
              if (retryResult.data) {
                const member = transformUser(retryResult.data);
                updateState({
                  member,
                  isAuthenticated: true,
                  isLoading: false,
                });
                return;
              }
            }
          }

          clearTokens();
          updateState({
            member: null,
            isAuthenticated: false,
            isLoading: false,
          });
          return;
        }

        const member = transformUser(data);
        updateState({
          member,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch (err) {
        clearTokens();
        updateState({
          error: err instanceof Error ? err.message : 'Failed to load member',
          member: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    }, [updateState, saveTokens, clearTokens, transformUser]),

    login: useCallback(() => {
      window.location.href = '/login';
    }, []),

    loginWithCredentials: useCallback(async (credentials: LoginCredentials): Promise<boolean> => {
      try {
        updateState({ isLoading: true, error: null });

        const { data, error } = await apiRequest<AuthResponse>('/auth/login', {
          method: 'POST',
          body: JSON.stringify({
            email: credentials.email,
            password: credentials.password,
          }),
        });

        if (error) {
          // Check if it's a verification required error
          if (error.includes('not verified')) {
            updateState({
              error: null,
              isLoading: false,
              pendingVerification: true,
              pendingEmail: credentials.email,
            });
            return false;
          }

          updateState({
            error,
            isLoading: false,
          });
          return false;
        }

        if (data) {
          saveTokens(data.tokens);
          const member = transformUser(data.user);
          updateState({
            member,
            isAuthenticated: true,
            isLoading: false,
            error: null,
            pendingVerification: false,
            pendingEmail: null,
          });
          return true;
        }

        return false;
      } catch (err) {
        updateState({
          error: err instanceof Error ? err.message : 'Login failed',
          isLoading: false,
        });
        return false;
      }
    }, [updateState, saveTokens, transformUser]),

    loginWithGoogle: useCallback(() => {
      window.location.href = `${API_URL}/auth/google`;
    }, []),

    loginWithGitHub: useCallback(() => {
      window.location.href = `${API_URL}/auth/github`;
    }, []),

    register: useCallback(async (credentials: RegisterCredentials): Promise<boolean> => {
      try {
        updateState({ isLoading: true, error: null });

        const { data, error } = await apiRequest<{ message: string }>('/auth/register', {
          method: 'POST',
          body: JSON.stringify({
            email: credentials.email,
            password: credentials.password,
            first_name: credentials.firstName,
            last_name: credentials.lastName,
          }),
        });

        if (error) {
          updateState({
            error,
            isLoading: false,
          });
          return false;
        }

        // Registration successful, need OTP verification
        updateState({
          isLoading: false,
          pendingVerification: true,
          pendingEmail: credentials.email,
          error: null,
        });

        return true;
      } catch (err) {
        updateState({
          error: err instanceof Error ? err.message : 'Registration failed',
          isLoading: false,
        });
        return false;
      }
    }, [updateState]),

    verifyOTP: useCallback(async (verification: OTPVerification): Promise<boolean> => {
      try {
        updateState({ isLoading: true, error: null });

        const { data, error } = await apiRequest<AuthResponse>('/auth/verify-email', {
          method: 'POST',
          body: JSON.stringify({
            email: verification.email,
            code: verification.code,
          }),
        });

        if (error) {
          updateState({
            error,
            isLoading: false,
          });
          return false;
        }

        if (data) {
          saveTokens(data.tokens);
          const member = transformUser(data.user);
          updateState({
            member,
            isAuthenticated: true,
            isLoading: false,
            pendingVerification: false,
            pendingEmail: null,
            error: null,
          });
          return true;
        }

        return false;
      } catch (err) {
        updateState({
          error: err instanceof Error ? err.message : 'Verification failed',
          isLoading: false,
        });
        return false;
      }
    }, [updateState, saveTokens, transformUser]),

    resendOTP: useCallback(async (email: string): Promise<boolean> => {
      try {
        updateState({ isLoading: true, error: null });

        const { error } = await apiRequest<{ message: string }>('/auth/resend-otp', {
          method: 'POST',
          body: JSON.stringify({ email }),
        });

        if (error) {
          updateState({
            error,
            isLoading: false,
          });
          return false;
        }

        updateState({ isLoading: false });
        return true;
      } catch (err) {
        updateState({
          error: err instanceof Error ? err.message : 'Failed to resend OTP',
          isLoading: false,
        });
        return false;
      }
    }, [updateState]),

    forgotPassword: useCallback(async (email: string): Promise<boolean> => {
      try {
        updateState({ isLoading: true, error: null });

        const { error } = await apiRequest<{ message: string }>('/auth/forgot-password', {
          method: 'POST',
          body: JSON.stringify({ email }),
        });

        if (error) {
          updateState({
            error,
            isLoading: false,
          });
          return false;
        }

        updateState({ isLoading: false });
        return true;
      } catch (err) {
        updateState({
          error: err instanceof Error ? err.message : 'Failed to send reset email',
          isLoading: false,
        });
        return false;
      }
    }, [updateState]),

    resetPassword: useCallback(async (email: string, code: string, newPassword: string): Promise<boolean> => {
      try {
        updateState({ isLoading: true, error: null });

        const { error } = await apiRequest<{ message: string }>('/auth/reset-password', {
          method: 'POST',
          body: JSON.stringify({
            email,
            code,
            new_password: newPassword,
          }),
        });

        if (error) {
          updateState({
            error,
            isLoading: false,
          });
          return false;
        }

        updateState({ isLoading: false });
        return true;
      } catch (err) {
        updateState({
          error: err instanceof Error ? err.message : 'Failed to reset password',
          isLoading: false,
        });
        return false;
      }
    }, [updateState]),

    logout: useCallback(async () => {
      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
        if (refreshToken) {
          await apiRequest('/auth/logout', {
            method: 'POST',
            body: JSON.stringify({ refresh_token: refreshToken }),
          });
        }
      } catch (error) {
        console.error('Logout error:', error);
      }

      clearTokens();
      updateState({
        member: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        pendingVerification: false,
        pendingEmail: null,
      });

      window.location.href = '/';
    }, [updateState, clearTokens]),

    clearMember: useCallback(() => {
      updateState({
        member: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        pendingVerification: false,
        pendingEmail: null,
      });
    }, [updateState]),

    clearError: useCallback(() => {
      updateState({ error: null });
    }, [updateState]),
  };

  // Check for OAuth callback tokens on mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    if (accessToken && refreshToken) {
      // Save tokens from OAuth callback
      saveTokens({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'bearer',
        expires_in: 1800,
      });

      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);

      // Load user
      actions.loadCurrentMember();
    } else if (localStorage.getItem(ACCESS_TOKEN_KEY)) {
      // Load existing user
      actions.loadCurrentMember();
    }
  }, []);

  const contextValue = {
    ...state,
    actions,
  };

  return (
    <MemberContext.Provider value={contextValue}>
      {children}
    </MemberContext.Provider>
  );
};
