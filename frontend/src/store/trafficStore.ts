import { create } from 'zustand'
import { TrafficZone } from '../types'

interface TrafficStore {
  zones: Record<string, TrafficZone>
  updateZone: (zone: TrafficZone) => void
  setZones: (zones: TrafficZone[]) => void
}

export const useTrafficStore = create<TrafficStore>((set) => ({
  zones: {},
  updateZone: (zone) => set((state) => ({ zones: { ...state.zones, [zone.zone_id]: zone } })),
  setZones: (zones) => set({ zones: Object.fromEntries(zones.map(z => [z.zone_id, z])) }),
}))
