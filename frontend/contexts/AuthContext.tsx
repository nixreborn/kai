/**
 * Authentication context provider
 */

'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AuthContextType, AuthState, UserResponse } from '@/lib/types/auth';
import * as authAPI from '@/lib/api/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'kai-auth-token';
const USER_KEY = 'kai-auth-user';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Load auth state from localStorage on mount
  useEffect(() => {
    const loadAuthState = async () => {
      try {
        if (typeof window === 'undefined') {
          setState(prev => ({ ...prev, isLoading: false }));
          return;
        }

        const token = localStorage.getItem(TOKEN_KEY);
        const userJson = localStorage.getItem(USER_KEY);

        if (token && userJson) {
          const user: UserResponse = JSON.parse(userJson);

          // Verify token is still valid
          try {
            await authAPI.getCurrentUser(token);
            setState({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
            });
          } catch (error) {
            // Token is invalid, clear storage
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
            setState({
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
            });
          }
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (error) {
        console.error('Error loading auth state:', error);
        setState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    };

    loadAuthState();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await authAPI.login({ email, password });

      // Store auth state
      localStorage.setItem(TOKEN_KEY, response.token);
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));

      setState({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
      });

      // Redirect to chat
      router.push('/chat');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }, [router]);

  const register = useCallback(async (email: string, password: string, confirmPassword: string) => {
    if (password !== confirmPassword) {
      throw new Error('Passwords do not match');
    }

    try {
      const response = await authAPI.register({ email, password, confirmPassword });

      // Store auth state
      localStorage.setItem(TOKEN_KEY, response.token);
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));

      setState({
        user: response.user,
        token: response.token,
        isAuthenticated: true,
        isLoading: false,
      });

      // Redirect to chat
      router.push('/chat');
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }, [router]);

  const logout = useCallback(async () => {
    try {
      if (state.token) {
        await authAPI.logout(state.token);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local state regardless of API call success
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);

      setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });

      router.push('/auth/login');
    }
  }, [state.token, router]);

  const refreshAuth = useCallback(async () => {
    if (!state.token) return;

    try {
      const newToken = await authAPI.refreshToken(state.token);
      localStorage.setItem(TOKEN_KEY, newToken);

      setState(prev => ({
        ...prev,
        token: newToken,
      }));
    } catch (error) {
      console.error('Token refresh error:', error);
      // If refresh fails, logout
      await logout();
    }
  }, [state.token, logout]);

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
