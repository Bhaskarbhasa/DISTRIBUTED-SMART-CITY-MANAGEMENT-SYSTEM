import React from 'react';
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
