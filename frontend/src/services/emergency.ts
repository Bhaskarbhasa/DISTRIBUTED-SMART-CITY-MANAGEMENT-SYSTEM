import api from './api';

export const getAlerts = async () => {
  const { data } = await api.get('/api/v1/emergency/alerts');
  return data;
};

export const updateAlertStatus = async (alertId: string, status: string) => {
  const { data } = await api.patch(`/api/v1/emergency/alerts/${alertId}/status`, { status });
  return data;
};
