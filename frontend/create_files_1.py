import os

base_dir = r"d:\Distributed_system\Smart_DS_Project\distributed-smart-city\frontend\src"

files = {
    "store/trafficStore.ts": """import { create } from 'zustand'
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
""",
    "store/emergencyStore.ts": """import { create } from 'zustand'
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
""",
    "store/environmentStore.ts": """import { create } from 'zustand'
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
""",
    "store/nodeStore.ts": """import { create } from 'zustand'
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
""",
    "store/notificationStore.ts": """import { create } from 'zustand'

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
""",
    "services/auth.ts": """import api from './api'
import { User } from '../types'

export const authService = {
  login: async (email: string, password: string) => {
    const res = await api.post('/api/auth/login', { email, password })
    return res.data // { access_token, user }
  },
  logout: async () => api.post('/api/auth/logout'),
  me: async (): Promise<User> => {
    const res = await api.get('/api/auth/me')
    return res.data
  },
  getUsers: async () => {
    const res = await api.get('/api/auth/users')
    return res.data
  }
}
""",
    "services/environment.ts": """import api from './api';

export const getEnvironmentData = async () => {
  const { data } = await api.get('/api/v1/environment');
  return data;
};
""",
    "services/analytics.ts": """import api from './api';

export const getTrafficTrends = async () => {
  const { data } = await api.get('/api/v1/analytics/traffic-trends');
  return data;
};
export const getCongestionDistribution = async () => {
  const { data } = await api.get('/api/v1/analytics/congestion');
  return data;
};
export const getSystemThroughput = async () => {
  const { data } = await api.get('/api/v1/analytics/throughput');
  return data;
};
""",
    "services/nodes.ts": """import api from './api';
import { FogNode } from '../types';

export const getNodes = async (): Promise<FogNode[]> => {
  const { data } = await api.get('/api/v1/nodes');
  return data;
};
export const stopNode = async (nodeId: string) => {
  const { data } = await api.post(`/api/v1/nodes/${nodeId}/stop`);
  return data;
};
export const restartNode = async (nodeId: string) => {
  const { data } = await api.post(`/api/v1/nodes/${nodeId}/restart`);
  return data;
};
""",
    "hooks/useWebSocket.ts": """import { useEffect, useRef, useState, useCallback } from 'react'

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export const useWebSocket = (url: string, onMessage: (data: any) => void) => {
  const ws = useRef<WebSocket | null>(null)
  const [status, setStatus] = useState<ConnectionStatus>('disconnected')
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout>>()
  const reconnectDelay = useRef(1000)

  const connect = useCallback(() => {
    setStatus('connecting')
    ws.current = new WebSocket(url)
    
    ws.current.onopen = () => {
      setStatus('connected')
      reconnectDelay.current = 1000
    }
    
    ws.current.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        onMessage(data)
      } catch {}
    }
    
    ws.current.onclose = () => {
      setStatus('disconnected')
      reconnectTimeout.current = setTimeout(() => {
        reconnectDelay.current = Math.min(reconnectDelay.current * 2, 30000)
        connect()
      }, reconnectDelay.current)
    }
    
    ws.current.onerror = () => setStatus('error')
  }, [url, onMessage])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimeout.current)
      ws.current?.close()
    }
  }, [connect])

  return { status }
}
""",
    "hooks/useTrafficWebSocket.ts": """import { useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { useTrafficStore } from '../store/trafficStore';

export const useTrafficWebSocket = () => {
  const updateZone = useTrafficStore(state => state.updateZone);
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
  
  const { status } = useWebSocket(`${wsUrl}/ws/traffic`, (data) => {
    if (data && data.zone_id) {
      updateZone(data);
    }
  });

  return { status };
};
""",
    "hooks/useEmergencyWebSocket.ts": """import { useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { useEmergencyStore } from '../store/emergencyStore';

export const useEmergencyWebSocket = () => {
  const updateAlert = useEmergencyStore(state => state.updateAlert);
  const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
  
  const { status } = useWebSocket(`${wsUrl}/ws/emergency`, (data) => {
    if (data && data.alert_id) {
      updateAlert(data);
    }
  });

  return { status };
};
""",
    "hooks/useNodeStatus.ts": """import { useEffect } from 'react';
import { useNodeStore } from '../store/nodeStore';
import { getNodes } from '../services/nodes';

export const useNodeStatus = () => {
  const setNodes = useNodeStore(state => state.setNodes);

  useEffect(() => {
    const fetchNodes = async () => {
      try {
        const nodes = await getNodes();
        setNodes(nodes);
      } catch (e) {
        console.error('Failed to fetch nodes', e);
      }
    };
    fetchNodes();
    const interval = setInterval(fetchNodes, 3000);
    return () => clearInterval(interval);
  }, [setNodes]);
};
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace('/', '\\'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding='utf-8') as f:
        f.write(content)

print("Created stores, services, and hooks.")
