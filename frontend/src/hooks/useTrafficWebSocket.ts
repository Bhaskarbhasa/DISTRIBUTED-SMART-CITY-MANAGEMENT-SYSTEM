import { useEffect } from 'react';
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
