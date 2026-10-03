import { create } from 'zustand'
import { EnvironmentData } from '../types'

interface EnvironmentStore {
  data: Record<string, EnvironmentData>
  updateData: (data: EnvironmentData) => void
  setData: (data: EnvironmentData[]) => void
}

export const useEnvironmentStore = create<EnvironmentStore>((set) => ({
  data: {},
  updateData: (d) => set((state) => ({ data: { ...state.data, [d.zone_id]: d } })),
  setData: (data) => set({ data: Object.fromEntries(data.map(d => [d.zone_id, d])) }),
}))
