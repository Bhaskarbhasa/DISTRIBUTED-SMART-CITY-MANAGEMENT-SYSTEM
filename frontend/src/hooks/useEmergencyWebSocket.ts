import { useEffect } from 'react';
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
