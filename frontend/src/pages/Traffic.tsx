import React from 'react';
import { Box, Typography, Grid, Paper, Button } from '@mui/material';
import { TrafficSignal } from '../components/common/TrafficSignal';
import { CongestionBadge } from '../components/common/CongestionBadge';
import { TrafficChart } from '../components/charts/TrafficChart';

export default function Traffic() {
  const dummyChartData = [
    { timestamp: '10:00', zone_1: 400, zone_2: 240 },
    { timestamp: '10:05', zone_1: 300, zone_2: 139 },
    { timestamp: '10:10', zone_1: 200, zone_2: 980 },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Traffic Management</Typography>
      <Grid container spacing={3}>
        {[1, 2].map((zone) => (
          <Grid item xs={12} md={6} key={zone}>
            <Paper sx={{ p: 2, display: 'flex', gap: 2 }}>
              <TrafficSignal signal={zone === 1 ? 'GREEN' : 'RED'} />
              <Box flex={1}>
                <Typography variant="h6">Downtown Zone {zone}</Typography>
                <Typography variant="body2">Vehicles: {zone * 150}</Typography>
                <Typography variant="body2">Speed: {zone === 1 ? 45 : 15} km/h</Typography>
                <Box mt={1}><CongestionBadge level={zone === 1 ? 'LOW' : 'HIGH'} /></Box>
              </Box>
            </Paper>
          </Grid>
        ))}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Traffic Volume (Last 30m)</Typography>
            <TrafficChart data={dummyChartData} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
