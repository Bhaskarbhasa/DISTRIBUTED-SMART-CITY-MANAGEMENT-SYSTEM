import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';
import { CongestionPieChart } from '../components/charts/CongestionPieChart';
import { ThroughputChart } from '../components/charts/ThroughputChart';

export default function Analytics() {
  const pieData = [
    { name: 'Low', value: 400 }, { name: 'Medium', value: 300 },
    { name: 'High', value: 300 }, { name: 'Critical', value: 200 },
  ];
  const tpData = [{ time: '10:00', value: 100 }, { time: '10:10', value: 150 }];
  
  return (
    <Box>
      <Typography variant="h4" gutterBottom>System Analytics</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Congestion Distribution</Typography>
            <CongestionPieChart data={pieData} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">System Throughput (Events/sec)</Typography>
            <ThroughputChart data={tpData} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
