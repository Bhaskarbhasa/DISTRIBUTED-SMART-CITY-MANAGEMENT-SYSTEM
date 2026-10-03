import React from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, Button } from '@mui/material';

export default function Devices() {
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" mb={2}>
        <Typography variant="h4">Device Management</Typography>
        <Button variant="contained" color="primary">Register Device</Button>
      </Box>
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Zone</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell>cam-01</TableCell>
              <TableCell>CAMERA</TableCell>
              <TableCell>zone-1</TableCell>
              <TableCell>ONLINE</TableCell>
              <TableCell><Button size="small" color="error">Deregister</Button></TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
