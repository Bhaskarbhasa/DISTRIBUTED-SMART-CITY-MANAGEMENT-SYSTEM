import api from './api';

export const getEnvironmentData = async () => {
  const { data } = await api.get('/api/v1/environment');
  return data;
};
