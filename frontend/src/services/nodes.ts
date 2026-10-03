import api from './api';
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
