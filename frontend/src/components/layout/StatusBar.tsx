import React from 'react';
import { Box, Typography, Chip } from '@mui/material';

export const StatusBar: React.FC = () => {
  return (
    <Box sx={{ position: 'fixed', bottom: 0, left: 240, right: 0, height: 32, bgcolor: 'background.paper', borderTop: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', px: 2, gap: 2, zIndex: 1100 }}>
      <Typography variant="caption">Raft Leader: <Chip label="fog-1 (Term 3)" size="small" color="primary" sx={{ height: 20 }} /></Typography>
      <Typography variant="caption">Kafka: <Chip label="Connected" size="small" color="success" sx={{ height: 20 }} /></Typography>
      <Typography variant="caption">Active Alerts: <Chip label="2" size="small" color="error" sx={{ height: 20 }} /></Typography>
    </Box>
  );
};
