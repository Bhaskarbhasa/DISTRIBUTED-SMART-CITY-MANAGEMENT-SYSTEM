import api from './api';

export const getTrafficZones = async () => {
  const { data } = await api.get('/api/v1/traffic/zones');
  return data;
};

export const updateTrafficZoneMode = async (zoneId: string, mode: string) => {
  const { data } = await api.post(`/api/v1/traffic/zones/${zoneId}/mode`, { mode });
  return data;
};
