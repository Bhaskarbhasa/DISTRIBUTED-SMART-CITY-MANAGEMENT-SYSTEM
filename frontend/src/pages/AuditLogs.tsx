import React from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableHead, TableRow, Chip } from '@mui/material';

export default function AuditLogs() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Audit Logs</Typography>
      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Actor</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>Result</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell>{new Date().toISOString()}</TableCell>
              <TableCell>admin@smartcity.local</TableCell>
              <TableCell>UPDATE_SIGNAL</TableCell>
              <TableCell>zone-1</TableCell>
              <TableCell><Chip label="SUCCESS" color="success" size="small" /></TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
