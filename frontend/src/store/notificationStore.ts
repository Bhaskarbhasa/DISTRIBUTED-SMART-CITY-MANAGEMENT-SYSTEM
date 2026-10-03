import { create } from 'zustand'

export interface Notification {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
}

interface NotificationStore {
  notifications: Notification[]
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [],
  addNotification: (n) => set((state) => ({ 
    notifications: [{ ...n, id: Math.random().toString(), timestamp: new Date().toISOString() }, ...state.notifications].slice(0, 50) 
  })),
}))
