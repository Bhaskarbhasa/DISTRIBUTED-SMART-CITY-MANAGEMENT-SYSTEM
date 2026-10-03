import { create } from 'zustand'
import { EmergencyAlert } from '../types'

interface EmergencyStore {
  alerts: Record<string, EmergencyAlert>
  updateAlert: (alert: EmergencyAlert) => void
  setAlerts: (alerts: EmergencyAlert[]) => void
}

export const useEmergencyStore = create<EmergencyStore>((set) => ({
  alerts: {},
  updateAlert: (alert) => set((state) => ({ alerts: { ...state.alerts, [alert.alert_id]: alert } })),
  setAlerts: (alerts) => set({ alerts: Object.fromEntries(alerts.map(a => [a.alert_id, a])) }),
}))
