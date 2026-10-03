import React from 'react';
import { Box, Typography, Grid, Paper, Button } from '@mui/material';
import { useAuthStore } from '../store/authStore';

const Dashboard: React.FC = () => {
  const logout = useAuthStore((state) => state.logout);

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3} alignItems="center">
        <Grid item xs={10}>
          <Typography variant="h4" gutterBottom>
            Smart City Dashboard
          </Typography>
        </Grid>
        <Grid item xs={2} textAlign="right">
          <Button variant="outlined" color="error" onClick={logout}>Logout</Button>
        </Grid>

        {/* Dashboard Content */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6">Active Alerts</Typography>
            <Typography variant="h3" color="error.main">12</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6">Online Sensors</Typography>
            <Typography variant="h3" color="primary.main">1,024</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6">Fog Nodes</Typography>
            <Typography variant="h3" color="success.main">5 / 5</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
