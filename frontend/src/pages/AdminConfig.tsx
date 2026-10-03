import React from 'react';
import { Box, Typography, Paper, TextField, Button, Grid } from '@mui/material';

export default function AdminConfig() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Admin Configuration</Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Traffic Thresholds</Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}><TextField fullWidth label="LOW Threshold" defaultValue="50" /></Grid>
          <Grid item xs={12} md={4}><TextField fullWidth label="MEDIUM Threshold" defaultValue="150" /></Grid>
          <Grid item xs={12} md={4}><TextField fullWidth label="HIGH Threshold" defaultValue="300" /></Grid>
        </Grid>
        <Box mt={3}>
          <Button variant="contained" color="primary">Save Configuration</Button>
        </Box>
      </Paper>
    </Box>
  );
}
