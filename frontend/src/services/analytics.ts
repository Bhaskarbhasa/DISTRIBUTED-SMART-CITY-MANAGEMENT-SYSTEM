import api from './api';

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
