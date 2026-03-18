import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id?: string;
  name?: string;
  email?: string;
  avatar?: string;
  [key: string]: any;
}

interface UserState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isPremium: boolean;
  setAuth: (user: User, token: string) => void;
  updateUser: (user: User) => void;
  setIsPremium: (isPremium: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isPremium: false,
      setAuth: (user, token) => {
        localStorage.setItem('token', token);
        set({ user, token, isAuthenticated: true });
      },
      updateUser: (user) => set((state) => ({ 
        user: { ...state.user, ...user } 
      })),
      setIsPremium: (isPremium) => set({ isPremium }),
      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false, isPremium: false });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
