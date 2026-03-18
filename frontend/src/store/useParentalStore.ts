import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ParentalState {
  pin: string;
  screenTimeLimit: number; // in minutes
  timeUsedToday: number; // in seconds
  lastResetDate: string; // ISO date string
  notificationsEnabled: boolean;
  weeklyReportEnabled: boolean;
  setPin: (pin: string) => void;
  setScreenTimeLimit: (limit: number) => void;
  setTimeUsedToday: (time: number) => void;
  addTimeUsed: (seconds: number) => void;
  resetTimeUsed: () => void;
  setNotificationsEnabled: (enabled: boolean) => void;
  setWeeklyReportEnabled: (enabled: boolean) => void;
}

export const useParentalStore = create<ParentalState>()(
  persist(
    (set) => ({
      pin: '1234',
      screenTimeLimit: 60,
      timeUsedToday: 0,
      lastResetDate: new Date().toISOString().split('T')[0],
      notificationsEnabled: true,
      weeklyReportEnabled: true,
      setPin: (pin) => set({ pin }),
      setScreenTimeLimit: (screenTimeLimit) => set({ screenTimeLimit }),
      setTimeUsedToday: (timeUsedToday) => set({ timeUsedToday }),
      addTimeUsed: (seconds) => set((state) => ({ timeUsedToday: state.timeUsedToday + seconds })),
      resetTimeUsed: () => set({ timeUsedToday: 0, lastResetDate: new Date().toISOString().split('T')[0] }),
      setNotificationsEnabled: (notificationsEnabled) => set({ notificationsEnabled }),
      setWeeklyReportEnabled: (weeklyReportEnabled) => set({ weeklyReportEnabled }),
    }),
    {
      name: 'parental-storage',
    }
  )
);
