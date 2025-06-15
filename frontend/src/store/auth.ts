'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
}

// Function to set the auth token cookie
const setAuthCookie = (token: string | null) => {
  if (token) {
    // Set cookie with security flags
    document.cookie = `auth-token=${token}; path=/; secure; samesite=strict`;
  } else {
    // Remove cookie
    document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; secure; samesite=strict';
  }
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      login: (user: User, token: string) => {
        setAuthCookie(token);
        set({ user, isAuthenticated: true });
      },
      logout: () => {
        setAuthCookie(null);
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
      // Only persist user data in localStorage, not the token
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
); 