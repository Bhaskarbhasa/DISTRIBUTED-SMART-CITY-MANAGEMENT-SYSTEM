import React, { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Button, TextField, Box, Typography, Container, Paper } from '@mui/material';

const Login: React.FC = () => {
  const login = useAuthStore((state) => state.login);
  const [email, setEmail] = useState('admin@smartcity.local');
  const [password, setPassword] = useState('admin');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    login('dummy-jwt-token');
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Paper elevation={3} sx={{ padding: 4, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Typography component="h1" variant="h5">Smart City Login</Typography>
          <Box component="form" onSubmit={handleLogin} sx={{ mt: 1 }}>
            <TextField margin="normal" required fullWidth label="Email Address" autoFocus value={email} onChange={e => setEmail(e.target.value)} />
            <TextField margin="normal" required fullWidth label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
            <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>Sign In</Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
