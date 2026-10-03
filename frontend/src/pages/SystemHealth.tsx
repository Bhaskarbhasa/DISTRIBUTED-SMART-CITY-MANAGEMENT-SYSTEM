import React from 'react';
import { Box, Typography, Grid, Paper, Chip } from '@mui/material';

export default function SystemHealth() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>System Health</Typography>
      <Grid container spacing={2}>
        {['API Gateway', 'Traffic Service', 'Emergency Service', 'Auth Service', 'PostgreSQL', 'Kafka Cluster', 'Redis'].map(service => (
          <Grid item xs={12} sm={6} md={3} key={service}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1">{service}</Typography>
              <Box mt={1} display="flex" justifyContent="space-between">
                <Chip label="UP" color="success" size="small" />
                <Typography variant="caption">12ms</Typography>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
