import { useEffect } from 'react';
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
