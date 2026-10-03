import React from 'react';
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
