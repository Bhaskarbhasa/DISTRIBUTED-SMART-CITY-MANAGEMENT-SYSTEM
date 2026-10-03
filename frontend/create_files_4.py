import os

base_dir = r"d:\Distributed_system\Smart_DS_Project\distributed-smart-city\frontend\src"

files = {
    "pages/Analytics.tsx": """import React from 'react';
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
""",
    "pages/Devices.tsx": """import React from 'react';
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
""",
    "pages/AuditLogs.tsx": """import React from 'react';
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
""",
    "pages/SystemHealth.tsx": """import React from 'react';
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
""",
    "pages/AdminConfig.tsx": """import React from 'react';
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
""",
    "App.tsx": """import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { AppLayout } from './components/layout/AppLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Traffic from './pages/Traffic';
import Emergency from './pages/Emergency';
import Environment from './pages/Environment';
import FogNodes from './pages/FogNodes';
import Analytics from './pages/Analytics';
import Devices from './pages/Devices';
import AuditLogs from './pages/AuditLogs';
import SystemHealth from './pages/SystemHealth';
import AdminConfig from './pages/AdminConfig';

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
        
        {/* Protected Routes */}
        <Route element={isAuthenticated ? <AppLayout /> : <Navigate to="/login" />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/traffic" element={<Traffic />} />
          <Route path="/emergency" element={<Emergency />} />
          <Route path="/environment" element={<Environment />} />
          <Route path="/nodes" element={<FogNodes />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/devices" element={<Devices />} />
          <Route path="/audit" element={<AuditLogs />} />
          <Route path="/health" element={<SystemHealth />} />
          <Route path="/admin" element={<AdminConfig />} />
        </Route>

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace('/', '\\'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding='utf-8') as f:
        f.write(content)

print("Created Layout and pages (part 2).")
