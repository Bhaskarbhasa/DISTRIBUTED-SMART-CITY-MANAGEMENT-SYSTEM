import { create } from 'zustand'
import { FogNode } from '../types'

interface NodeStore {
  nodes: Record<string, FogNode>
  updateNode: (node: FogNode) => void
  setNodes: (nodes: FogNode[]) => void
}

export const useNodeStore = create<NodeStore>((set) => ({
  nodes: {},
  updateNode: (node) => set((state) => ({ nodes: { ...state.nodes, [node.node_id]: node } })),
  setNodes: (nodes) => set({ nodes: Object.fromEntries(nodes.map(n => [n.node_id, n])) }),
}))
