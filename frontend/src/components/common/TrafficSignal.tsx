import React from 'react';
import { Box } from '@mui/material';

type SignalState = 'GREEN' | 'YELLOW' | 'RED';

export const TrafficSignal: React.FC<{ signal: SignalState, animated?: boolean }> = ({ signal, animated = true }) => {
  const getGlow = (color: string) => animated ? `0 0 10px ${color}` : 'none';

  return (
    <Box sx={{ 
      display: 'inline-flex', flexDirection: 'column', bgcolor: '#333', 
      p: 1, borderRadius: 2, gap: 1 
    }}>
      <Box sx={{ 
        width: 20, height: 20, borderRadius: '50%', 
        bgcolor: signal === 'RED' ? '#ff0000' : '#440000',
        boxShadow: signal === 'RED' ? getGlow('#ff0000') : 'none'
      }} />
      <Box sx={{ 
        width: 20, height: 20, borderRadius: '50%', 
        bgcolor: signal === 'YELLOW' ? '#ffff00' : '#444400',
        boxShadow: signal === 'YELLOW' ? getGlow('#ffff00') : 'none'
      }} />
      <Box sx={{ 
        width: 20, height: 20, borderRadius: '50%', 
        bgcolor: signal === 'GREEN' ? '#00ff00' : '#004400',
        boxShadow: signal === 'GREEN' ? getGlow('#00ff00') : 'none'
      }} />
    </Box>
  );
};
