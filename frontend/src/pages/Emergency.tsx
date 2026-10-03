import React from 'react';
import { Box, Typography, Card, CardContent, Button } from '@mui/material';
import { SeverityBadge } from '../components/common/SeverityBadge';

export default function Emergency() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Emergency Alerts</Typography>
      <Card sx={{ borderLeft: '4px solid #f44336', mb: 2 }}>
        <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h6">Vehicle Accident - Main St</Typography>
            <Typography variant="body2" color="textSecondary">Zone 1 • 2 mins ago</Typography>
            <Box mt={1}><SeverityBadge severity="CRITICAL" /></Box>
          </Box>
          <Box>
            <Button variant="contained" color="primary" sx={{ mr: 1 }}>Acknowledge</Button>
            <Button variant="outlined" color="success">Resolve</Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
