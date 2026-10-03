import React from 'react';
import { Box, Typography, Grid, Paper, Button, LinearProgress } from '@mui/material';
import { NodeStateBadge } from '../components/common/NodeStateBadge';

export default function FogNodes() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Raft Consensus Cluster</Typography>
      <Grid container spacing={3}>
        {['fog-1', 'fog-2', 'fog-3'].map((node, i) => (
          <Grid item xs={12} md={4} key={node}>
            <Paper sx={{ p: 2 }}>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography variant="h5">{node}</Typography>
                <NodeStateBadge state={i === 0 ? 'LEADER' : 'FOLLOWER'} />
              </Box>
              <Typography variant="body2">Term: 3</Typography>
              <Typography variant="body2">Commit Index: 1402</Typography>
              <Box mt={2}>
                <Typography variant="caption">CPU Usage</Typography>
                <LinearProgress variant="determinate" value={30 + i * 10} />
              </Box>
              <Box mt={3} display="flex" gap={1}>
                <Button size="small" variant="contained" color="error">Stop</Button>
                <Button size="small" variant="outlined" color="success">Restart</Button>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
