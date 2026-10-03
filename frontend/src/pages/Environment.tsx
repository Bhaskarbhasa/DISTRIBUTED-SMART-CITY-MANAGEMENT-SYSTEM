import React from 'react';
import { Box, Typography, Grid, Paper } from '@mui/material';
import { EnvironmentGauge } from '../components/charts/EnvironmentGauge';

export default function Environment() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Environment Monitoring</Typography>
      <Grid container spacing={3}>
        {[1, 2, 3].map((zone) => (
          <Grid item xs={12} md={4} key={zone}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography variant="h6">Zone {zone}</Typography>
              <EnvironmentGauge value={zone * 45} max={500} label="AQI" />
              <Typography variant="h3">{22 + zone}°C</Typography>
              <Typography variant="body2" color="textSecondary">Humidity: {50 + zone}%</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
