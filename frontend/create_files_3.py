import os

base_dir = r"d:\Distributed_system\Smart_DS_Project\distributed-smart-city\frontend\src"

files = {
    "components/layout/Sidebar.tsx": """import React from 'react';
import { List, ListItem, ListItemIcon, ListItemText, Drawer, Box } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import TrafficIcon from '@mui/icons-material/Traffic';
import ParkIcon from '@mui/icons-material/Park';
import WarningIcon from '@mui/icons-material/Warning';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import BarChartIcon from '@mui/icons-material/BarChart';
import DeviceHubIcon from '@mui/icons-material/DeviceHub';
import AssignmentIcon from '@mui/icons-material/Assignment';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Traffic', icon: <TrafficIcon />, path: '/traffic' },
  { text: 'Environment', icon: <ParkIcon />, path: '/environment' },
  { text: 'Emergency', icon: <WarningIcon />, path: '/emergency' },
  { text: 'Fog Nodes', icon: <AccountTreeIcon />, path: '/nodes' },
  { text: 'Analytics', icon: <BarChartIcon />, path: '/analytics' },
  { text: 'Devices', icon: <DeviceHubIcon />, path: '/devices' },
  { text: 'Audit Logs', icon: <AssignmentIcon />, path: '/audit' },
  { text: 'System Health', icon: <MonitorHeartIcon />, path: '/health' },
  { text: 'Admin Config', icon: <AdminPanelSettingsIcon />, path: '/admin' },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  return (
    <Drawer variant="permanent" sx={{ width: drawerWidth, flexShrink: 0, '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' } }}>
      <Box sx={{ height: 64 }} />
      <List>
        {menuItems.map((item) => (
          <ListItem button key={item.text} component={Link} to={item.path} selected={location.pathname === item.path}>
            <ListItemIcon sx={{ color: location.pathname === item.path ? 'primary.main' : 'inherit' }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} sx={{ color: location.pathname === item.path ? 'primary.main' : 'inherit' }} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};
""",
    "components/layout/StatusBar.tsx": """import React from 'react';
import { Box, Typography, Chip } from '@mui/material';

export const StatusBar: React.FC = () => {
  return (
    <Box sx={{ position: 'fixed', bottom: 0, left: 240, right: 0, height: 32, bgcolor: 'background.paper', borderTop: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', px: 2, gap: 2, zIndex: 1100 }}>
      <Typography variant="caption">Raft Leader: <Chip label="fog-1 (Term 3)" size="small" color="primary" sx={{ height: 20 }} /></Typography>
      <Typography variant="caption">Kafka: <Chip label="Connected" size="small" color="success" sx={{ height: 20 }} /></Typography>
      <Typography variant="caption">Active Alerts: <Chip label="2" size="small" color="error" sx={{ height: 20 }} /></Typography>
    </Box>
  );
};
""",
    "components/layout/AppLayout.tsx": """import React from 'react';
import { Box, AppBar, Toolbar, Typography, CssBaseline, IconButton, Avatar } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import { Sidebar } from './Sidebar';
import { StatusBar } from './StatusBar';
import { Outlet } from 'react-router-dom';

export const AppLayout: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Smart City OS
          </Typography>
          <IconButton color="inherit">
            <NotificationsIcon />
          </IconButton>
          <Avatar sx={{ ml: 2, bgcolor: 'secondary.main' }}>A</Avatar>
        </Toolbar>
      </AppBar>
      <Sidebar />
      <Box component="main" sx={{ flexGrow: 1, p: 3, pb: 6, mt: 8 }}>
        <Outlet />
      </Box>
      <StatusBar />
    </Box>
  );
};
""",
    "pages/Traffic.tsx": """import React from 'react';
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
""",
    "pages/Emergency.tsx": """import React from 'react';
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
""",
    "pages/Environment.tsx": """import React from 'react';
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
""",
    "pages/FogNodes.tsx": """import React from 'react';
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
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace('/', '\\'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding='utf-8') as f:
        f.write(content)

print("Created Layout and pages (part 1).")
